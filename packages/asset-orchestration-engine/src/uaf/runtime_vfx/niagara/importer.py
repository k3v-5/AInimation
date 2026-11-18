"""
UAF-81.84.10: Unreal Engine 5 Niagara Asset Importer and Compatibility Auditing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .ir import VFXIREmitter, VFXIRModule, VFXIRRenderer, VFXIRSystem


@dataclass
class NiagaraCompatibilityReport:
    """Detailed audit report of Niagara asset import/export fidelity."""
    compatible_features: List[str] = field(default_factory=list)
    lossy_features: List[str] = field(default_factory=list)
    unsupported_features: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    source_hash: str = ""
    target_hash: str = ""

    @property
    def is_fully_compatible(self) -> bool:
        return len(self.unsupported_features) == 0 and len(self.errors) == 0


class NiagaraImporter:
    """Parses UE5 Niagara System representations back into UAF VFX IR with fidelity auditing."""

    @classmethod
    def import_from_niagara(cls, niagara_data: Dict[str, Any]) -> Tuple[VFXIRSystem, NiagaraCompatibilityReport]:
        report = NiagaraCompatibilityReport()
        report.source_hash = niagara_data.get("TargetHash", "")

        sys_data = niagara_data.get("NiagaraSystem", {})
        system_id = sys_data.get("SystemName", "ImportedNiagaraSystem")
        revision = sys_data.get("Revision", 1)
        parameters = sys_data.get("Parameters", {})

        ir_emitters: List[VFXIREmitter] = []

        for em_data in sys_data.get("Emitters", []):
            em_id = em_data.get("EmitterHandle", "Emitter")
            sim_target = "CPU" if em_data.get("SimTarget") == "CPUSim" else "GPU"
            max_cap = em_data.get("MaxParticles", 1000)

            # Check supported features
            report.compatible_features.append(f"Emitter:{em_id}")

            modules: List[VFXIRModule] = []
            for m_data in em_data.get("Modules", []):
                mod_name = m_data.get("ModuleName", "")
                stage = m_data.get("ExecutionStage", "Update")
                params = m_data.get("ModuleInputs", {})

                if "Unsupported" in mod_name or "CustomHLSL" in mod_name:
                    report.unsupported_features.append(f"Module:{mod_name}")
                    report.warnings.append(f"Module '{mod_name}' is not natively supported in UAF core.")
                else:
                    report.compatible_features.append(f"Module:{mod_name}")

                modules.append(VFXIRModule(module_name=mod_name, stage=stage, parameters=params))

            # Renderer
            rend_data = em_data.get("Renderer")
            renderer_ir = None
            if rend_data:
                r_class = rend_data.get("RendererClass", "")
                r_type = "Sprite"
                if "Mesh" in r_class:
                    r_type = "Mesh"
                elif "Ribbon" in r_class:
                    r_type = "Ribbon"
                elif "Light" in r_class:
                    r_type = "Light"
                    report.lossy_features.append("LightRenderer: approximated as point light")

                renderer_ir = VFXIRRenderer(
                    renderer_type=r_type,
                    settings=rend_data.get("Settings", {}),
                )
                report.compatible_features.append(f"Renderer:{r_type}")

            ir_emitters.append(
                VFXIREmitter(
                    emitter_id=em_id,
                    sim_target=sim_target,
                    spawn_mode="Rate",
                    max_capacity=max_cap,
                    modules=tuple(modules),
                    renderer=renderer_ir,
                )
            )

        ir_sys = VFXIRSystem(
            system_id=system_id,
            revision=revision,
            parameters=parameters,
            emitters=tuple(ir_emitters),
        )
        report.target_hash = ir_sys.compute_hash()
        return ir_sys, report
