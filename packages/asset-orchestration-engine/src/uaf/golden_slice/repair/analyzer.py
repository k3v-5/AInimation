"""Autonomous failure analysis engine: subsystem classification and root cause identification."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FailureDiagnosis:
    failure_id: str
    subsystem: str
    symptom: str
    probable_cause: str
    suggested_repair: str
    severity: str = "ERROR"  # "INFO", "WARNING", "BLOCKING_WARNING", "ERROR", "FATAL"


class FailureAnalyzer:
    """Analyzes runtime error logs, stack traces, and anomalies to diagnose faults."""

    def diagnose(
        self,
        error_message: str,
        subsystem: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> FailureDiagnosis:
        err_lower = error_message.lower()

        if "texture" in err_lower or "material" in err_lower:
            return FailureDiagnosis(
                failure_id="diag_tex_01",
                subsystem="Rendering/Material",
                symptom="MISSING_TEXTURE_MAP",
                probable_cause="Asset dependency path was not resolved prior to material compilation",
                suggested_repair="assign_fallback_texture",
            )
        elif "orphan" in err_lower or "unmapped" in err_lower:
            return FailureDiagnosis(
                failure_id="diag_reg_01",
                subsystem="Registry/Scene",
                symptom="ORPHAN_ACTOR",
                probable_cause="Actor instantiated in UE5 without synchronization handshake",
                suggested_repair="unregister_orphan_actor",
            )
        elif "particle" in err_lower or "niagara" in err_lower or "vfx" in err_lower:
            return FailureDiagnosis(
                failure_id="diag_vfx_01",
                subsystem="VFX/Niagara",
                symptom="FRAME_SPIKE_VFX",
                probable_cause="Particle emitter spawn rate exceeds GPU buffer allocation",
                suggested_repair="clamp_emitter_spawn_rate",
            )
        elif "collision" in err_lower or "stuck" in err_lower or "nav" in err_lower:
            return FailureDiagnosis(
                failure_id="diag_nav_01",
                subsystem="Physics/Navigation",
                symptom="NAV_COLLISION_CLIP",
                probable_cause="Spawn volume intersects static mesh collision geometry",
                suggested_repair="nudge_spawn_position",
            )

        return FailureDiagnosis(
            failure_id="diag_gen_01",
            subsystem=subsystem or "General",
            symptom="GENERIC_RUNTIME_EXCEPTION",
            probable_cause=error_message,
            suggested_repair="restart_subsystem",
        )
