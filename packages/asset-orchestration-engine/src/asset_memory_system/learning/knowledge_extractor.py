import uuid
from typing import Dict, Any, Optional
from ..core.memory_schema import PatternRecord
from ..core.memory_status import PatternStatus, PatternScope

class KnowledgeExtractor:
    @staticmethod
    def extract_pattern_from_correction(
        template_id: str,
        trigger_issue: str,
        target_parameter: str,
        recommended_action: str,
        template_version: str = "1.0.0"
    ) -> PatternRecord:
        return PatternRecord(
            pattern_id=f"pat_{uuid.uuid4().hex[:6]}",
            template_id=template_id,
            trigger_issue=trigger_issue,
            recommended_action=recommended_action,
            target_parameter=target_parameter,
            status=PatternStatus.CANDIDATE,
            scope=PatternScope.TEMPLATE,
            confidence=0.60,
            evidence_count=1,
            success_count=1,
            failure_count=0,
            success_rate=1.0,
            compatible_template_versions=f">={template_version} <{int(template_version.split('.')[0])+1}.0.0"
        )
