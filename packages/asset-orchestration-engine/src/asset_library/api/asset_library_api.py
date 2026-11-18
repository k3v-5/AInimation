from typing import Dict, Any, Optional, Tuple, List
from ..core.library_schema import (
    BuildIntent, ResolvedBuildSpec, ComponentDefinition, VariantDefinition, PresetDefinition
)
from ..components.component_registry import ComponentRegistry
from ..components.socket_system import SocketSystem
from ..templates.variant_registry import VariantRegistry
from ..templates.preset_registry import PresetRegistry
from ..resolution.template_resolver import TemplateResolver
from ..search.library_search_engine import LibrarySearchEngine
from ...correction_execution.providers.blender_provider import IBlenderProvider

class AssetLibraryAPI:
    """
    Asset Library & Template System API (AOE v18)
    
    Regla Fundamental:
    LA IA DEJA DE MODELAR. PASA A SER PLANNER, SELECTOR, DIRECTOR Y VALIDADOR.
    BuildIntent -> Resolution -> Sockets/Hierarchy -> Deterministic Build.
    """
    def __init__(self):
        self.comp_registry = ComponentRegistry()
        self.variant_registry = VariantRegistry()
        self.preset_registry = PresetRegistry()
        self.resolver = TemplateResolver(self.comp_registry, self.variant_registry, self.preset_registry)
        self.search_engine = LibrarySearchEngine(self.comp_registry, self.variant_registry, self.preset_registry)
        self.build_cache: Dict[str, str] = {} # manifest_hash -> asset_id

    def resolve_intent(self, intent: BuildIntent) -> Tuple[bool, Optional[ResolvedBuildSpec], str]:
        return self.resolver.resolve_intent(intent)

    def build_from_resolved_spec(
        self,
        asset_id: str,
        spec: ResolvedBuildSpec,
        provider: IBlenderProvider
    ) -> Tuple[bool, bool, str]: # (success, is_cache_hit, message)
        # 1. Comprobar Build Cache
        if spec.manifest_hash in self.build_cache:
            return True, True, f"Cache Hit: Manifest {spec.manifest_hash} already built as '{self.build_cache[spec.manifest_hash]}'."

        # 2. Validar Composición de Sockets
        ok_sock, msg_sock = SocketSystem.validate_composition(spec.components)
        if not ok_sock:
            return False, False, msg_sock

        # 3. Construir Asset en el Provider
        p = spec.resolved_parameters
        comps_dict = {
            "blade": {"dimensions": (p.get("blade_width", 0.05), p.get("blade_thickness", 0.02), p.get("blade_length", 0.90)), "material": spec.components["blade"].materials},
            "guard": {"dimensions": (p.get("guard_width", 0.18), 0.04, 0.04), "material": spec.components["guard"].materials},
            "grip": {"dimensions": (0.03, 0.03, p.get("handle_length", 0.22)), "material": spec.components["handle"].materials},
            "pommel": {"dimensions": (0.04, 0.04, 0.04), "material": spec.components["pommel"].materials}
        }
        provider.init_asset(asset_id, comps_dict)
        self.build_cache[spec.manifest_hash] = asset_id

        return True, False, f"Asset '{asset_id}' built successfully from variant '{spec.variant_id}'."

    def search_library(self, query: str) -> Dict[str, List[str]]:
        return self.search_engine.search(query)
