"""Busca somente leitura de equipamentos para a interface principal."""

from __future__ import annotations

import math
import sqlite3
from contextlib import closing
from dataclasses import dataclass, field


def parse_optional_number(value, label):
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    text = str(value).strip()
    if "," in text and "." in text:
        raise ValueError(f"{label}: use ponto ou vírgula somente como separador decimal.")
    try:
        number = float(text.replace(",", "."))
    except ValueError as error:
        raise ValueError(f"{label}: valor numérico inválido.") from error
    if not math.isfinite(number):
        raise ValueError(f"{label}: NaN e infinito não são aceitos.")
    return number


def parse_range(minimum, maximum, label):
    low = parse_optional_number(minimum, f"{label} mínimo")
    high = parse_optional_number(maximum, f"{label} máximo")
    if low is not None and high is not None and low > high:
        raise ValueError(f"{label}: o mínimo não pode ser maior que o máximo.")
    return low, high


@dataclass
class SearchCriteria:
    text: str = ""
    manufacturer_ids: tuple[int, ...] = ()
    model: str = ""
    active: int | None = None
    ranges: dict[str, tuple[float | None, float | None]] = field(default_factory=dict)
    options: dict[str, tuple[str, ...]] = field(default_factory=dict)
    mppt_mode: str = "any"


