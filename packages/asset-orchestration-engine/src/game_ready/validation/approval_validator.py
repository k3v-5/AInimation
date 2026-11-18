from typing import Tuple, Optional

class ApprovalValidator:
    @staticmethod
    def validate_approvals(geometry_status: str, appearance_status: str) -> Tuple[bool, Optional[str]]:
        if geometry_status != "APPROVED":
            return False, f"GEOMETRY_NOT_APPROVED: Source geometry must be APPROVED (currently '{geometry_status}')."
        if appearance_status != "APPROVED":
            return False, f"APPEARANCE_NOT_APPROVED: Source appearance must be APPROVED (currently '{appearance_status}')."
        return True, None
