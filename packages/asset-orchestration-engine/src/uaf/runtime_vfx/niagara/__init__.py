"""
UAF-81.84: Niagara Bridge layer exports.
"""

from .compiler import VFXIRCompiler
from .exporter import NiagaraExporter
from .golden_assets import GoldenVFXFactory
from .importer import NiagaraCompatibilityReport, NiagaraImporter
from .ir import VFXIREmitter, VFXIRModule, VFXIRRenderer, VFXIRSystem

__all__ = [
    "GoldenVFXFactory",
    "NiagaraCompatibilityReport",
    "NiagaraExporter",
    "NiagaraImporter",
    "VFXIRCompiler",
    "VFXIREmitter",
    "VFXIRModule",
    "VFXIRRenderer",
    "VFXIRSystem",
]
