import copy
import subprocess
import sys
import unittest
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from calculation_core import (  # noqa: E402
    CalculationOptions,
    CalculationRequest,
    InverterInput,
    IssueCode,
    LimitingFactor,
    ModuleInput,
    MPPTGroup,
    OutputProfile,
    ProfileType,
    calculate,
    resolve_output_profile,
)


def group(index=1, count=1, inputs=2, max_input=1000, startup=100,
          op_min=100, op_max=900, isc=30, impp=30,
          full_min=None, full_max=None, group_id=1):
    return MPPTGroup(
        group_id, index, count, inputs, max_input, startup, op_max, op_min,
        isc, impp, full_min, full_max, source="fixture"
    )


def inverter(groups=None, systems=("ON-GRID",), overload=100, active=True):
    return InverterInput(
        10, "Fabricante", "Inversor", overload,
        tuple(groups or (group(),)), systems, active, 7, "fixture"
    )


def module(power=550, vmpp=40, impp=10, voc=50, isc=11):
    return ModuleInput(
        20, "Fabricante", "Módulo", power, vmpp, impp, voc, isc,
        -0.3, 0.05, -0.35, True, 3, "fixture"
    )


def profile(profile_id=100, inverter_id=10, profile_type=ProfileType.AC_OUTPUT,
            power=10_000, active=True, default=True):
    return OutputProfile(
        profile_id, inverter_id, profile_type, power,
        output_mode_id=2, output_mode="THREE_PHASE_THREE_WIRE",
        max_active_power_w=11_000, max_peak_active_power_w=12_000,
        rated_line_to_line_voltage_v=380,
        rated_line_to_neutral_voltage_v=220,
        active=active, is_default=default, row_version=9, source="fixture",
    )


def request(inv=None, mod=None, output=None, options=None):
    return CalculationRequest(
        inv or inverter(), mod or module(), output or profile(),
        options or CalculationOptions(enforce_full_load=False, power_tolerance=0),
    )


class ProfileResolutionTests(unittest.TestCase):
    def test_explicit_selection_uses_selected_power_without_combining_profiles(self):
        inv = inverter()
        low = profile(100, power=5_000, default=True)
        high = profile(101, power=10_000, default=False)
        selected = resolve_output_profile(inv, (low, high), 101)
        self.assertTrue(selected.valid)
        result = calculate(request(inv=inv, output=selected.profile))
        low_result = calculate(request(inv=inv, output=low))
        self.assertGreater(result.quantity, low_result.quantity)
        self.assertEqual(result.profile_id, 101)
        self.assertEqual(result.rated_active_power_w, 10_000)
        self.assertEqual(result.max_active_power_w, 11_000)
        self.assertEqual(result.max_peak_active_power_w, 12_000)
        self.assertEqual(result.rated_line_to_line_voltage_v, 380)
        self.assertEqual(result.rated_line_to_neutral_voltage_v, 220)
        self.assertEqual(result.output_mode, "THREE_PHASE_THREE_WIRE")
        self.assertEqual(result.inverter_source, "fixture")
        self.assertEqual(result.module_source, "fixture")
        self.assertEqual(result.profile_source, "fixture")

    def test_default_profile_is_used_only_when_unique_and_valid(self):
        chosen = resolve_output_profile(inverter(), (profile(100), profile(101, default=False)))
        self.assertTrue(chosen.valid)
        self.assertEqual(chosen.profile.profile_id, 100)

    def test_no_default_or_selection_requires_choice(self):
        resolved = resolve_output_profile(inverter(), (profile(default=False),))
        self.assertFalse(resolved.valid)
        self.assertTrue(resolved.selection_required)

    def test_multiple_valid_defaults_are_not_resolved_silently(self):
        resolved = resolve_output_profile(inverter(), (profile(100), profile(101)))
        self.assertFalse(resolved.valid)
        self.assertEqual(resolved.issues[0].code, IssueCode.MULTIPLE_DEFAULT_PROFILES)

    def test_eps_is_eligible_for_off_grid(self):
        inv = inverter(systems=("OFF-GRID",))
        resolved = resolve_output_profile(inv, (profile(profile_type=ProfileType.EPS_OUTPUT),))
        self.assertTrue(resolved.valid)

    def test_ac_output_is_eligible_for_grid_zero(self):
        resolved = resolve_output_profile(inverter(systems=("GRIDZERO",)), (profile(),))
        self.assertTrue(resolved.valid)

    def test_ac_input_inactive_and_other_inverter_are_rejected(self):
        inv = inverter(systems=("HYBRID",))
        cases = (
            profile(profile_type=ProfileType.AC_INPUT),
            profile(active=False),
            profile(inverter_id=999),
        )
        expected = (
            IssueCode.PROFILE_TYPE_NOT_ELIGIBLE,
            IssueCode.PROFILE_INACTIVE,
            IssueCode.PROFILE_WRONG_INVERTER,
        )
        for candidate, code in zip(cases, expected):
            with self.subTest(code=code):
                resolved = resolve_output_profile(inv, (candidate,), candidate.profile_id)
                self.assertFalse(resolved.valid)
                self.assertIn(code, {item.code for item in resolved.issues})

    def test_output_profile_without_mode_is_rejected(self):
        candidate = OutputProfile(100, 10, ProfileType.AC_OUTPUT, 10_000)
        resolved = resolve_output_profile(inverter(), (candidate,), 100)
        self.assertFalse(resolved.valid)
        self.assertIn(IssueCode.PROFILE_OUTPUT_MODE_MISSING, {item.code for item in resolved.issues})


