import json
from typing import Dict, Any
from .asset_schema import (
    AssetSpecification, AssetCategory, PrimitiveType, SymmetryType,
    DimensionsSpec, ComponentSpec, StyleSpec, BudgetSpec
)
from .normalizer import UnitNormalizer
from ..core.id_manager import IdManager

class SpecificationParser:
    @classmethod
    def parse_dict(cls, data: Dict[str, Any]) -> AssetSpecification:
        asset_id = data.get("asset_id") or IdManager.generate_asset_id(data.get("name", "asset"))
        name = data.get("name", asset_id)
        cat_str = data.get("category", "prop").lower()
        try:
            category = AssetCategory(cat_str)
        except ValueError:
            category = AssetCategory.PROP

        dim_data = data.get("dimensions", {})
        if isinstance(dim_data, (list, tuple)):
            dims = DimensionsSpec(width=dim_data[0], depth=dim_data[1], height=dim_data[2])
        else:
            dims = DimensionsSpec(
                height=float(dim_data.get("height", 1.0)),
                width=float(dim_data.get("width", 1.0)),
                depth=float(dim_data.get("depth", 1.0)),
                unit=str(dim_data.get("unit", "meters"))
            )

        style_data = data.get("style", {})
        sym_str = style_data.get("symmetry", "none").lower()
        try:
            sym = SymmetryType(sym_str)
        except ValueError:
            sym = SymmetryType.NONE
        style = StyleSpec(
            category=style_data.get("category", style_data.get("type", "stylized")),
            symmetry=sym,
            tags=style_data.get("tags", [])
        )

        budget_data = data.get("budget", data.get("geometry", {}))
        budget = BudgetSpec(
            max_triangles=int(budget_data.get("max_triangles", budget_data.get("polygon_budget", 10000))),
            polygon_budget=int(budget_data.get("polygon_budget", 5000)),
            max_materials=int(budget_data.get("max_materials", 4))
        )

        comps = []
        for c_data in data.get("components", data.get("parts", [])):
            cid = c_data.get("id", c_data.get("name"))
            ctype = c_data.get("type", cid)
            prim_str = c_data.get("primitive", "box").lower()
            try:
                prim = PrimitiveType(prim_str)
            except ValueError:
                prim = PrimitiveType.BOX

            c_dims = None
            if "dimensions" in c_data:
                cd = c_data["dimensions"]
                c_dims = DimensionsSpec(
                    height=float(cd.get("height", 1.0)),
                    width=float(cd.get("width", 1.0)),
                    depth=float(cd.get("depth", 1.0)),
                    unit=str(cd.get("unit", "meters"))
                )
            elif "scale" in c_data:
                s = c_data["scale"]
                c_dims = DimensionsSpec(width=s[0], depth=s[1], height=s[2])

            comp = ComponentSpec(
                id=cid,
                type=ctype,
                primitive=prim,
                parent_id=c_data.get("parent", c_data.get("parent_id")),
                dimensions=c_dims,
                relative_position=tuple(c_data.get("position", c_data.get("relative_position", (0.0, 0.0, 0.0)))),
                relative_rotation=tuple(c_data.get("rotation", c_data.get("relative_rotation", (0.0, 0.0, 0.0)))),
                relative_scale=tuple(c_data.get("scale", c_data.get("relative_scale", (1.0, 1.0, 1.0)))),
                material_id=c_data.get("material", c_data.get("material_id")),
                properties=c_data.get("properties", {})
            )
            comps.append(comp)

        spec = AssetSpecification(
            asset_id=asset_id,
            name=name,
            category=category,
            dimensions=dims,
            style=style,
            budget=budget,
            components=comps,
            materials=data.get("materials", []),
            engine_target=data.get("engine_target", data.get("engine", {}).get("target", "unreal")),
            version=data.get("version", 1),
            metadata=data.get("metadata", {})
        )

        return UnitNormalizer.normalize_specification(spec)

    @classmethod
    def parse_json(cls, json_str: str) -> AssetSpecification:
        data = json.loads(json_str)
        return cls.parse_dict(data)
