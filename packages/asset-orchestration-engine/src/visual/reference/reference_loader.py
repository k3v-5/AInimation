from typing import Dict, Any, Optional, List
from .reference_metadata import VisualReference, ReferenceView, ReferenceType
from ..capture.camera_manager import ViewOrientation

class ReferenceLoader:
    @staticmethod
    def load_from_spec_and_dict(ref_data: Dict[str, Any], specification: Dict[str, Any]) -> VisualReference:
        ref_id = ref_data.get("reference_id", "ref_default")
        rtype_str = ref_data.get("type", "specification_only").lower()
        
        try:
            rtype = ReferenceType(rtype_str)
        except ValueError:
            rtype = ReferenceType.SPECIFICATION_ONLY

        expected_dims = {}
        expected_struct = []
        for comp in specification.get("components", []):
            cid = comp.get("id", comp.get("name", ""))
            if cid:
                expected_struct.append(cid)
                dim = comp.get("dimensions", {})
                if isinstance(dim, dict):
                    expected_dims[cid] = {
                        "width": float(dim.get("width", 1.0)),
                        "depth": float(dim.get("depth", 1.0)),
                        "height": float(dim.get("height", 1.0))
                    }

        # Cargar vistas de referencia
        views = {}
        if "views" in ref_data:
            for v_orient_str, v_info in ref_data["views"].items():
                try:
                    vo = ViewOrientation(v_orient_str.lower())
                    views[vo] = ReferenceView(
                        orientation=vo,
                        weight=float(v_info.get("weight", 1.0)),
                        expected_aspect_ratio=v_info.get("aspect_ratio"),
                        expected_components=v_info.get("components", expected_struct),
                        grid_occupancy=v_info.get("grid")
                    )
                except ValueError:
                    pass
        else:
            # Vista frontal por defecto
            views[ViewOrientation.FRONT] = ReferenceView(
                orientation=ViewOrientation.FRONT,
                weight=1.0,
                expected_components=expected_struct
            )

        return VisualReference(
            reference_id=ref_id,
            ref_type=rtype,
            views=views,
            expected_dimensions=expected_dims,
            expected_structure=expected_struct,
            style_metadata=ref_data.get("style", {})
        )