class CalculationCoreTests(unittest.TestCase):
    def test_homogeneous_fixture_matches_pre_extraction_baseline(self):
        inv = inverter(groups=(group(inputs=1),), overload=67)
        result = calculate(request(inv=inv, output=profile(power=3300)))
        self.assertEqual(result.quantity, 10)
        self.assertEqual(result.dc_power_kw, 5.5)
        self.assertAlmostEqual(result.overload_percent, 66.6666666667)
        self.assertEqual(result.limiting_factor, LimitingFactor.OVERLOAD_LIMIT)
        self.assertEqual(result.total_strings, 1)
        self.assertEqual(result.mppt_results[0].modules_per_string, 10)
        self.assertEqual(result.total_limits.max_modules_by_overload, 10)

    def test_heterogeneous_fixture_matches_pre_extraction_baseline(self):
        inv = inverter(groups=(
            group(1, inputs=1, max_input=400, op_max=400, group_id=1),
            group(2, inputs=2, max_input=800, op_max=800, group_id=2),
        ))
        result = calculate(request(inv=inv, output=profile(power=20_000)))
        self.assertEqual(result.quantity, 37)
        self.assertEqual(tuple(item.modules_per_string for item in result.mppt_results), (7, 15))
        self.assertEqual(tuple(item.strings for item in result.mppt_results), (1, 2))

    def test_custom_overload_replaces_registered_value_and_exact_floor_is_stable(self):
        inv = inverter(groups=(group(inputs=20, isc=500, impp=500),), overload=10)
        options = CalculationOptions(custom_overload_percent=50, enforce_full_load=False, power_tolerance=0.005)
        result = calculate(request(inv=inv, mod=module(power=500), output=profile(power=100_000), options=options))
        self.assertEqual(result.effective_overload_percent, 50)
        self.assertEqual(result.overload_limit, 301)
        self.assertEqual(inv.overload_percent, 10)

    def test_registered_and_custom_overload_follow_distinct_explicit_options(self):
        inv = inverter(groups=(group(inputs=4, isc=100, impp=100),), overload=10)
        output = profile(power=3_000)
        registered = calculate(request(inv=inv, mod=module(power=500), output=output))
        custom = calculate(request(
            inv=inv, mod=module(power=500), output=output,
            options=CalculationOptions(custom_overload_percent=50, enforce_full_load=False, power_tolerance=0),
        ))
        self.assertEqual(registered.quantity, 6)
        self.assertEqual(custom.quantity, 9)

    def test_operating_current_can_be_ignored_without_fabricating_missing_limit(self):
        inv = inverter(groups=(group(impp=None, isc=25),))
        normal = calculate(request(inv=inv))
        ignored = calculate(request(inv=inv, options=CalculationOptions(ignore_operating_current=True, enforce_full_load=False, power_tolerance=0)))
        self.assertFalse(normal.valid)
        self.assertIsNone(normal.quantity)
        self.assertTrue(ignored.valid)
        self.assertIsNone(ignored.mppt_limits[0].operating_current_limit)

    def test_full_load_option_changes_only_full_load_constraint(self):
        inv = inverter(groups=(group(isc=100, impp=100, full_min=300, full_max=350),))
        enforced = calculate(request(inv=inv, output=profile(power=50_000), options=CalculationOptions(enforce_full_load=True, power_tolerance=0)))
        ignored = calculate(request(inv=inv, output=profile(power=50_000), options=CalculationOptions(enforce_full_load=False, power_tolerance=0)))
        self.assertEqual(enforced.quantity, 0)
        self.assertEqual(enforced.limiting_factor, LimitingFactor.FULL_LOAD_RANGE)
        self.assertGreater(ignored.quantity, 0)

    def test_missing_data_is_structured_and_not_coerced_to_zero(self):
        result = calculate(request(mod=module(power=None)))
        self.assertFalse(result.valid)
        self.assertIsNone(result.quantity)
        self.assertIsNone(result.dc_power_kw)
        self.assertIsNone(result.overload_percent)
        self.assertEqual(result.limiting_factor, LimitingFactor.MISSING_DATA)
        self.assertIn("module.nominal_power_w", {item.field for item in result.issues})

    def test_negative_temperatures_and_coefficients_remain_valid(self):
        options = CalculationOptions(min_cell_temperature_c=-10, max_cell_temperature_c=60, enforce_full_load=False)
        result = calculate(request(options=options))
        self.assertTrue(result.valid)
        self.assertGreater(result.thermal.voc_max_v, result.thermal.voc_min_v)

    def test_per_mppt_current_is_not_divided_by_inputs(self):
        inv = inverter(groups=(group(inputs=5, isc=162.5, impp=130),))
        result = calculate(request(inv=inv, mod=module(impp=20, isc=20)))
        self.assertEqual(result.mppt_limits[0].short_circuit_limit, 8)
        self.assertEqual(result.mppt_limits[0].operating_current_limit, 6)

    def test_calculation_is_deterministic_and_does_not_mutate_request(self):
        original = request()
        snapshot = copy.deepcopy(original)
        first = calculate(original)
        second = calculate(original)
        self.assertEqual(first, second)
        self.assertEqual(original, snapshot)

    def test_inactive_equipment_is_not_rejected_by_core(self):
        result = calculate(request(inv=inverter(active=False)))
        self.assertTrue(result.valid)

    def test_core_import_does_not_load_gui_or_database_modules(self):
        code = (
            f"import sys; sys.path.insert(0, {str(SRC_DIR)!r}); import calculation_core; "
            "assert not ({'tkinter','matplotlib','sqlite3','pymysql'} & set(sys.modules))"
        )
        completed = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()
