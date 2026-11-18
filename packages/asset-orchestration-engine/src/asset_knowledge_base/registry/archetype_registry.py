import copy
from typing import Dict, Any, List, Optional
from ..core.knowledge_types import (
    ArchetypeCategory, ComponentNecessity, DependencyType,
    StyleEra, DesignRuleSeverity
)
from ..core.knowledge_schema import (
    ComponentSlot, DesignRule, ArchetypeDefinition, DesignTemplate,
    GeneratorDefinitionKB, FailureKnowledge
)

class ArchetypeRegistry:
    def __init__(self):
        self.archetypes: Dict[str, ArchetypeDefinition] = {}
        self.generators: Dict[str, GeneratorDefinitionKB] = {}
        self.failures: Dict[str, FailureKnowledge] = {}
        self._register_default_data()

    def _register_default_data(self):
        # 1. Generators
        self.generators["GEN_FOUNDATION_01"] = GeneratorDefinitionKB(
            generator_id="GEN_FOUNDATION_01", version="1.2.0",
            capabilities=["box_mesh", "slab_generation"], cost="LOW", reliability_score=0.99,
            compatible_archetypes=["MEDIEVAL_HOUSE", "WATCHTOWER", "NORDIC_CABIN"]
        )
        self.generators["GEN_WALLS_MODULAR"] = GeneratorDefinitionKB(
            generator_id="GEN_WALLS_MODULAR", version="2.0.0",
            capabilities=["boolean_openings", "modular_segments"], cost="MEDIUM", reliability_score=0.97,
            fallback_generator_id="GEN_WALLS_BASIC", compatible_archetypes=["MEDIEVAL_HOUSE", "WATCHTOWER"]
        )
        self.generators["GEN_WALLS_BASIC"] = GeneratorDefinitionKB(
            generator_id="GEN_WALLS_BASIC", version="1.0.0",
            capabilities=["box_mesh"], cost="LOW", reliability_score=0.99,
            compatible_archetypes=["MEDIEVAL_HOUSE", "WATCHTOWER"]
        )
        self.generators["GEN_ROOF_PARAMETRIC"] = GeneratorDefinitionKB(
            generator_id="GEN_ROOF_PARAMETRIC", version="2.1.0",
            capabilities=["gable", "hip", "mansard", "overhang"], cost="MEDIUM", reliability_score=0.96,
            fallback_generator_id="GEN_ROOF_PRIMITIVE", compatible_archetypes=["MEDIEVAL_HOUSE", "NORDIC_CABIN"]
        )
        self.generators["GEN_ROOF_PRIMITIVE"] = GeneratorDefinitionKB(
            generator_id="GEN_ROOF_PRIMITIVE", version="1.0.0",
            capabilities=["prism_mesh"], cost="LOW", reliability_score=0.99,
            compatible_archetypes=["MEDIEVAL_HOUSE"]
        )
        self.generators["GEN_OPENINGS_V1"] = GeneratorDefinitionKB(
            generator_id="GEN_OPENINGS_V1", version="1.5.0",
            capabilities=["door_frame", "window_frame", "subdivisions"], cost="LOW", reliability_score=0.98,
            compatible_archetypes=["MEDIEVAL_HOUSE", "WATCHTOWER", "NORDIC_CABIN"]
        )

        # 2. Medieval House Archetype
        self.archetypes["MEDIEVAL_HOUSE"] = ArchetypeDefinition(
            archetype_id="MEDIEVAL_HOUSE",
            name="Medieval Rural / Town House",
            category=ArchetypeCategory.RESIDENTIAL,
            style_era=StyleEra.MEDIEVAL,
            component_slots={
                "foundation": ComponentSlot("foundation", ComponentNecessity.MANDATORY, "foundation", min_count=1, max_count=1, children=["walls"]),
                "walls": ComponentSlot("walls", ComponentNecessity.MANDATORY, "walls", parent_component="foundation", min_count=1, max_count=1, children=["roof", "door", "windows"]),
                "roof": ComponentSlot("roof", ComponentNecessity.MANDATORY, "roof", parent_component="walls", min_count=1, max_count=1, allowed_types=["GABLE", "HIP", "MANSARD"], children=["chimney"]),
                "door": ComponentSlot("door", ComponentNecessity.MANDATORY, "doors", parent_component="walls", min_count=1, max_count=2, attachment_target="walls"),
                "windows": ComponentSlot("windows", ComponentNecessity.OPTIONAL, "windows", parent_component="walls", min_count=0, max_count=8, attachment_target="walls"),
                "chimney": ComponentSlot("chimney", ComponentNecessity.OPTIONAL, "chimney", parent_component="roof", min_count=0, max_count=2, attachment_target="roof")
            },
            default_parameters={
                "width": 8.0,
                "depth": 6.0,
                "wall_height": 3.0,
                "roof_height": 1.8,
                "roof_pitch": 35.0,
                "window_count": 4,
                "door_count": 1
            },
            parameter_expressions={
                "roof_width": "house_width + 0.40",
                "roof_depth": "house_depth + 0.40"
            },
            design_rules=[
                DesignRule("RULE_ROOF_PITCH_MIN", "Minimum Roof Pitch", DesignRuleSeverity.ERROR, "Roof pitch must be >= 25 degrees for tile/thatch drainage.", condition_code="roof_pitch >= 25.0"),
                DesignRule("RULE_CHIMNEY_ATTACHMENT", "Chimney Roof Attachment", DesignRuleSeverity.ERROR, "Chimney requires a roof component to attach.", condition_code="has_roof_for_chimney"),
                DesignRule("RULE_MAX_WINDOWS", "Max Windows per Wall Area", DesignRuleSeverity.WARNING, "Window count must not exceed max slot capacity.", condition_code="window_count <= 8")
            ],
            primary_generators={
                "foundation": "GEN_FOUNDATION_01",
                "walls": "GEN_WALLS_MODULAR",
                "roof": "GEN_ROOF_PARAMETRIC",
                "door": "GEN_OPENINGS_V1",
                "windows": "GEN_OPENINGS_V1"
            }
        )

        # 3. Watchtower
        self.archetypes["WATCHTOWER"] = ArchetypeDefinition(
            archetype_id="WATCHTOWER",
            name="Fortified Medieval Watchtower",
            category=ArchetypeCategory.MILITARY,
            style_era=StyleEra.MEDIEVAL,
            component_slots={
                "foundation": ComponentSlot("foundation", ComponentNecessity.MANDATORY, "foundation", min_count=1, max_count=1, children=["walls"]),
                "walls": ComponentSlot("walls", ComponentNecessity.MANDATORY, "walls", parent_component="foundation", min_count=1, max_count=1, children=["crenellations", "door"]),
                "crenellations": ComponentSlot("crenellations", ComponentNecessity.MANDATORY, "crenellations", parent_component="walls", min_count=1, max_count=1),
                "door": ComponentSlot("door", ComponentNecessity.MANDATORY, "doors", parent_component="walls", min_count=1, max_count=1)
            },
            default_parameters={
                "width": 4.0,
                "depth": 4.0,
                "wall_height": 12.0,
                "door_count": 1
            },
            primary_generators={
                "foundation": "GEN_FOUNDATION_01",
                "walls": "GEN_WALLS_MODULAR",
                "crenellations": "GEN_WALLS_BASIC",
                "door": "GEN_OPENINGS_V1"
            }
        )

        # 4. Nordic Cabin
        self.archetypes["NORDIC_CABIN"] = ArchetypeDefinition(
            archetype_id="NORDIC_CABIN",
            name="Nordic Timber Cabin",
            category=ArchetypeCategory.RESIDENTIAL,
            style_era=StyleEra.NORDIC,
            component_slots={
                "foundation": ComponentSlot("foundation", ComponentNecessity.MANDATORY, "foundation", min_count=1, max_count=1, children=["walls"]),
                "walls": ComponentSlot("walls", ComponentNecessity.MANDATORY, "walls", parent_component="foundation", min_count=1, max_count=1, children=["roof", "door"]),
                "roof": ComponentSlot("roof", ComponentNecessity.MANDATORY, "roof", parent_component="walls", min_count=1, max_count=1, allowed_types=["GABLE"]),
                "door": ComponentSlot("door", ComponentNecessity.MANDATORY, "doors", parent_component="walls", min_count=1, max_count=1)
            },
            default_parameters={
                "width": 7.0,
                "depth": 5.0,
                "wall_height": 2.6,
                "roof_height": 2.2,
                "roof_pitch": 45.0
            },
            primary_generators={
                "foundation": "GEN_FOUNDATION_01",
                "walls": "GEN_WALLS_BASIC",
                "roof": "GEN_ROOF_PARAMETRIC",
                "door": "GEN_OPENINGS_V1"
            }
        )

        # 5. Known Failures
        self.failures["FAIL_ROOF_TOO_HIGH"] = FailureKnowledge(
            failure_id="FAIL_ROOF_TOO_HIGH",
            category="GEOMETRIC_PROPORTION",
            symptoms=["silhouette mismatch", "excessive vertical mass", "roof ratio > 0.35"],
            causes=["roof_height parameter set too high", "steep pitch with excessive width"],
            candidate_corrections=["decrease roof_height by 15-20%", "reduce roof_pitch"]
        )

    def get_archetype(self, archetype_id: str) -> ArchetypeDefinition:
        if archetype_id not in self.archetypes:
            raise KeyError(f"Archetype '{archetype_id}' not found in Knowledge Base.")
        return copy.deepcopy(self.archetypes[archetype_id])

    def query_by_style(self, style: StyleEra) -> List[ArchetypeDefinition]:
        return [copy.deepcopy(arch) for arch in self.archetypes.values() if arch.style_era == style]

    def get_generator(self, generator_id: str) -> GeneratorDefinitionKB:
        if generator_id not in self.generators:
            raise KeyError(f"Generator '{generator_id}' not registered in Knowledge Base.")
        return copy.deepcopy(self.generators[generator_id])

