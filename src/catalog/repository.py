"""Persistência transacional e consultas dos cadastros."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager

from .domain import CatalogValidationError, encode_mppt_index, validate_inverter_draft


class CatalogRepository:
    def __init__(self, database):
        self.database = str(database)

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def list_manufacturers(self, search="", category=None):
        term = search.strip()
        sql, values = "SELECT * FROM manufacturer WHERE (NAME LIKE ?", [f"%{term}%"]
        if term.isdigit():
            sql += " OR ID = ?"; values.append(int(term))
        sql += ")"
        if category not in (None, ""):
            sql += " AND CATEGORY = ?"; values.append(int(category))
        sql += " ORDER BY NAME COLLATE NOCASE, ID"
        with self.connect() as connection:
            return [dict(row) for row in connection.execute(sql, values)]

    def list_equipment(self, table, search="", manufacturer_id=None, active=None,
                       order="MODEL", descending=False):
        if table not in ("inverter", "module"):
            raise ValueError("Tabela de equipamento inválida.")
        columns = {"ID", "MODEL", "MANUFACTURER_NAME", "ACTIVE",
                   "RATED_ACTIVE_POWER" if table == "inverter" else "WP"}
        if order not in columns:
            order = "MODEL"
        expression = "m.NAME" if order == "MANUFACTURER_NAME" else f"e.{order}"
        term = search.strip()
        sql = (f"SELECT e.*, m.NAME MANUFACTURER_NAME FROM {table} e "
               "JOIN manufacturer m ON m.ID=e.MANUFACTURER_ID "
               "WHERE (e.MODEL LIKE ? OR m.NAME LIKE ?")
        values = [f"%{term}%"] * 2
        if term.isdigit():
            sql += " OR e.ID=?"; values.append(int(term))
        sql += ")"
        if manufacturer_id not in (None, ""):
            sql += " AND e.MANUFACTURER_ID=?"; values.append(int(manufacturer_id))
        if active not in (None, ""):
            sql += " AND e.ACTIVE=?"; values.append(int(active))
        sql += f" ORDER BY {expression} COLLATE NOCASE {'DESC' if descending else 'ASC'}, e.ID"
        with self.connect() as connection:
            return [dict(row) for row in connection.execute(sql, values)]

    def manufacturer_choices(self, equipment):
        categories = (0, 2) if equipment == "inverter" else (1, 2)
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM manufacturer WHERE CATEGORY IN (?,?) ORDER BY NAME COLLATE NOCASE", categories)
            return [dict(row) for row in rows]

    def load_inverter_draft(self, inverter_id):
        with self.connect() as connection:
            parent = connection.execute("SELECT * FROM inverter WHERE ID=?", (inverter_id,)).fetchone()
            if parent is None:
                raise LookupError("Inversor não encontrado.")
            result = {"inverter": dict(parent)}
            result["mppts"] = [dict(row) for row in connection.execute(
                "SELECT * FROM mppt WHERE INVERTER_ID=? ORDER BY ID", (inverter_id,))]
            for key, table, column in (
                ("systems", "inverter_system", "SYSTEM_TYPE"),
                ("communications", "inverter_communication", "COMMUNICATION_TYPE"),
                ("output_modes", "inverter_output_mode", "OUTPUT_MODE"),
            ):
                result[key] = [row[0] for row in connection.execute(
                    f"SELECT {column} FROM {table} WHERE INVERTER_ID=? ORDER BY ID", (inverter_id,))]
            return result

    def save_inverter(self, draft, inverter_id=None, *, fail_after_child=False):
        validate_inverter_draft(draft)
        parent = dict(draft["inverter"])
        parent.pop("ID", None); parent.pop("MANUFACTURER_NAME", None)
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            self._validate_manufacturer(connection, parent["MANUFACTURER_ID"], (0, 2))
            if inverter_id is None:
                columns = tuple(parent)
                cursor = connection.execute(
                    f"INSERT INTO inverter ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                    tuple(parent[column] for column in columns))
                inverter_id = cursor.lastrowid
            else:
                assignments = ",".join(f"{column}=?" for column in parent)
                connection.execute(f"UPDATE inverter SET {assignments} WHERE ID=?",
                                   tuple(parent.values()) + (inverter_id,))
                incoming_mppt_ids = tuple(group.get("ID") for group in draft["mppts"] if group.get("ID") is not None)
                if incoming_mppt_ids:
                    placeholders = ",".join("?" for _ in incoming_mppt_ids)
                    connection.execute(
                        f"DELETE FROM mppt WHERE INVERTER_ID=? AND ID NOT IN ({placeholders})",
                        (inverter_id,) + incoming_mppt_ids,
                    )
                else:
                    connection.execute("DELETE FROM mppt WHERE INVERTER_ID=?", (inverter_id,))
                for table in ("inverter_system", "inverter_communication", "inverter_output_mode"):
                    connection.execute(f"DELETE FROM {table} WHERE INVERTER_ID=?", (inverter_id,))
            for number, group in enumerate(draft["mppts"]):
                child = dict(group); child_id = child.pop("ID", None); child.pop("INVERTER_ID", None)
                for private_key in tuple(key for key in child if key.startswith("_")):
                    child.pop(private_key)
                if "positions" in group or "POSITIONS" in group:
                    positions = tuple(sorted(child.pop("positions", ()) or child.pop("POSITIONS", ())))
                    homogeneous = len(draft["mppts"]) == 1 and positions == tuple(
                        range(1, int(parent["NUMBER_OF_TRACKERS"]) + 1)
                    )
                    child["MPPT_INDEX"] = 0 if homogeneous else encode_mppt_index(positions)
                columns = tuple(child)
                if child_id is None:
                    connection.execute(
                        f"INSERT INTO mppt (INVERTER_ID,{','.join(columns)}) VALUES (?,{','.join('?' for _ in columns)})",
                        (inverter_id,) + tuple(child[column] for column in columns))
                else:
                    assignments = ",".join(f"{column}=?" for column in columns)
                    cursor = connection.execute(
                        f"UPDATE mppt SET {assignments} WHERE ID=? AND INVERTER_ID=?",
                        tuple(child[column] for column in columns) + (child_id, inverter_id),
                    )
                    if cursor.rowcount != 1:
                        raise CatalogValidationError((f"Grupo MPPT {child_id} não pertence ao inversor editado.",))
                if fail_after_child and number == 0:
                    raise sqlite3.IntegrityError("Falha induzida para teste")
            for key, table, column in (
                ("systems", "inverter_system", "SYSTEM_TYPE"),
                ("communications", "inverter_communication", "COMMUNICATION_TYPE"),
                ("output_modes", "inverter_output_mode", "OUTPUT_MODE"),
            ):
                connection.executemany(f"INSERT INTO {table}(INVERTER_ID,{column}) VALUES (?,?)",
                                       ((inverter_id, value) for value in draft.get(key, ())))
            return inverter_id

    def save_equipment(self, table, data, record_id=None):
        if table not in ("module", "manufacturer"):
            raise ValueError("Cadastro inválido.")
        data = dict(data); data.pop("ID", None); data.pop("MANUFACTURER_NAME", None)
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            if table == "module":
                self._validate_manufacturer(connection, data["MANUFACTURER_ID"], (1, 2))
            if record_id is None:
                columns = tuple(data)
                cursor = connection.execute(
                    f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                    tuple(data.values()))
                return cursor.lastrowid
            assignments = ",".join(f"{column}=?" for column in data)
            connection.execute(f"UPDATE {table} SET {assignments} WHERE ID=?", tuple(data.values()) + (record_id,))
            if table == "manufacturer":
                self._validate_manufacturer_category_change(connection, record_id, data.get("CATEGORY"))
            return record_id

    def delete(self, table, record_id):
        if table not in ("manufacturer", "inverter", "module"):
            raise ValueError("Cadastro inválido.")
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            if table == "manufacturer":
                counts = [connection.execute(f"SELECT COUNT(*) FROM {child} WHERE MANUFACTURER_ID=?", (record_id,)).fetchone()[0]
                          for child in ("inverter", "module")]
                if any(counts):
                    raise CatalogValidationError((f"Fabricante possui {counts[0]} inversor(es) e {counts[1]} módulo(s) vinculados.",))
            elif table == "inverter":
                # O schema real não declara CASCADE em todas as tabelas filhas
                # (notadamente inverter_communication); a exclusão explícita
                # mantém o conjunto atômico e não deixa órfãos.
                for child in ("mppt", "inverter_system", "inverter_communication", "inverter_output_mode"):
                    connection.execute(f"DELETE FROM {child} WHERE INVERTER_ID=?", (record_id,))
            connection.execute(f"DELETE FROM {table} WHERE ID=?", (record_id,))

    @staticmethod
    def _validate_manufacturer(connection, manufacturer_id, allowed):
        row = connection.execute("SELECT CATEGORY FROM manufacturer WHERE ID=?", (manufacturer_id,)).fetchone()
        if row is None or row[0] not in allowed:
            raise CatalogValidationError(("Fabricante incompatível com o tipo de equipamento.",))

    @staticmethod
    def _validate_manufacturer_category_change(connection, manufacturer_id, category):
        inverter_count = connection.execute("SELECT COUNT(*) FROM inverter WHERE MANUFACTURER_ID=?", (manufacturer_id,)).fetchone()[0]
        module_count = connection.execute("SELECT COUNT(*) FROM module WHERE MANUFACTURER_ID=?", (manufacturer_id,)).fetchone()[0]
        if (inverter_count and category not in (0, 2)) or (module_count and category not in (1, 2)):
            raise CatalogValidationError(("A nova categoria é incompatível com equipamentos já vinculados.",))
