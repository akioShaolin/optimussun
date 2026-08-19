import sys
import unittest
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from optimus_lib import (  # noqa: E402
    compensacao_termica,
    limite_strings_curto_circuito,
    limite_strings_operacao,
    limite_modulos_sobrecarga,
    limites_modulos_serie,
    minimo_valido,
)


class ThermalCompensationTests(unittest.TestCase):
    def test_negative_coefficient_reverses_temperature_extremes(self):
        minimo, maximo = compensacao_termica(-0.004, 0, 50, 100)
        self.assertAlmostEqual(minimo, 90)
        self.assertAlmostEqual(maximo, 110)

    def test_positive_coefficient_preserves_temperature_order(self):
        minimo, maximo = compensacao_termica(0.001, 0, 50, 100)
        self.assertAlmostEqual(minimo, 97.5)
        self.assertAlmostEqual(maximo, 102.5)


class StringLimitTests(unittest.TestCase):
    def test_q_s_mppt_ignores_missing_limits(self):
        self.assertEqual(minimo_valido([2, -1, None]), 2)

    def test_q_s_mppt_returns_sentinel_without_valid_limits(self):
        self.assertEqual(minimo_valido([-1, None]), -1)

    def test_q_s_mppt_selects_smallest_limit_for_different_input_counts(self):
        self.assertEqual(minimo_valido([4, 3, 2]), 2)

    def test_short_circuit_limit_uses_isc(self):
        self.assertEqual(limite_strings_curto_circuito(40, 13), 3)

    def test_short_circuit_limit_rejects_missing_or_zero_isc(self):
        self.assertEqual(limite_strings_curto_circuito(40, None), -1)
        self.assertEqual(limite_strings_curto_circuito(40, 0), -1)

    def test_operating_limit_applies_tolerance(self):
        self.assertEqual(limite_strings_operacao(30, 11, 0.10), 3)

    def test_series_limits_round_in_safe_directions(self):
        self.assertEqual(limites_modulos_serie(200, 1000, 35, 50), (6, 20))

    def test_series_limits_handle_incomplete_mppt_data(self):
        self.assertEqual(limites_modulos_serie(None, 1000, 35, 50), (-1, -1))

    def test_overload_limit_and_invalid_module_power(self):
        self.assertEqual(limite_modulos_sobrecarga(100_000, 0.50, 0.005, 500), 301)
        self.assertEqual(limite_modulos_sobrecarga(100_000, 0.50, 0.005, 0), 0)
        self.assertEqual(limite_modulos_sobrecarga(None, 0.50, 0.005, 500), 0)


if __name__ == "__main__":
    unittest.main()
