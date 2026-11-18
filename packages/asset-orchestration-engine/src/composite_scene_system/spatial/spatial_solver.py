import math
from typing import Dict, Any, List
from ..core.scene_schema import AssetInstance, SceneSpecification

class SpatialConstraintSolver:
    @staticmethod
    def solve_village_radial_layout(
        spec: SceneSpecification,
        instances: Dict[str, AssetInstance]
    ) -> Dict[str, AssetInstance]:
        """
        Resuelve colocación radial de casas, plaza, iglesia y tiendas.
        """
        houses = [inst for inst in instances.values() if inst.asset_type == "HOUSE"]
        shops = [inst for inst in instances.values() if inst.asset_type == "SHOP"]
        church = next((inst for inst in instances.values() if inst.asset_type == "CHURCH"), None)
        plaza = next((inst for inst in instances.values() if inst.asset_type == "PLAZA"), None)

        # 1. Plaza en el centro
        if plaza:
            plaza.transform = {"x": 0.0, "y": 0.0, "z": 0.0, "rot_z": 0.0}
            plaza.region_id = "CENTER"

        # 2. Iglesia en el norte a 18m
        if church:
            church.transform = {"x": 0.0, "y": 18.0, "z": 0.0, "rot_z": 180.0}
            church.region_id = "NORTH"

        # 3. Tiendas cerca del centro en el sur
        for idx, shop in enumerate(shops):
            angle = -60.0 if idx == 0 else -120.0 # Posicionamiento sur-este / sur-oeste
            rad = math.radians(angle)
            dist = 11.0
            shop.transform = {
                "x": round(math.cos(rad) * dist, 2),
                "y": round(math.sin(rad) * dist, 2),
                "z": 0.0,
                "rot_z": round((math.degrees(math.atan2(-math.sin(rad), -math.cos(rad)))) % 360, 1)
            }
            shop.region_id = "COMMERCIAL"

        # 4. Casas distribuidas radialmente a 24m con offset de ángulo (22.5°) para dejar libre el corredor norte de la iglesia
        num_houses = len(houses)
        for idx, house in enumerate(houses):
            angle_deg = (360.0 / max(1, num_houses)) * idx + 22.5
            rad = math.radians(angle_deg)
            dist = 24.0

            hx = round(math.cos(rad) * dist, 2)
            hy = round(math.sin(rad) * dist, 2)
            facing_rot = round(math.degrees(math.atan2(-hy, -hx)) % 360, 1)

            # Asignar región cardinal
            if -45 <= (angle_deg % 360) < 45 or (angle_deg % 360) >= 315:
                reg = "EAST_REGION"
            elif 45 <= (angle_deg % 360) < 135:
                reg = "NORTH_REGION"
            elif 135 <= (angle_deg % 360) < 225:
                reg = "WEST_REGION"
            else:
                reg = "SOUTH_REGION"

            house.transform = {"x": hx, "y": hy, "z": 0.0, "rot_z": facing_rot}
            house.region_id = reg

        return instances