class DesignTemplateLibrary:
    def __init__(self):
        self.templates: Dict[str, DesignTemplate] = {}
        self._register_default_templates()

    def _register_default_templates(self):
        self.templates["BASE_BUILDING"] = DesignTemplate(
            template_id="BASE_BUILDING",
            archetype_id="MEDIEVAL_HOUSE",
            style_era=StyleEra.MEDIEVAL,
            parameter_overrides={"width": 8.0, "depth": 6.0, "wall_height": 3.0}
        )

        self.templates["RESIDENTIAL_HOUSE"] = DesignTemplate(
            template_id="RESIDENTIAL_HOUSE",
            parent_template="BASE_BUILDING",
            archetype_id="MEDIEVAL_HOUSE",
            style_era=StyleEra.MEDIEVAL,
            parameter_overrides={"roof_height": 1.8, "window_count": 4, "door_count": 1}
        )

        self.templates["MEDIEVAL_RURAL_HOUSE"] = DesignTemplate(
            template_id="MEDIEVAL_RURAL_HOUSE",
            parent_template="RESIDENTIAL_HOUSE",
            archetype_id="MEDIEVAL_HOUSE",
            style_era=StyleEra.MEDIEVAL,
            parameter_overrides={"wall_material": "STONE", "roof_material": "WOOD", "roof_pitch": 38.0},
            materials={"walls": "STONE_ROUGH", "roof": "TIMBER_SHINGLES"}
        )

    def get_resolved_template(self, template_id: str) -> DesignTemplate:
        if template_id not in self.templates:
            raise KeyError(f"Template '{template_id}' not found in Design Library.")
        
        chain = []
        curr = self.templates[template_id]
        while curr:
            chain.append(curr)
            curr = self.templates.get(curr.parent_template) if curr.parent_template else None

        merged_params: Dict[str, Any] = {}
        merged_mats: Dict[str, str] = {}
        for tmpl in reversed(chain):
            merged_params.update(tmpl.parameter_overrides)
            merged_mats.update(tmpl.materials)

        leaf = self.templates[template_id]
        return DesignTemplate(
            template_id=leaf.template_id,
            parent_template=leaf.parent_template,
            archetype_id=leaf.archetype_id,
            style_era=leaf.style_era,
            parameter_overrides=merged_params,
            materials=merged_mats
        )
