# -*- coding: utf-8 -*-
# weapon_proportion_guard.py
# Guardian de Proporciones Metricas y Aspect Ratio de Armas para DarX
# Previene que armas gigantescas, desproporcionadas o con escalas erroneas se importen o equipen.

from typing import Dict, Any, List, Optional, Tuple

class WeaponSpec:
    def __init__(
        self,
        category: str,
        min_length_cm: float,
        max_length_cm: float,
        min_width_cm: float,
        max_width_cm: float,
        min_height_cm: float,
        max_height_cm: float,
        min_aspect_ratio_lw: float,
        max_aspect_ratio_lw: float,
        max_sphere_radius_cm: float
    ):
        self.category = category
        self.min_length_cm = min_length_cm
        self.max_length_cm = max_length_cm
        self.min_width_cm = min_width_cm
        self.max_width_cm = max_width_cm
        self.min_height_cm = min_height_cm
        self.max_height_cm = max_height_cm
        self.min_aspect_ratio_lw = min_aspect_ratio_lw
        self.max_aspect_ratio_lw = max_aspect_ratio_lw
        self.max_sphere_radius_cm = max_sphere_radius_cm

SPECS_CATALOG: Dict[str, WeaponSpec] = {
    "HANDGUN": WeaponSpec("HANDGUN", 18.0, 45.0, 3.0, 8.0, 10.0, 25.0, 3.0, 9.0, 30.0),
    "SMG": WeaponSpec("SMG", 30.0, 58.0, 4.0, 12.0, 10.0, 22.0, 3.0, 10.0, 35.0),
    "SHOTGUN": WeaponSpec("SHOTGUN", 55.0, 95.0, 5.0, 14.0, 15.0, 30.0, 4.0, 14.0, 55.0),
    "RIFLE": WeaponSpec("RIFLE", 60.0, 105.0, 4.0, 12.0, 18.0, 32.0, 4.5, 15.0, 55.0),
    "SHIELD": WeaponSpec("SHIELD", 40.0, 130.0, 10.0, 90.0, 40.0, 150.0, 0.5, 4.0, 90.0),
    "TOOL": WeaponSpec("TOOL", 25.0, 70.0, 5.0, 20.0, 10.0, 35.0, 1.5, 10.0, 45.0)
}

ASSET_CATEGORY_MAP: Dict[str, str] = {
    "SM_Wep_Apex6": "HANDGUN",
    "SM_Wep_PhaseSMG": "SMG",
    "SM_Wep_BreacherS4": "SHOTGUN",
    "SM_Wep_VanguardAR": "RIFLE",
    "SM_Shield_Aegis": "SHIELD",
    "SM_Tool_ArcCutter": "TOOL"
}

