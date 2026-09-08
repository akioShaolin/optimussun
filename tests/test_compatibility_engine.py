import sys
import unittest
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from compatibility import (  # noqa: E402
    CompatibilityOptions,
    InverterData,
    LimitingFactor,
    ModuleData,
    MPPTData,
    analyze_compatibility,
    compare_operating_current_modes,
)


def module(power=550, vmpp=40, impp=10, voc=50, isc=11):
    return ModuleData("Módulo", power, vmpp, impp, voc, isc, -0.3, 0.05)


def mppt(
    index=1,
    inputs=2,
    max_input=1000,
    startup=100,
    op_min=100,
    op_max=900,
    isc=30,
    impp=30,
    count=1,
):
    return MPPTData(index, inputs, max_input, startup, op_max, op_min, isc, impp, count=count)


def inverter(power=10_000, overload=100, mppts=None):
    return InverterData("Inversor", power, overload, tuple(mppts or [mppt()]))


NO_FULL_LOAD = {"enforce_full_load": False, "power_tolerance": 0.0}


class CompatibilityEngineTests(unittest.TestCase):
    def test_overload_percentage_is_above_ac_nominal_power(self):
        result = analyze_compatibility(
            inverter(power=3300, overload=67, mppts=[mppt(inputs=1)]),
            module(),
            CompatibilityOptions(**NO_FULL_LOAD),
        )
        self.assertEqual(result.quantity, 10)
        self.assertAlmostEqual(result.dc_power_kw, 5.5)
        self.assertAlmostEqual(result.overload_percent, 66.6667, places=3)

    def test_result_below_nominal_power_has_negative_overload(self):
        result = analyze_compatibility(
            inverter(power=2400, overload=0, mppts=[mppt(inputs=1)]),
            module(),
            CompatibilityOptions(**NO_FULL_LOAD),
        )
        self.assertEqual(result.quantity, 4)
        self.assertAlmostEqual(result.dc_power_kw, 2.2)
        self.assertAlmostEqual(result.overload_percent, -8.3333, places=3)

    def test_ignoring_operating_current_allows_more_modules(self):
        inv = inverter(power=100_000, mppts=[mppt(inputs=2, isc=25, impp=11)])
        normal, ignored = compare_operating_current_modes(
            inv, module(), CompatibilityOptions(**NO_FULL_LOAD)
        )
        self.assertLess(normal.quantity, ignored.quantity)
        self.assertEqual(normal.limiting_factor, LimitingFactor.OPERATING_CURRENT)
        self.assertTrue(ignored.operating_current_ignored)

    def test_zero_quantity_identifies_operating_current(self):
        result = analyze_compatibility(
            inverter(power=100_000, mppts=[mppt(inputs=2, isc=25, impp=10)]),
            module(),
            CompatibilityOptions(**NO_FULL_LOAD),
        )
        self.assertEqual(result.quantity, 0)
        self.assertEqual(result.limiting_factor, LimitingFactor.OPERATING_CURRENT)

    def test_zero_quantity_identifies_short_circuit_current(self):
        result = analyze_compatibility(
            inverter(power=100_000, mppts=[mppt(inputs=2, isc=10, impp=100)]),
            module(),
            CompatibilityOptions(ignore_operating_current=True, **NO_FULL_LOAD),
        )
        self.assertEqual(result.quantity, 0)
        self.assertEqual(result.limiting_factor, LimitingFactor.SHORT_CIRCUIT_CURRENT)

    def test_zero_quantity_identifies_missing_physical_inputs(self):
        result = analyze_compatibility(
            inverter(power=100_000, mppts=[mppt(inputs=0, isc=100, impp=100)]),
            module(),
            CompatibilityOptions(**NO_FULL_LOAD),
        )
        self.assertEqual(result.quantity, 0)
        self.assertEqual(result.limiting_factor, LimitingFactor.INPUT_COUNT)

    def test_zero_quantity_identifies_operating_current(self):
        result = analyze_compatibility(
            inverter(power=100_000, mppts=[mppt(inputs=2, isc=25, impp=10)]),
            module(),
            CompatibilityOptions(**NO_FULL_LOAD),
        )
        self.assertEqual(result.quantity, 0)
        self.assertEqual(result.limiting_factor, LimitingFactor.OPERATING_CURRENT)

    def test_zero_quantity_identifies_short_circuit_current(self):
        result = analyze_compatibility(
            inverter(power=100_000, mppts=[mppt(inputs=2, isc=10, impp=100)]),
            module(),
            CompatibilityOptions(ignore_operating_current=True, **NO_FULL_LOAD),
        )
        self.assertEqual(result.quantity, 0)
        self.assertEqual(result.limiting_factor, LimitingFactor.SHORT_CIRCUIT_CURRENT)

    def test_zero_quantity_identifies_missing_physical_inputs(self):
        result = analyze_compatibility(
            inverter(power=100_000, mppts=[mppt(inputs=0, isc=100, impp=100)]),
            module(),
            CompatibilityOptions(**NO_FULL_LOAD),
        )
        self.assertEqual(result.quantity, 0)
        self.assertEqual(result.limiting_factor, LimitingFactor.INPUT_COUNT)

    def test_short_circuit_still_limits_when_operating_current_is_ignored(self):
        result = analyze_compatibility(
            inverter(mppts=[mppt(inputs=3, isc=21, impp=10)]),
            module(),
            CompatibilityOptions(ignore_operating_current=True, **NO_FULL_LOAD),
        )
        self.assertEqual(result.total_strings, 1)
        self.assertEqual(result.limiting_factor, LimitingFactor.SHORT_CIRCUIT_CURRENT)

    def test_all_physical_inputs_can_be_occupied(self):
        result = analyze_compatibility(
            inverter(power=100_000, mppts=[mppt(inputs=2, isc=100, impp=100)]),
            module(),
            CompatibilityOptions(**NO_FULL_LOAD),
        )
        self.assertEqual(result.total_strings, 2)
        self.assertEqual(result.limiting_factor, LimitingFactor.ALL_STRINGS_OCCUPIED)

    def test_maximum_voltage_limits_modules_per_string(self):
        result = analyze_compatibility(
            inverter(mppts=[mppt(inputs=1, max_input=260, op_max=1000, isc=100, impp=100)]),
            module(),
            CompatibilityOptions(**NO_FULL_LOAD),
        )
        self.assertEqual(result.modules_per_string, (4,))

    def test_insufficient_minimum_voltage_rejects_configuration(self):
        result = analyze_compatibility(
            inverter(mppts=[mppt(startup=300, op_min=300, max_input=200, op_max=200)]),
            module(),
            CompatibilityOptions(**NO_FULL_LOAD),
        )
        self.assertFalse(result.valid)
        self.assertEqual(result.limiting_factor, LimitingFactor.INSUFFICIENT_SERIES_VOLTAGE)

    def test_overload_cap_can_be_the_limiting_factor(self):
        result = analyze_compatibility(
            inverter(power=3000, overload=10, mppts=[mppt(inputs=4, isc=100, impp=100)]),
            module(power=500),
            CompatibilityOptions(**NO_FULL_LOAD),
        )
        self.assertEqual(result.quantity, 6)
        self.assertEqual(result.limiting_factor, LimitingFactor.OVERLOAD_LIMIT)

    def test_zero_quantity_is_overload_only_when_minimum_string_exceeds_cap(self):
        result = analyze_compatibility(
            inverter(power=1000, overload=0, mppts=[mppt(inputs=2, isc=100, impp=100)]),
            module(power=600),
            CompatibilityOptions(**NO_FULL_LOAD),
        )
        self.assertEqual(result.quantity, 0)
        self.assertEqual(result.limiting_factor, LimitingFactor.OVERLOAD_LIMIT)

    def test_zero_quantity_is_overload_only_when_minimum_string_exceeds_cap(self):
        result = analyze_compatibility(
            inverter(power=1000, overload=0, mppts=[mppt(inputs=2, isc=100, impp=100)]),
            module(power=600),
            CompatibilityOptions(**NO_FULL_LOAD),
        )
        self.assertEqual(result.quantity, 0)
        self.assertEqual(result.limiting_factor, LimitingFactor.OVERLOAD_LIMIT)

    def test_custom_overload_replaces_database_value_without_mutation(self):
        inv = inverter(power=3000, overload=10, mppts=[mppt(inputs=4, isc=100, impp=100)])
        registered = analyze_compatibility(inv, module(power=500), CompatibilityOptions(**NO_FULL_LOAD))
        custom = analyze_compatibility(
            inv,
            module(power=500),
            CompatibilityOptions(custom_overload_percent=50, **NO_FULL_LOAD),
        )
        self.assertGreater(custom.quantity, registered.quantity)
        self.assertEqual(inv.overload_percent, 10)

    def test_missing_data_is_not_reported_as_zero_compatibility(self):
        result = analyze_compatibility(inverter(), module(power=-1))
        self.assertFalse(result.valid)
        self.assertEqual(result.limiting_factor, LimitingFactor.MISSING_DATA)

    def test_different_mppts_are_evaluated_individually(self):
        inv = inverter(
            power=20_000,
            overload=100,
            mppts=[
                mppt(index=1, inputs=1, max_input=400, op_max=400),
                mppt(index=2, inputs=2, max_input=800, op_max=800),
            ],
        )
        result = analyze_compatibility(inv, module(), CompatibilityOptions(**NO_FULL_LOAD))
        self.assertTrue(result.valid)
        self.assertEqual(len(result.mppt_results), 2)
        self.assertNotEqual(result.modules_per_string[0], result.modules_per_string[1])


if __name__ == "__main__":
    unittest.main()
