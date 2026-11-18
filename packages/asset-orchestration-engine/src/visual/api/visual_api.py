from typing import Dict, Any, Optional
from ..reference.reference_loader import ReferenceLoader
from ..qa.feedback_loop import VisualFeedbackLoop
from ..qa.threshold_manager import ThresholdManager
from ..qa.report_generator import ReportGenerator
from ...geometry.core.geometry_engine import GeometryEngine

class VisualAPI:
    def __init__(self, geometry_engine: GeometryEngine):
        self.geo_engine = geometry_engine
        self.feedback_loop = VisualFeedbackLoop(self.geo_engine)

    def evaluate_asset(
        self,
        asset_id: str,
        specification: Dict[str, Any],
        reference_data: Optional[Dict[str, Any]] = None,
        profile_name: str = "GAME_ASSET",
        auto_correct: bool = False
    ) -> Dict[str, Any]:
        ref = ReferenceLoader.load_from_spec_and_dict(reference_data or {}, specification)
        self.feedback_loop.profile = ThresholdManager.get_profile(profile_name)
        return self.feedback_loop.run_qa_cycle(asset_id, ref, auto_correct=auto_correct)

    def explain_visual_report(self, report: Dict[str, Any]) -> str:
        return ReportGenerator.generate_human_readable_report(report)
