"""
ResolutionPipeline orchestrates the 8-stage transformation of raw specifications into resolved specifications.
UAF-81.1 Sections 46 to 50.
"""

from typing import Dict, Any, List, Optional
from ...core.specification.asset_specification import AssetSpecification
from ...core.diagnostics.errors import SpecificationError
from ...contracts.validator import ContractValidator
from ..parameters.unit_normalizer import UnitNormalizer
from ..archetypes.archetype_registry import ArchetypeRegistry
from ..constraints.constraint import AssetConstraint, ConstraintType, ConstraintCategory
from ..constraints.constraint_resolver import ConstraintResolver, ResolutionTraceEntry
from ..dependencies.dependency_graph import DependencyGraph
from .resolved_specification import ResolvedAssetSpecification


class ResolutionPipeline:
    """
    Compiler pipeline transforming user/intent specification into a fully resolved,
    validated, and normalized asset specification.
    """
    def __init__(self, archetype_registry: Optional[ArchetypeRegistry] = None):
        self.archetypes = archetype_registry or ArchetypeRegistry()

    def resolve(self, raw_spec: AssetSpecification) -> ResolvedAssetSpecification:
        # Stage 1: Schema Validation
        report = ContractValidator.validate_specification(raw_spec)
        if not report.is_valid:
            errors = [d.message for d in report.diagnostics]
            raise SpecificationError(
                f"Specification schema validation failed: {'; '.join(errors)}",
                details={"diagnostics": [d.to_dict() for d in report.diagnostics]},
            )

        resolved_parameters: Dict[str, Any] = dict(raw_spec.parameters)
        resolution_traces: List[ResolutionTraceEntry] = []

        # Stage 2: Normalization (physical units to meters)
        for k, v in list(resolved_parameters.items()):
            if isinstance(v, str) and any(unit in v for unit in ["cm", "mm", "km", "m", "in", "ft", "yd"]):
                try:
                    norm_val = UnitNormalizer.normalize_length(v)
                    resolved_parameters[k] = norm_val
                    resolution_traces.append(
                        ResolutionTraceEntry(
                            parameter=k,
                            requested_value=v,
                            resolved_value=norm_val,
                            applied_constraints=["unit_normalization"],
                            status="accepted",
                            rationale=f"Normalized '{v}' to {norm_val} meters.",
                        )
                    )
                except ValueError:
                    pass  # Non-dimension string, leave unchanged

        # Stage 3: Default Resolution from Archetype
        archetype_id = raw_spec.parameters.get("archetype")
        required_capabilities = []

        if archetype_id and self.archetypes.supports(archetype_id):
            archetype = self.archetypes.get(archetype_id)
            for default_key, default_val in archetype.default_parameters.items():
                if default_key not in resolved_parameters:
                    resolved_parameters[default_key] = default_val
                    resolution_traces.append(
                        ResolutionTraceEntry(
                            parameter=default_key,
                            requested_value=None,
                            resolved_value=default_val,
                            applied_constraints=["archetype_defaults"],
                            status="accepted",
                            rationale=f"Inherited default from archetype '{archetype_id}'.",
                        )
                    )
            for cap in archetype.required_capabilities:
                if cap not in required_capabilities:
                    required_capabilities.append(cap)

        # Stage 4: Reference Resolution
        # (References to sub-assets recorded in parameters)
        references = [str(v) for k, v in resolved_parameters.items() if k.endswith("_ref") or k.endswith("_asset")]

        # Stage 5: Dependency Resolution & Cycle Check
        dep_graph = DependencyGraph()
        all_deps = list(raw_spec.dependencies) + references
        for dep in all_deps:
            dep_graph.add_dependency(raw_spec.identity.asset_id, dep)

        # Validates no cycles exist
        dep_graph.validate_acyclic()

        # Stage 6: Constraint Resolution
        constraints_list = []
        for c_data in raw_spec.constraints.get("rules", []):
            if isinstance(c_data, dict):
                constraints_list.append(AssetConstraint.from_dict(c_data))

        resolved_parameters, conflict_report = ConstraintResolver.resolve(
            parameters=resolved_parameters,
            constraints=constraints_list,
        )

        for trace in conflict_report.traces:
            resolution_traces.append(trace)

        if conflict_report.has_conflicts:
            raise SpecificationError(
                f"Specification constraint conflicts detected: {'; '.join(conflict_report.reasons)}",
                details=conflict_report.to_dict(),
            )

        # Stage 7: Capability Extraction based on Fidelity / Complexity
        complexity = raw_spec.parameters.get("complexity", "C2")
        if complexity in ["C3", "C4", "C5"]:
            for cap in ["high_detail_surface", "advanced_topology"]:
                if cap not in required_capabilities:
                    required_capabilities.append(cap)

        if raw_spec.parameters.get("facial_fidelity") == "high":
            if "advanced_facial_generation" not in required_capabilities:
                required_capabilities.append("advanced_facial_generation")

        if raw_spec.parameters.get("clothing_complexity") == "high":
            if "cloth_geometry" not in required_capabilities:
                required_capabilities.append("cloth_geometry")

        # Stage 8: Resolved Specification
        return ResolvedAssetSpecification(
            original_specification=raw_spec,
            resolved_parameters=resolved_parameters,
            resolved_dependencies=all_deps,
            resolved_constraints=[c.to_dict() for c in constraints_list],
            required_capabilities=required_capabilities,
            effective_quality_profile=raw_spec.quality_profile,
            effective_target_profile=raw_spec.target,
            resolution_trace=[t.to_dict() for t in resolution_traces],
        )
