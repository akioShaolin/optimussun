import math
import sqlite3
import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
DB_PATH = SRC_DIR / "optimus_sun.db"
sys.path.insert(0, str(SRC_DIR))

from optimus_lib import (  # noqa: E402
    compensacao_termica,
    limite_strings_curto_circuito,
    limite_strings_operacao,
    limites_modulos_serie,
)
from compatibility import (  # noqa: E402
    LimitingFactor,
    compare_operating_current_modes,
    list_active_inverters,
    list_active_modules,
    list_inverters,
    list_modules,
    load_inverter,
    load_module,
)


@unittest.skipUnless(DB_PATH.exists(), "banco operacional local não disponível")
class RealDatabaseRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection = sqlite3.connect(f"file:{DB_PATH.resolve()}?mode=ro", uri=True)
        cls.connection.row_factory = sqlite3.Row

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def test_core_limits_match_legacy_formulas_for_real_equipment(self):
        modules = self.connection.execute(
            "SELECT * FROM module WHERE ACTIVE = 1 ORDER BY ID LIMIT 5"
        ).fetchall()
        mppts = self.connection.execute("SELECT * FROM mppt ORDER BY ID LIMIT 5").fetchall()

        self.assertEqual(len(modules), 5)
        self.assertEqual(len(mppts), 5)

        for module, mppt in zip(modules, mppts):
            _, voc_max = compensacao_termica(module["COEF_VOC"] / 100, 10, 50, module["VOC"])
            vmpp_min, vmpp_max = compensacao_termica(module["COEF_VOC"] / 100, 10, 50, module["VMPP"])
            _, isc_max = compensacao_termica(module["COEF_ISC"] / 100, 10, 50, module["ISC"])
            _, impp_max = compensacao_termica(module["COEF_ISC"] / 100, 10, 50, module["IMPP"])

            self.assertEqual(
                limite_strings_curto_circuito(mppt["MAX_SHORT_CIRCUIT_CURRENT"], isc_max),
                math.trunc(mppt["MAX_SHORT_CIRCUIT_CURRENT"] / isc_max),
            )
            self.assertEqual(
                limite_strings_operacao(mppt["MAX_OPERATING_CURRENT"], impp_max, 0),
                math.trunc(mppt["MAX_OPERATING_CURRENT"] / impp_max),
            )
            self.assertEqual(
                limites_modulos_serie(
                    mppt["MIN_OPERATING_VOLTAGE"], mppt["MAX_OPERATING_VOLTAGE"], vmpp_min, vmpp_max
                ),
                (
                    math.ceil(mppt["MIN_OPERATING_VOLTAGE"] / vmpp_min),
                    math.trunc(mppt["MAX_OPERATING_VOLTAGE"] / vmpp_max),
                ),
            )
            self.assertGreater(voc_max, 0)

    def test_active_selector_lists_exclude_inactive_and_preserve_order_and_ids(self):
        all_inverters = list_inverters(self.connection)
        active_inverters = list_active_inverters(self.connection)
        all_modules = list_modules(self.connection)
        active_modules = list_active_modules(self.connection)

        self.assertGreater(len(all_inverters), len(active_inverters))
        self.assertGreater(len(all_modules), len(active_modules))
        self.assertTrue(all(item.active for item in active_inverters))
        self.assertTrue(all(item.active for item in active_modules))
        self.assertTrue(any(not item.active for item in all_inverters))
        self.assertTrue(any(not item.active for item in all_modules))
        self.assertEqual(
            {item.database_id for item in active_inverters},
            {item.database_id for item in all_inverters if item.active},
        )
        self.assertEqual(
            {item.database_id for item in active_modules},
            {item.database_id for item in all_modules if item.active},
        )
        for equipment in (all_inverters, all_modules):
            self.assertEqual(
                list(equipment),
                sorted(
                    equipment,
                    key=lambda item: (
                        item.manufacturer.casefold(),
                        item.model.casefold(),
                        item.database_id,
                    ),
                ),
            )
            self.assertTrue(all(item.database_id for item in equipment))

    def test_compatibility_engine_with_real_medium_inverter(self):
        inverter = load_inverter(self.connection, 214)
        module = load_module(self.connection, 397)
        normal, ignored = compare_operating_current_modes(inverter, module)

        self.assertEqual(inverter.model, "SIW500H ST015 M2")
        self.assertEqual(module.model, "ODA610-33V-MHDRz")
        self.assertEqual(normal.quantity, 37)
        self.assertEqual(normal.limiting_factor, LimitingFactor.OVERLOAD_LIMIT)
        self.assertEqual(ignored.quantity, 37)

    def test_compatibility_engine_expands_different_real_mppt_groups(self):
        inverter = load_inverter(self.connection, 203)
        module = load_module(self.connection, 117)
        normal, ignored = compare_operating_current_modes(inverter, module)

        self.assertEqual(len(normal.mppt_results), 6)
        self.assertGreater(ignored.quantity, normal.quantity)
        self.assertEqual(normal.limiting_factor, LimitingFactor.OPERATING_CURRENT)

    def test_real_zero_quantity_reports_operating_current_cause(self):
        inverter_row = self.connection.execute(
            "SELECT ID FROM inverter WHERE MODEL = ?", ("SIW200G M050 W1",)
        ).fetchone()
        module_row = self.connection.execute(
            "SELECT ID FROM module WHERE MODEL = ?", ("JAM66D42-570/MB",)
        ).fetchone()
        inverter = load_inverter(self.connection, inverter_row["ID"])
        module = load_module(self.connection, module_row["ID"])
        normal, ignored = compare_operating_current_modes(inverter, module)

        self.assertEqual(normal.quantity, 0)
        self.assertEqual(normal.limiting_factor, LimitingFactor.OPERATING_CURRENT)
        self.assertEqual(ignored.quantity, 13)
        self.assertEqual(ignored.limiting_factor, LimitingFactor.OVERLOAD_LIMIT)
        self.assertAlmostEqual(ignored.dc_power_kw, 7.41)
        self.assertAlmostEqual(ignored.overload_percent, 48.20)


if __name__ == "__main__":
    unittest.main()
