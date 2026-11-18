from typing import List, Dict, Any
from ..core.similarity_types import DifferenceType, DifferenceSeverity
from ..core.similarity_schema import ReferenceProfile, AssetObservation, DifferenceRecord

class DifferenceDetector:
    @staticmethod
    def detect_differences(
        ref: ReferenceProfile,
        obs: AssetObservation
    ) -> List[DifferenceRecord]:
        diffs: List[DifferenceRecord] = []

        # 1. Forma de Techo / Componentes Críticos
        if "roof_type" in ref.expected_features:
            exp_roof = ref.expected_features["roof_type"]
            act_roof = obs.detected_features.get("roof_type")
            if exp_roof != act_roof:
                diffs.append(DifferenceRecord(
                    target="HOUSE.ROOF",
                    diff_type=DifferenceType.WRONG_SHAPE,
                    severity=DifferenceSeverity.CRITICAL,
                    expected=exp_roof,
                    actual=act_roof,
                    metric="roof_shape"
                ))

        # 2. Conteo de Ventanas
        if "windows" in ref.expected_features:
            exp_w = ref.expected_features["windows"]
            act_w = obs.detected_features.get("windows", 0)
            if exp_w != act_w:
                diffs.append(DifferenceRecord(
                    target="HOUSE.WINDOWS",
                    diff_type=DifferenceType.WRONG_COUNT,
                    severity=DifferenceSeverity.MEDIUM,
                    expected=exp_w,
                    actual=act_w,
                    metric="window_count"
                ))

        # 3. Componentes Faltantes (MISSING)
        if ref.expected_features.get("chimney") is True:
            if not obs.detected_features.get("chimney", False):
                diffs.append(DifferenceRecord(
                    target="HOUSE.CHIMNEY",
                    diff_type=DifferenceType.MISSING,
                    severity=DifferenceSeverity.HIGH,
                    expected="CHIMNEY_PRESENT",
                    actual="CHIMNEY_ABSENT",
                    metric="chimney_presence"
                ))

        # 4. Componentes Extras no solicitados (EXTRA)
        if obs.detected_features.get("balcony") is True and not ref.expected_features.get("balcony", False):
            diffs.append(DifferenceRecord(
                target="HOUSE.BALCONY",
                diff_type=DifferenceType.EXTRA,
                severity=DifferenceSeverity.HIGH,
                expected="NO_BALCONY",
                actual="BALCONY_DETECTED",
                metric="balcony_presence"
            ))

        # 5. Discrepancia de Proporciones
        if "roof_to_body" in ref.proportions and "roof_to_body" in obs.detected_proportions:
            exp_p = ref.proportions["roof_to_body"]
            act_p = obs.detected_proportions["roof_to_body"]
            if abs(exp_p - act_p) > 0.08:
                diffs.append(DifferenceRecord(
                    target="HOUSE.ROOF_PROPORTION",
                    diff_type=DifferenceType.WRONG_SIZE,
                    severity=DifferenceSeverity.HIGH,
                    expected=exp_p,
                    actual=act_p,
                    metric="roof_to_body_ratio"
                ))

        # 6. Discrepancia de Materiales (MATERIAL_MISMATCH)
        ref_mats = ref.expected_features.get("materials", {})
        obs_mats = obs.detected_features.get("materials", {})
        for part, exp_mat in ref_mats.items():
            act_mat = obs_mats.get(part)
            if act_mat and exp_mat != act_mat:
                diffs.append(DifferenceRecord(
                    target=f"HOUSE.MATERIAL.{part.upper()}",
                    diff_type=DifferenceType.WRONG_MATERIAL,
                    severity=DifferenceSeverity.MEDIUM,
                    expected=exp_mat,
                    actual=act_mat,
                    metric="material_category"
                ))

        return diffs
