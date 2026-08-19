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


if __name__ == "__main__":
    unittest.main()
