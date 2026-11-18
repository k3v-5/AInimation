from typing import Dict, Any, List, Optional
from ..core.knowledge_schema import ArchetypeDefinition, KnowledgeContextSummary
from ..registry.archetype_registry import ArchetypeRegistry

class KnowledgeQueryEngine:
    def __init__(self, registry: ArchetypeRegistry):
        self.registry = registry

    def hybrid_search(self, query: str) -> List[ArchetypeDefinition]:
        query_clean = query.strip().upper()
        # 1. Exact ID match
        if query_clean in self.registry.archetypes:
            return [self.registry.get_archetype(query_clean)]

        # 2. Keyword / Semantic Search
        results = []
        tokens = query_clean.split()
        for arch_id, arch in self.registry.archetypes.items():
            arch_text = f"{arch.name} {arch.category.value} {arch.style_era.value} {' '.join(arch.component_slots.keys())}".upper()
            if any(token in arch_text for token in tokens):
                results.append(self.registry.get_archetype(arch_id))

        return results

class KnowledgeContextBuilder:
    @staticmethod
    def build_focused_context(
        archetype: ArchetypeDefinition,
        target_component: Optional[str] = None
    ) -> KnowledgeContextSummary:
        relevant_comps = [target_component] if target_component else list(archetype.component_slots.keys())
        active_params = dict(archetype.default_parameters)
        if target_component and target_component in ["roof"]:
            # Filtrar solo parámetros relevantes al componente
            active_params = {k: v for k, v in active_params.items() if "roof" in k or "width" in k or "depth" in k}

        rec_gens = {
            c: archetype.primary_generators.get(c, "GEN_DEFAULT")
            for c in relevant_comps if c in archetype.primary_generators
        }

        known_fails = ["FAIL_ROOF_TOO_HIGH"] if "roof" in relevant_comps else []

        return KnowledgeContextSummary(
            archetype_id=archetype.archetype_id,
            relevant_components=relevant_comps,
            active_parameters=active_params,
            recommended_generators=rec_gens,
            known_failures=known_fails,
            estimated_context_tokens=180 if target_component else 280
        )