class EquipmentSearchRepository:
    COMMON_COLUMNS = {
        "inverter": {"power": "e.RATED_ACTIVE_POWER", "max_power": "e.MAX_ACTIVE_POWER",
                     "ac_voltage": "e.RATED_OUTPUT_VOLTAGE", "rated_current": "e.RATED_OUTPUT_CURRENT",
                     "max_current": "e.MAX_OUTPUT_CURRENT", "trackers": "e.NUMBER_OF_TRACKERS",
                     "inputs": "e.NUMBER_OF_INPUTS"},
        "module": {"power": "e.WP", "vmpp": "e.VMPP", "voc": "e.VOC", "impp": "e.IMPP", "isc": "e.ISC"},
    }
    MPPT_COLUMNS = {
        "max_input_voltage": "p.MAX_INPUT_VOLTAGE", "min_startup_voltage": "p.MIN_STARTUP_VOLTAGE",
        "min_operating_voltage": "p.MIN_OPERATING_VOLTAGE", "max_operating_voltage": "p.MAX_OPERATING_VOLTAGE",
        "max_operating_current": "p.MAX_OPERATING_CURRENT",
        "max_short_circuit_current": "p.MAX_SHORT_CIRCUIT_CURRENT",
    }
    RELATIONS = {
        "systems": ("inverter_system", "SYSTEM_TYPE"),
        "communications": ("inverter_communication", "COMMUNICATION_TYPE"),
        "output_modes": ("inverter_output_mode", "OUTPUT_MODE"),
    }
    MODULE_OPTIONS = {"solar_cells": "SOLAR_CELLS", "cell_type": "CELL_TYPE", "surface_type": "SURFACE_TYPE"}

    def __init__(self, database):
        self.database = str(database)

    def connect(self):
        connection = sqlite3.connect(f"file:{self.database}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        return connection

    def manufacturers(self, entity):
        categories = (0, 2) if entity == "inverter" else (1, 2)
        with closing(self.connect()) as connection:
            return [dict(row) for row in connection.execute(
                "SELECT ID,NAME FROM manufacturer WHERE CATEGORY IN (?,?) ORDER BY NAME COLLATE NOCASE,ID",
                categories,
            )]

    def search(self, entity, criteria=None, order="MODEL", descending=False):
        if entity not in ("inverter", "module"):
            raise ValueError("Tipo de equipamento inválido.")
        criteria = criteria or SearchCriteria()
        power = self.COMMON_COLUMNS[entity]["power"]
        extra = ", e.RATED_OUTPUT_VOLTAGE AS AC_VOLTAGE" if entity == "inverter" else ", NULL AS AC_VOLTAGE"
        sql = (f"SELECT e.ID,m.NAME MANUFACTURER,e.MODEL,{power} NOMINAL_POWER,e.ACTIVE{extra} "
               f"FROM {entity} e JOIN manufacturer m ON m.ID=e.MANUFACTURER_ID WHERE 1=1")
        params = []
        term = criteria.text.strip()
        if term:
            sql += " AND (e.MODEL LIKE ? COLLATE NOCASE OR m.NAME LIKE ? COLLATE NOCASE"
            params.extend((f"%{term}%", f"%{term}%"))
            if term.isdigit():
                sql += " OR e.ID=?"; params.append(int(term))
            sql += ")"
        if criteria.model.strip():
            sql += " AND e.MODEL LIKE ? COLLATE NOCASE"; params.append(f"%{criteria.model.strip()}%")
        if criteria.manufacturer_ids:
            marks = ",".join("?" for _ in criteria.manufacturer_ids)
            sql += f" AND e.MANUFACTURER_ID IN ({marks})"; params.extend(criteria.manufacturer_ids)
        if criteria.active in (0, 1):
            sql += " AND e.ACTIVE=?"; params.append(criteria.active)
        mppt_ranges = {}
        for key, bounds in criteria.ranges.items():
            if key in self.MPPT_COLUMNS:
                if any(value is not None for value in bounds):
                    mppt_ranges[key] = bounds
            elif key in self.COMMON_COLUMNS[entity]:
                sql += self._range_sql(self.COMMON_COLUMNS[entity][key], bounds, params)
        if entity == "inverter":
            for key, (table, column) in self.RELATIONS.items():
                values = criteria.options.get(key, ())
                if values:
                    marks = ",".join("?" for _ in values)
                    sql += f" AND EXISTS(SELECT 1 FROM {table} r WHERE r.INVERTER_ID=e.ID AND r.{column} IN ({marks}))"
                    params.extend(values)
            if mppt_ranges:
                group_conditions = []
                group_params = []
                for key, bounds in mppt_ranges.items():
                    group_conditions.append(self._range_sql(self.MPPT_COLUMNS[key], bounds, group_params, prefix=""))
                predicate = " AND ".join(condition for condition in group_conditions if condition)
                if criteria.mppt_mode == "all":
                    sql += (" AND EXISTS(SELECT 1 FROM mppt p WHERE p.INVERTER_ID=e.ID)"
                            f" AND NOT EXISTS(SELECT 1 FROM mppt p WHERE p.INVERTER_ID=e.ID AND NOT ({predicate}))")
                else:
                    sql += f" AND EXISTS(SELECT 1 FROM mppt p WHERE p.INVERTER_ID=e.ID AND {predicate})"
                params.extend(group_params)
        else:
            for key, column in self.MODULE_OPTIONS.items():
                values = criteria.options.get(key, ())
                if values:
                    marks = ",".join("?" for _ in values)
                    sql += f" AND e.{column} IN ({marks})"; params.extend(values)
        order_map = {"ID": "e.ID", "MANUFACTURER": "m.NAME", "MODEL": "e.MODEL",
                     "NOMINAL_POWER": power, "ACTIVE": "e.ACTIVE", "AC_VOLTAGE": "e.RATED_OUTPUT_VOLTAGE"}
        expression = order_map.get(order, "e.MODEL")
        sql += f" ORDER BY {expression} {'DESC' if descending else 'ASC'}, e.ID"
        with closing(self.connect()) as connection:
            return [dict(row) for row in connection.execute(sql, params)]

    @staticmethod
    def _range_sql(column, bounds, params, prefix=" AND "):
        low, high = bounds
        parts = []
        if low is not None:
            parts.append(f"{column} IS NOT NULL AND {column} != -1 AND {column} >= ?"); params.append(low)
        if high is not None:
            parts.append(f"{column} IS NOT NULL AND {column} != -1 AND {column} <= ?"); params.append(high)
        return prefix + " AND ".join(parts) if parts else ""
