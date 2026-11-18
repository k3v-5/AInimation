from .asset_schema import DimensionsSpec, AssetSpecification

class UnitNormalizer:
    FACTORS_TO_METERS = {
        "m": 1.0, "meter": 1.0, "meters": 1.0,
        "cm": 0.01, "centimeter": 0.01, "centimeters": 0.01,
        "mm": 0.001, "millimeter": 0.001,
        "in": 0.0254, "inch": 0.0254, "inches": 0.0254,
        "ft": 0.3048, "foot": 0.3048, "feet": 0.3048,
        "uu": 0.01
    }

    @classmethod
    def normalize_dimensions(cls, dims: DimensionsSpec) -> DimensionsSpec:
        unit = (dims.unit or "meters").lower().strip()
        factor = cls.FACTORS_TO_METERS.get(unit, 1.0)
        return DimensionsSpec(
            height=round(dims.height * factor, 6),
            width=round(dims.width * factor, 6),
            depth=round(dims.depth * factor, 6),
            unit="meters"
        )

    @classmethod
    def normalize_specification(cls, spec: AssetSpecification) -> AssetSpecification:
        spec.dimensions = cls.normalize_dimensions(spec.dimensions)
        for comp in spec.components:
            if comp.dimensions:
                comp.dimensions = cls.normalize_dimensions(comp.dimensions)
        return spec