class WeaponProportionGuard:
    @staticmethod
    def infer_category(mesh_name: str) -> str:
        for prefix, cat in ASSET_CATEGORY_MAP.items():
            if prefix.lower() in mesh_name.lower():
                return cat
        name_lower = mesh_name.lower()
        if "shotgun" in name_lower or "breacher" in name_lower:
            return "SHOTGUN"
        elif "rifle" in name_lower or "ar" in name_lower or "vanguard" in name_lower:
            return "RIFLE"
        elif "smg" in name_lower or "phase" in name_lower:
            return "SMG"
        elif "pistol" in name_lower or "handgun" in name_lower or "apex" in name_lower:
            return "HANDGUN"
        elif "shield" in name_lower or "aegis" in name_lower:
            return "SHIELD"
        return "TOOL"

    @classmethod
    def validate_proportions(
        cls,
        mesh_name: str,
        width_cm: float,
        length_cm: float,
        height_cm: float,
        sphere_radius_cm: float
    ) -> Dict[str, Any]:
        category = cls.infer_category(mesh_name)
        spec = SPECS_CATALOG.get(category, SPECS_CATALOG["TOOL"])
        
        errors: List[str] = []
        warnings: List[str] = []
        
        # 1. Validar longitud (dimension mayor)
        if length_cm < spec.min_length_cm:
            errors.append(f"Longitud ({length_cm:.1f} cm) menor al minimo permitido ({spec.min_length_cm} cm) para {category}")
        elif length_cm > spec.max_length_cm:
            errors.append(f"Longitud ({length_cm:.1f} cm) excede el maximo permitido ({spec.max_length_cm} cm) para {category}")
            
        # 2. Validar ancho
        if width_cm < spec.min_width_cm:
            errors.append(f"Ancho ({width_cm:.1f} cm) menor al minimo ({spec.min_width_cm} cm) para {category}")
        elif width_cm > spec.max_width_cm:
            errors.append(f"Ancho ({width_cm:.1f} cm) excede el maximo ({spec.max_width_cm} cm) para {category}")
            
        # 3. Validar altura
        if height_cm < spec.min_height_cm:
            errors.append(f"Altura ({height_cm:.1f} cm) menor al minimo ({spec.min_height_cm} cm) para {category}")
        elif height_cm > spec.max_height_cm:
            errors.append(f"Altura ({height_cm:.1f} cm) excede el maximo ({spec.max_height_cm} cm) para {category}")
            
        # 4. Validar radio de esfera envolvente
        if sphere_radius_cm > spec.max_sphere_radius_cm:
            errors.append(f"Radio envolvente ({sphere_radius_cm:.1f} cm) excede el limite ({spec.max_sphere_radius_cm} cm) para {category}")
            
        # 5. Aspect Ratio (Longitud / Ancho)
        ratio_lw = length_cm / max(width_cm, 0.001)
        ratio_lh = length_cm / max(height_cm, 0.001)
        
        if ratio_lw < spec.min_aspect_ratio_lw:
            warnings.append(f"Aspect Ratio L:W ({ratio_lw:.2f}) demasiado ancho (esperado >= {spec.min_aspect_ratio_lw})")
        elif ratio_lw > spec.max_aspect_ratio_lw:
            warnings.append(f"Aspect Ratio L:W ({ratio_lw:.2f}) demasiado estrecho (esperado <= {spec.max_aspect_ratio_lw})")
            
        passed = len(errors) == 0
        summary = (
            f"[{'PASS' if passed else 'FAIL'}] {mesh_name} ({category}): "
            f"L={length_cm:.1f}cm, W={width_cm:.1f}cm, H={height_cm:.1f}cm, R={sphere_radius_cm:.1f}cm | "
            f"Ratios (L:W={ratio_lw:.1f}:1, L:H={ratio_lh:.1f}:1)"
        )
        
        return {
            "mesh_name": mesh_name,
            "category": category,
            "passed": passed,
            "dimensions_cm": {
                "width": round(width_cm, 2),
                "length": round(length_cm, 2),
                "height": round(height_cm, 2),
                "sphere_radius": round(sphere_radius_cm, 2)
            },
            "aspect_ratio": {
                "length_to_width": round(ratio_lw, 2),
                "length_to_height": round(ratio_lh, 2)
            },
            "errors": errors,
            "warnings": warnings,
            "summary": summary
        }

if __name__ == "__main__":
    test_cases = [
        ("SM_Wep_Apex6", 6.27, 34.87, 19.21, 19.32),
        ("SM_Wep_PhaseSMG", 16.42, 87.08, 25.21, 44.90),
        ("SM_Wep_BreacherS4", 8.20, 75.00, 20.63, 38.84),
        ("SM_Wep_VanguardAR", 6.22, 75.00, 25.23, 38.55),
        ("SM_Shield_Aegis", 25.0, 95.0, 110.0, 55.0),
        ("SM_Tool_ArcCutter", 12.0, 48.0, 22.0, 28.0),
        ("SM_Wep_Gigante_Invalida", 150.0, 450.0, 120.0, 250.0)
    ]
    
    print("=== EJECUTANDO WEAPON PROPORTION GUARD ===")
    for name, w, l, h, r in test_cases:
        res = WeaponProportionGuard.validate_proportions(name, w, l, h, r)
        print(res["summary"])
        if res["errors"]:
            print(f"   [!] Errores: {res['errors']}")
        if res["warnings"]:
            print(f"   [*] Advertencias: {res['warnings']}")
