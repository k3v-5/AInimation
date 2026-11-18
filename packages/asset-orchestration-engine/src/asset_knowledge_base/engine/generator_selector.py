from typing import Dict, Any, List, Optional
from ..core.knowledge_schema import GeneratorDefinitionKB
from ..registry.archetype_registry import ArchetypeRegistry

class GeneratorSelector:
    def __init__(self, registry: ArchetypeRegistry):
        self.registry = registry

    def select_generator_for_component(
        self,
        archetype_id: str,
        component_name: str,
        simulate_primary_failure: bool = False
    ) -> GeneratorDefinitionKB:
        archetype = self.registry.get_archetype(archetype_id)
        if component_name not in archetype.primary_generators:
            raise KeyError(f"No generator registered for component '{component_name}' in archetype '{archetype_id}'.")
        
        primary_id = archetype.primary_generators[component_name]
        primary_gen = self.registry.get_generator(primary_id)

        if not simulate_primary_failure:
            return primary_gen

        # Fallback si el primario falla o no está disponible
        if primary_gen.fallback_generator_id:
            fallback_gen = self.registry.get_generator(primary_gen.fallback_generator_id)
            return fallback_gen
        
        raise RuntimeError(f"Primary generator '{primary_id}' failed and no fallback is registered.")

    def rank_generators_for_archetype(self, archetype_id: str) -> List[Dict[str, Any]]:
        results = []
        for gid, gen in self.registry.generators.items():
            if archetype_id in gen.compatible_archetypes:
                # Score de ranking basado en confiabilidad y costo
                cost_weight = 1.0 if gen.cost == "LOW" else (0.8 if gen.cost == "MEDIUM" else 0.5)
                score = round(gen.reliability_score * cost_weight, 3)
                results.append({"generator_id": gid, "score": score, "reliability": gen.reliability_score, "cost": gen.cost})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
