from typing import Dict, Any, List, Optional
from ..core.intent_types import (
    RequirementType, RequirementPriority, RequirementSource,
    AmbiguitySeverity, AmbiguityCategory, ReferenceScopeType,
    TaskCriticality, MilestoneType, PreflightStatus
)
from ..core.intent_schema import (
    UserRequest, Requirement, ExclusionItem, AmbiguityItem,
    ClarificationRequest, ReferenceTargetMask, CompiledIntent,
    TaskGraphNode, TaskGraphDAG, ExecutionPlanStep, IntentDelta
)
from ..compiler.intent_parser import IntentParser
from ..graph.task_graph_builder import TaskGraphBuilder
from ..graph.graph_validator import GraphValidator
from ..graph.plan_compiler import PlanCompiler
from ..traceability.drift_detector import DriftDetector, IncrementalReplanner

class IntentCompilerAPI:
    """
    Intent Compiler & Task Graph Planner API (AOE v39)
    
    Regla Fundamental:
    LA IA NO PASA DIRECTAMENTE DE LENGUAJE NATURAL A ACCIONES EN BLENDER.
    EXTRAE REQUISITOS (Must-Have), EXCLUSIONES (Must-Not-Have), DETECTA AMBIGÜEDADES,
    COMPILA ESPECIFICACIONES FORMALES Y CONSTRUYE UN GRAFO ACÍCLICO DIRIGIDO (DAG)
    CON VALIDACIÓN EN TIEMPO DE COMPILACIÓN ANTES DE TOCAR EL MCP.
    """
    def __init__(self):
        self.default_capabilities = [
            "geometry_generation",
            "blender_mesh_creation",
            "component_placement",
            "material_assignment",
            "quality_validation"
        ]

    def compile_intent(self, raw_text: str, references: Optional[List[Dict]] = None, context: Optional[Dict] = None) -> CompiledIntent:
        req = UserRequest(
            request_id="REQ_DIRECT",
            raw_text=raw_text,
            references=references or [],
            context=context or {}
        )
        return IntentParser.parse_request(req)

    def build_task_graph(self, intent: CompiledIntent) -> TaskGraphDAG:
        return TaskGraphBuilder.build_dag(intent)

    def validate_graph(self, dag: TaskGraphDAG, intent: CompiledIntent, available_capabilities: Optional[List[str]] = None):
        caps = available_capabilities if available_capabilities is not None else self.default_capabilities
        GraphValidator.validate_graph(dag, caps, intent)

    def compile_plan(self, dag: TaskGraphDAG, intent: CompiledIntent) -> List[ExecutionPlanStep]:
        return PlanCompiler.compile_plan(dag, intent)

    def detect_intent_drift(self, intent: CompiledIntent, steps: List[ExecutionPlanStep]):
        DriftDetector.detect_drift(intent, steps)

    def replan_delta(self, target: str, property_name: str, old_val: Any, new_val: Any) -> IntentDelta:
        delta = IntentDelta(
            delta_id="DELTA_01",
            target=target,
            property_name=property_name,
            old_value=old_val,
            new_value=new_val
        )
        delta.affected_subgraph = IncrementalReplanner.calculate_affected_subgraph(delta)
        return delta
