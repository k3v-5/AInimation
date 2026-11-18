from typing import Dict, Any, List, Optional
from ..core.prompt_types import (
    IntentType, AssetClassType, ProvenanceType,
    RequirementHardness, ConflictSeverity, CompilationStatus
)
from ..core.prompt_schema import (
    CompiledSpecification, CompilationResult, ConversationContext,
    ClarificationRequest, RequirementConflict
)
from ..compiler.specification_compiler import SpecificationCompiler

class PromptCompilerAPI:
    """
    Prompt Compiler & Intent-to-Specification Engine API (AOE v51)
    
    Regla Fundamental:
    EL COMPILADOR NO GENERA GEOMETRÍA NI LLAMA A BLENDER O MCP.
    TRANSFORMA LENGUAJE NATURAL EN UNA ESPECIFICACIÓN ESTRUCTURADA, DETERMINISTA,
    TRAZABLE CON PROVENANCE, CON EXPANSIÓN DERIVADA DE GAMEPLAY Y DETECCIÓN ESTRICTA DE CONTRADICCIONES.
    """
    def __init__(self):
        pass

    def compile_intent(
        self,
        prompt_text: str,
        context: Optional[ConversationContext] = None
    ) -> CompilationResult:
        return SpecificationCompiler.compile_prompt(prompt_text, context)
