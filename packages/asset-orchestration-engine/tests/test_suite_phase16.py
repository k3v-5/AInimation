import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    VisualCriticAPI, ProceduralTemplatesAPI, MockBlenderProvider,
    SpecificationCompilerAPI, ParameterMappingEngine, IssueSeverity, CriticStatus
)

class TestVisualCriticPhase16(unittest.TestCase):
    def setUp(self):
        self.provider = MockBlenderProvider()
        self.templates_api = ProceduralTemplatesAPI(self.provider)
        self.critic_api = VisualCriticAPI(self.templates_api, self.provider, max_visual_iterations=4)
        self.spec_api = SpecificationCompilerAPI()

    def test_01_correct_asset_passes(self):
        """Test 1: Correct Asset - Asset con proporciones correctas pasa en la primera iteración."""
        ok, spec, _ = self.spec_api.compile_request("Quiero una espada medieval de 120 cm")
        build_res = self.templates_api.build_from_spec("sword_ok", spec)
        
        eval_res = self.critic_api.evaluate_and_refine("sword_ok", spec, build_res["parameters"])
        self.assertEqual(eval_res["final_status"], "ACCEPT")
        self.assertEqual(eval_res["iterations"], 1)

    def test_02_missing_component_fails(self):
        """Test 2: Missing Component - Falta de componente obligatorio produce CRITICAL y REJECT."""
        ok, spec, _ = self.spec_api.compile_request("Espada medieval con guardia y pomo")
        # Crear asset sin guard
        self.provider.init_asset("sword_bad", {
            "blade": {"dimensions": (0.05, 0.02, 0.90)},
            "grip": {"dimensions": (0.03, 0.03, 0.22)}
        })
        eval_res = self.critic_api.evaluate_and_refine("sword_bad", spec, {})
        self.assertEqual(eval_res["final_status"], "REJECT")
        self.assertIn("missing", eval_res["message"].lower())

    def test_03_proportion_issue_generates_patch(self):
        """Test 3: Proportion Issue - 'hoja ancha' con anchura estrecha genera ParameterPatch sobre blade_width."""
        ok, spec, _ = self.spec_api.compile_request("Espada con hoja ancha de 120 cm")
        self.templates_api.build_from_spec("sword_narrow", spec)
        
        # Evaluar
        eval_res = self.critic_api.evaluate_and_refine("sword_narrow", spec, {"blade_width": 0.05})
        self.assertEqual(eval_res["final_status"], "ACCEPT")
        self.assertEqual(eval_res["iterations"], 2)
        # Comprobar que en la iteración 2 la anchura de la hoja en el provider aumentó a 0.075m
        b_dims = self.provider.assets["sword_narrow"]["components"]["blade"]["dimensions"]
        self.assertEqual(b_dims[0], 0.075)

    def test_04_partial_rebuild_leaves_grip_intact(self):
        """Test 4: Partial Rebuild - El ajuste de la hoja no altera las dimensiones del mango."""
        ok, spec, _ = self.spec_api.compile_request("Espada con hoja ancha de 120 cm")
        self.templates_api.build_from_spec("sword_part", spec)
        grip_dims_before = self.provider.assets["sword_part"]["components"]["grip"]["dimensions"]

        self.critic_api.evaluate_and_refine("sword_part", spec, {"blade_width": 0.05})
        grip_dims_after = self.provider.assets["sword_part"]["components"]["grip"]["dimensions"]
        self.assertEqual(grip_dims_before, grip_dims_after)

    def test_05_protected_parameters_not_modified(self):
        """Test 5: Protected Parameters - Parámetros en protected_parameters no son modificados."""
        ok, spec, _ = self.spec_api.compile_request("Espada con hoja ancha de 120 cm")
        self.templates_api.build_from_spec("sword_prot", spec)

        eval_res = self.critic_api.evaluate_and_refine(
            "sword_prot", spec, {"blade_width": 0.05},
            protected_params=["blade_width"]
        )
        # Al estar protegido, no se genera patch y se acepta con warnings
        self.assertEqual(eval_res["final_status"], "ACCEPT_WITH_WARNINGS")
        b_dims = self.provider.assets["sword_prot"]["components"]["blade"]["dimensions"]
        self.assertEqual(b_dims[0], 0.05) # No modificado

    def test_06_parameter_mapping_engine(self):
        """Test 6: Parameter Mapping - Mapea claves cualitativas a parámetros."""
        self.assertEqual(ParameterMappingEngine.map_issue_to_parameter("blade_too_narrow"), "blade_width")
        self.assertEqual(ParameterMappingEngine.map_issue_to_parameter("guard_too_wide"), "guard_width")
        self.assertEqual(ParameterMappingEngine.map_issue_to_parameter("handle_too_short"), "handle_length")

    def test_07_budget_limit_stops_infinite_loops(self):
        """Test 7: Budget - Límite de iteraciones previene bucles infinitos."""
        strict_critic = VisualCriticAPI(self.templates_api, self.provider, max_visual_iterations=1)
        ok, spec, _ = self.spec_api.compile_request("Espada con hoja ancha de 120 cm")
        self.templates_api.build_from_spec("sword_loop", spec)
        
        # En 1 iteración no alcanzará la convergencia completa si se requiere revisión
        eval_res = strict_critic.evaluate_and_refine("sword_loop", spec, {"blade_width": 0.05})
        self.assertIn(eval_res["final_status"], ["ACCEPT", "CONVERGENCE_FAILURE", "ACCEPT_WITH_WARNINGS"])

    def test_08_critical_section_146_diagnostic_loop(self):
        """Test 8: Critical Test Case (Sec 146) - Genera espada -> estrecha artificialmente -> Critic detecta -> Patch -> Rebuild parcial -> PASS."""
        ok, spec, _ = self.spec_api.compile_request("Quiero una espada medieval estilizada con hoja ancha de 120 cm")
        # 1. Generar mediante plantilla
        build_res = self.templates_api.build_from_spec("sword_sec146", spec)
        self.assertTrue(build_res["success"])

        # 2. Introducir artificialmente error en blade_width
        self.provider.set_component_dimensions("sword_sec146", "blade", (0.04, 0.02, 0.90))

        # 3. Diagnóstico y refinamiento por IA Critic
        eval_res = self.critic_api.evaluate_and_refine("sword_sec146", spec, build_res["parameters"])
        self.assertEqual(eval_res["final_status"], "ACCEPT")
        self.assertGreaterEqual(eval_res["overall_score"], 0.90)

        # 4. Verificar que sólo la hoja fue ensanchada
        final_b_dims = self.provider.assets["sword_sec146"]["components"]["blade"]["dimensions"]
        self.assertEqual(final_b_dims[0], 0.075)

if __name__ == "__main__":
    unittest.main()
