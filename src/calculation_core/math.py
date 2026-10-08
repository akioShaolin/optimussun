"""Fórmulas escalares compartilhadas pelo produto."""

import math


def thermal_compensation(coefficient_fraction, minimum_temperature_c, maximum_temperature_c, value):
    value_at_minimum = value * (1 + coefficient_fraction * (minimum_temperature_c - 25))
    value_at_maximum = value * (1 + coefficient_fraction * (maximum_temperature_c - 25))
    return min(value_at_minimum, value_at_maximum), max(value_at_minimum, value_at_maximum)


def valid_minimum(values):
    valid = [value for value in values if value is not None and value >= 0]
    return min(valid) if valid else -1


def short_circuit_string_limit(maximum_current_a, module_current_a):
    if maximum_current_a is None or module_current_a is None or module_current_a <= 0:
        return -1
    return math.floor(maximum_current_a / module_current_a)


def operating_string_limit(maximum_current_a, module_current_a, tolerance_fraction):
    if maximum_current_a is None or module_current_a is None or module_current_a <= 0:
        return -1
    return math.floor(maximum_current_a * (1 + tolerance_fraction) / module_current_a)


def series_module_limits(minimum_voltage_v, maximum_voltage_v, module_minimum_v, module_maximum_v):
    if any(
        value is None or value <= 0
        for value in (minimum_voltage_v, maximum_voltage_v, module_minimum_v, module_maximum_v)
    ):
        return -1, -1
    return math.ceil(minimum_voltage_v / module_minimum_v), math.floor(maximum_voltage_v / module_maximum_v)


def overload_module_limit(rated_power_w, overload_fraction, tolerance_fraction, module_power_w):
    if (
        rated_power_w is None
        or overload_fraction is None
        or tolerance_fraction is None
        or module_power_w is None
        or rated_power_w <= 0
        or module_power_w <= 0
    ):
        return 0
    return math.floor(rated_power_w * (1 + overload_fraction) * (1 + tolerance_fraction) / module_power_w)
