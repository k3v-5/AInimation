"""
UnitNormalizer standardizes physical measurement representations to canonical base units (meters).
UAF-81.1 Sections 18, 19.
"""

import re
from typing import Union, Tuple


class UnitNormalizer:
    """
    Normalizes string or numeric dimension specifications into canonical SI units (meters).
    """
    _LENGTH_FACTORS = {
        "m": 1.0,
        "meter": 1.0,
        "meters": 1.0,
        "cm": 0.01,
        "centimeter": 0.01,
        "centimeters": 0.01,
        "mm": 0.001,
        "millimeter": 0.001,
        "millimeters": 0.001,
        "km": 1000.0,
        "kilometer": 1000.0,
        "kilometers": 1000.0,
        "in": 0.0254,
        "inch": 0.0254,
        "inches": 0.0254,
        "ft": 0.3048,
        "foot": 0.3048,
        "feet": 0.3048,
        "yd": 0.9144,
        "yard": 0.9144,
        "yards": 0.9144,
    }

    _REGEX = re.compile(r"^([+-]?\d+(?:\.\d+)?)\s*([a-zA-Z]+)?$")

    @classmethod
    def normalize_length(cls, value: Union[str, float, int]) -> float:
        """
        Parses dimension inputs like '185cm', '1.85m', '6ft' and returns float in meters.
        If numeric without unit, assumes meters.
        """
        if isinstance(value, (int, float)):
            return float(value)

        val_str = str(value).strip().lower()
        match = cls._REGEX.match(val_str)
        if not match:
            raise ValueError(f"Cannot parse dimension with unit: '{value}'")

        number_str, unit_str = match.groups()
        number = float(number_str)

        if not unit_str:
            return number

        unit = unit_str.lower()
        if unit not in cls._LENGTH_FACTORS:
            raise ValueError(f"Unknown or unsupported unit '{unit_str}' in '{value}'. Supported: {list(cls._LENGTH_FACTORS.keys())}")

        return round(number * cls._LENGTH_FACTORS[unit], 6)
