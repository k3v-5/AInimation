"""
UAF-81.84.10: UAF VFX IR to Unreal Engine 5 Niagara Exporter.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

from .ir import VFXIRSystem


class NiagaraExporter:
    """Translates UAF VFX Intermediate Representation to Unreal Engine 5 Niagara asset schemas."""

    @classmethod
    def export_to_niagara(cls, ir_system: VFXIRSystem, ue_version: str = "5.4") -> Dict[str, Any]:
        source_hash = ir_system.compute_hash()

        niagara_emitters = []
        for em in ir_system.emitters:
            modules_data = []
            for m in em.modules:
                modules_data.append({
                    "ModuleName": m.module_name,
                    "ExecutionStage": m.stage,
                    "ModuleInputs": m.parameters,
                })

            renderer_data = None
            if em.renderer:
                renderer_data = {
                    "RendererClass": f"/Script/Niagara.Niagara{em.renderer.renderer_type.capitalize()}RendererProperties",
                    "Settings": em.renderer.settings,
                }

            niagara_emitters.append({
                "EmitterHandle": em.emitter_id,
                "SimTarget": "CPUSim" if em.sim_target == "CPU" else "GPUComputeSim",
                "MaxParticles": em.max_capacity,
                "Modules": modules_data,
                "Renderer": renderer_data,
            })

        manifest = {
            "SchemaVersion": "1.0.0",
            "TargetEngine": f"UnrealEngine_{ue_version}",
            "UAF_VFX_System": "81.84.10",
            "NiagaraSystem": {
                "SystemName": ir_system.system_id,
                "Revision": ir_system.revision,
                "Parameters": ir_system.parameters,
                "Emitters": niagara_emitters,
            },
            "SourceIRHash": source_hash,
        }

        raw = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
        manifest["TargetHash"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return manifest
