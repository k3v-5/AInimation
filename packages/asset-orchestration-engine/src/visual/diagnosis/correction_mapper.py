from dataclasses import dataclass
from typing import Dict, Any, List
from .difference_detector import DifferenceRecord, DifferenceType

@dataclass
class CorrectionProposal:
    target_component: str
    parameter: str
    operation: str # SET / INCREMENT / MULTIPLY
    value: Any
    reason: str = ""

class CorrectionMapper:
    @staticmethod
    def map_differences_to_corrections(differences: List[DifferenceRecord]) -> List[CorrectionProposal]:
        proposals: List[CorrectionProposal] = []

        for diff in differences:
            if diff.diff_type in [DifferenceType.LENGTH, DifferenceType.WIDTH, DifferenceType.HEIGHT, DifferenceType.DEPTH]:
                if diff.diff_type == DifferenceType.LENGTH:
                    p_name = "length"
                elif diff.axis:
                    p_name = diff.axis
                else:
                    p_name = "width" if diff.diff_type == DifferenceType.WIDTH else "thickness"
                proposals.append(CorrectionProposal(
                    target_component=diff.target_component,
                    parameter=p_name,
                    operation="SET",
                    value=diff.expected_value,
                    reason=f"Correct {diff.target_component} {p_name} from {diff.current_value}m to expected {diff.expected_value}m."
                ))

        return proposals
