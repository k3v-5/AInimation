from typing import Dict, Any
from ..core.amsl_schema import AssetSpecification, SpecificationDiff

class AMSLDiffEngine:
    @staticmethod
    def diff(spec_a: AssetSpecification, spec_b: AssetSpecification) -> SpecificationDiff:
        diff_res = SpecificationDiff()

        # 1. Comparar Dimensiones
        for d in ["width", "depth", "height"]:
            val_a = getattr(spec_a.dimensions, d, None)
            val_b = getattr(spec_b.dimensions, d, None)
            if val_a and val_b:
                if val_a.target != val_b.target:
                    diff_res.modified[f"dimensions.{d}"] = {"from": val_a.target, "to": val_b.target}
                else:
                    diff_res.unchanged[f"dimensions.{d}"] = val_a.target
            elif val_b and not val_a:
                diff_res.added[f"dimensions.{d}"] = val_b.target
            elif val_a and not val_b:
                diff_res.removed[f"dimensions.{d}"] = val_a.target

        # 2. Comparar Estructura (Techo, Pisos)
        if spec_a.structure.roof.get("pitch") != spec_b.structure.roof.get("pitch"):
            diff_res.modified["structure.roof.pitch"] = {
                "from": spec_a.structure.roof.get("pitch"),
                "to": spec_b.structure.roof.get("pitch")
            }
        else:
            diff_res.unchanged["structure.roof.pitch"] = spec_a.structure.roof.get("pitch")

        # 3. Comparar Componentes (Puertas, Ventanas)
        comps_a = {c.id: c for c in spec_a.components}
        comps_b = {c.id: c for c in spec_b.components}

        for c_id, comp_b in comps_b.items():
            if c_id not in comps_a:
                diff_res.added[f"component.{c_id}"] = comp_b.type
            else:
                comp_a = comps_a[c_id]
                if comp_a.parameters != comp_b.parameters or comp_a.count != comp_b.count:
                    diff_res.modified[f"component.{c_id}"] = {"from": comp_a.parameters, "to": comp_b.parameters}
                else:
                    diff_res.unchanged[f"component.{c_id}"] = comp_a.parameters

        for c_id, comp_a in comps_a.items():
            if c_id not in comps_b:
                diff_res.removed[f"component.{c_id}"] = comp_a.type

        # 4. Comparar Materiales
        mats_a = {m.material_id: m for m in spec_a.materials}
        mats_b = {m.material_id: m for m in spec_b.materials}
        for m_id, mat_b in mats_b.items():
            if m_id in mats_a:
                mat_a = mats_a[m_id]
                if mat_a.base_color != mat_b.base_color or mat_a.roughness != mat_b.roughness:
                    diff_res.modified[f"material.{m_id}"] = {"from": mat_a.base_color, "to": mat_b.base_color}
                else:
                    diff_res.unchanged[f"material.{m_id}"] = mat_a.base_color

        return diff_res
