import copy
import sys
import unittest
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from compatibility.legacy_main import build_legacy_main_calculations  # noqa: E402


def fixtures(op_max=900):
    inverter = {
        "ID": 1, "MODEL": "INV", "MANUFACTURER_NAME": "FAB",
        "RATED_ACTIVE_POWER": 10_000, "OVERLOAD": 50,
        "NUMBER_OF_TRACKERS": 2, "NUMBER_OF_INPUTS": 4,
        "SYSTEM_TYPE": ["ON-GRID"], "ACTIVE": 1,
        "MPPT": [{
            "ID": 9, "MPPT_INDEX": 0, "NUMBER_OF_INPUTS": 2,
            "MAX_INPUT_VOLTAGE": 1000, "MIN_STARTUP_VOLTAGE": 100,
            "MAX_OPERATING_VOLTAGE": op_max, "MIN_OPERATING_VOLTAGE": 100,
            "MAX_FULL_LOAD_VOLTAGE": 800, "MIN_FULL_LOAD_VOLTAGE": 300,
            "MAX_SHORT_CIRCUIT_CURRENT": 100, "MAX_OPERATING_CURRENT": 100,
            "RATED_INPUT_VOLTAGE": -1,
        }],
    }
    module = {
        "ID": 2, "MODEL": "MOD", "MANUFACTURER_NAME": "FAB", "ACTIVE": 1,
        "WP": 550, "VMPP": 40, "IMPP": 10, "VOC": 50, "ISC": 11,
        "COEF_PMAX": -0.35, "COEF_VOC": -0.3, "COEF_ISC": 0.05,
    }
    return inverter, module


def calculate(inv, mod, **overrides):
    values = dict(
        minimum_cell_temperature_c=10,
        maximum_cell_temperature_c=50,
        operating_current_tolerance_fraction=0,
        power_tolerance_fraction=0.005,
        effective_overload_fraction=0.5,
        ignore_operating_current=False,
        ignore_full_load=False,
    )
    values.update(overrides)
    return build_legacy_main_calculations(inv, mod, **values)


class LegacyMainAdapterTests(unittest.TestCase):
    def test_static_main_projection_preserves_rounding_and_graph_fields(self):
        inv, mod = fixtures()
        result = calculate(inv, mod)
        self.assertEqual(result["inv"]["n_max_sb"], 27)
        self.assertEqual(result["inv"]["q_max_o"], 27)
        self.assertEqual(result["inv"]["p_max_sb_o"], 14.8)
        self.assertEqual(result["inv"]["p_max_sb_o_per"], 48)
        self.assertEqual(result["mppt"][0]["q_s_mppt"], 2)
        self.assertEqual(result["mppt"][0]["n_max_in"], 19)
        self.assertEqual(result["mppt"][0]["n_max_fl"], 19)
        self.assertAlmostEqual(result["mod"]["voc_max"], 52.25)

    def test_legacy_ignore_full_load_semantics_are_explicitly_preserved(self):
        inv, mod = fixtures(op_max=220)
        normal = calculate(inv, mod, effective_overload_fraction=10)
        ignored = calculate(inv, mod, effective_overload_fraction=10, ignore_full_load=True)
        self.assertEqual(normal["inv"]["q_max_o"], normal["inv"]["n_max_o"])
        self.assertEqual(ignored["inv"]["q_max_o"], ignored["inv"]["n_max_in"])
        self.assertGreater(ignored["inv"]["q_max_o"], normal["inv"]["q_max_o"])

    def test_adapter_does_not_mutate_legacy_dictionaries(self):
        inv, mod = fixtures()
        before = copy.deepcopy((inv, mod))
        calculate(inv, mod)
        self.assertEqual((inv, mod), before)

    def test_off_grid_only_legacy_context_uses_eps_output_contract(self):
        inv, mod = fixtures()
        inv["SYSTEM_TYPE"] = ["OFF-GRID"]
        result = calculate(inv, mod)
        self.assertEqual(result["inv"]["q_max_o"], 27)


if __name__ == "__main__":
    unittest.main()
