"""Leitura dos modelos de compatibilidade a partir do banco SQLite."""

import sqlite3

from optimus_lib import mppt_index_dec

from .models import EquipmentSummary, InverterData, ModuleData, MPPTData


def _list_equipment(connection, table, active_only):
    connection.row_factory = sqlite3.Row
    power_column = "RATED_ACTIVE_POWER" if table == "inverter" else "WP"
    overload_column = "equipment.OVERLOAD" if table == "inverter" else "NULL"
    rows = connection.execute(
        f"SELECT equipment.ID, manufacturer.NAME AS MANUFACTURER, equipment.MODEL, "
        f"equipment.{power_column} AS NOMINAL_POWER, "
        f"{overload_column} AS OVERLOAD_PERCENT, equipment.ACTIVE "
        f"FROM {table} AS equipment "
        "JOIN manufacturer ON manufacturer.ID = equipment.MANUFACTURER_ID "
        + ("WHERE equipment.ACTIVE = 1 " if active_only else "")
        + "ORDER BY manufacturer.NAME COLLATE NOCASE, equipment.MODEL COLLATE NOCASE, equipment.ID"
    ).fetchall()
    return tuple(
        EquipmentSummary(
            row["ID"],
            row["MANUFACTURER"],
            row["MODEL"],
            row["NOMINAL_POWER"],
            row["OVERLOAD_PERCENT"],
            bool(row["ACTIVE"]),
        )
        for row in rows
    )


def list_active_inverters(connection):
    return _list_equipment(connection, "inverter", active_only=True)


def list_active_modules(connection):
    return _list_equipment(connection, "module", active_only=True)


def list_inverters(connection):
    """Lista todos os inversores, inclusive os inativos."""
    return _list_equipment(connection, "inverter", active_only=False)


def list_modules(connection):
    """Lista todos os módulos, inclusive os inativos."""
    return _list_equipment(connection, "module", active_only=False)


def _mppt_count(index, tracker_count):
    if index == 0:
        return tracker_count
    return len(mppt_index_dec(index))


def load_inverter(connection, inverter_id):
    connection.row_factory = sqlite3.Row
    row = connection.execute("SELECT * FROM inverter WHERE ID = ?", (inverter_id,)).fetchone()
    if row is None:
        raise LookupError(f"Inversor {inverter_id} não encontrado")
    mppt_rows = connection.execute(
        "SELECT * FROM mppt WHERE INVERTER_ID = ? ORDER BY ID", (inverter_id,)
    ).fetchall()
    mppts = tuple(
        MPPTData(
            index=item["MPPT_INDEX"],
            number_of_inputs=item["NUMBER_OF_INPUTS"],
            max_input_voltage=item["MAX_INPUT_VOLTAGE"],
            min_startup_voltage=item["MIN_STARTUP_VOLTAGE"],
            max_operating_voltage=item["MAX_OPERATING_VOLTAGE"],
            min_operating_voltage=item["MIN_OPERATING_VOLTAGE"],
            min_full_load_voltage=item["MIN_FULL_LOAD_VOLTAGE"],
            max_full_load_voltage=item["MAX_FULL_LOAD_VOLTAGE"],
            max_short_circuit_current=item["MAX_SHORT_CIRCUIT_CURRENT"],
            max_operating_current=item["MAX_OPERATING_CURRENT"],
            count=_mppt_count(item["MPPT_INDEX"], row["NUMBER_OF_TRACKERS"]),
        )
        for item in mppt_rows
    )
    return InverterData(
        database_id=row["ID"],
        model=row["MODEL"],
        rated_active_power_w=row["RATED_ACTIVE_POWER"],
        overload_percent=row["OVERLOAD"],
        mppts=mppts,
    )


def load_module(connection, module_id):
    connection.row_factory = sqlite3.Row
    row = connection.execute("SELECT * FROM module WHERE ID = ?", (module_id,)).fetchone()
    if row is None:
        raise LookupError(f"Módulo {module_id} não encontrado")
    return ModuleData(
        database_id=row["ID"],
        model=row["MODEL"],
        nominal_power_w=row["WP"],
        vmpp_v=row["VMPP"],
        impp_a=row["IMPP"],
        voc_v=row["VOC"],
        isc_a=row["ISC"],
        coef_voc_percent_c=row["COEF_VOC"],
        coef_isc_percent_c=row["COEF_ISC"],
    )
