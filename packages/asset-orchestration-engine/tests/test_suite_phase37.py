import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ai_critic_self_correction import (
    AICriticAPI, CriticStatus, ModificationLevel, CorrectionOperationType,
    CandidateBranch, CorrectionPlan, BudgetStatus
)
from src.visual_reference_similarity import DifferenceRecord, DifferenceType, DifferenceSeverity

class TestAICriticSelfCorrectionPhase37(unittest.TestCase):
    def setUp(self):
        self.api = AICriticAPI()

    def test_01_acceptance_1_roof_height_diagnosis(self):
        """Acceptance Test 1: Techo demasiado alto diagnostica escala de techo a nivel PROPERTY."""
        diff = DifferenceRecord(target="HOUSE.ROOF_PROPORTION", diff_type=DifferenceType.WRONG_SIZE, severity=DifferenceSeverity.HIGH, expected=0.30, actual=0.50, metric="roof_to_body_ratio")
        dec = self.api.diagnose_and_plan("HOUSE_001", [diff], current_score=0.72)
        self.assertEqual(dec.status, CriticStatus.CORRECT)
        self.assertEqual(dec.plan.operations[0].operation_type, CorrectionOperationType.SCALE_COMPONENT)
        self.assertEqual(dec.plan.operations[0].level, ModificationLevel.PROPERTY)

    def test_02_acceptance_2_wrong_roof_type_rebuild(self):
        """Acceptance Test 2: Techo de tipo incorrecto genera decisión REBUILD_COMPONENT."""
        diff = DifferenceRecord(target="HOUSE.ROOF", diff_type=DifferenceType.WRONG_SHAPE, severity=DifferenceSeverity.CRITICAL, expected="GABLE", actual="FLAT", metric="roof_shape")
        dec = self.api.diagnose_and_plan("HOUSE_001", [diff], current_score=0.65)
        self.assertEqual(dec.status, CriticStatus.REBUILD_COMPONENT)
        self.assertEqual(dec.plan.operations[0].operation_type, CorrectionOperationType.REBUILD_COMPONENT)

    def test_03_acceptance_3_door_width_property_correction(self):
        """Acceptance Test 3: Ancho de puerta incorrecto genera corrección a nivel PROPERTY."""
        diff = DifferenceRecord(target="HOUSE.DOOR.MAIN", diff_type=DifferenceType.WRONG_SIZE, severity=DifferenceSeverity.MEDIUM, expected=0.90, actual=1.20, metric="width")
        dec = self.api.diagnose_and_plan("HOUSE_001", [diff], current_score=0.85)
        self.assertEqual(dec.status, CriticStatus.CORRECT)
        self.assertEqual(dec.plan.operations[0].level, ModificationLevel.PROPERTY)

    def test_04_acceptance_4_rollback_on_regression(self):
        """Acceptance Test 4: Rollback restaura el mejor estado conocido (BEST_STATE)."""
        self.api.rollback_ctrl.save_checkpoint("CHK_01", score=0.88, asset_state={"roof": "v1"})
        self.api.rollback_ctrl.save_checkpoint("CHK_02", score=0.75, asset_state={"roof": "v2_regressed"})
        best = self.api.rollback_ctrl.rollback_to_best()
        self.assertEqual(best.score, 0.88)
        self.assertEqual(best.asset_state["roof"], "v1")

    def test_05_acceptance_5_budget_exceeded(self):
        """Acceptance Test 5: Superar el límite de iteraciones produce BUDGET_EXCEEDED."""
        for i in range(5):
            self.api.iteration_ctrl.record_iteration(0.70 + i*0.01)
        self.assertEqual(self.api.iteration_ctrl.check_budget(), BudgetStatus.BUDGET_EXCEEDED)

    def test_06_acceptance_6_oscillation_detection(self):
        """Acceptance Test 6: Correcciones alternantes activan detección de oscilación."""
        for s in [0.80, 0.84, 0.79, 0.83]:
            self.api.iteration_ctrl.record_iteration(s)
        self.assertTrue(self.api.iteration_ctrl.is_oscillating())

    def test_07_acceptance_7_plateau_detection(self):
        """Acceptance Test 7: Puntuaciones estancadas activan detección de meseta (PLATEAU)."""
        for s in [0.81, 0.815, 0.818, 0.812]:
            self.api.iteration_ctrl.record_iteration(s)
        self.assertTrue(self.api.iteration_ctrl.is_plateau(patience=3))

    def test_08_acceptance_8_critical_constraint_conflict_blocked(self):
        """Acceptance Test 8: Intento de modificar propiedad bloqueada resulta en BLOCKED."""
        diff = DifferenceRecord(target="HOUSE.ROOF", diff_type=DifferenceType.WRONG_SHAPE, severity=DifferenceSeverity.CRITICAL, expected="GABLE", actual="FLAT", metric="roof_shape")
        dec = self.api.diagnose_and_plan("HOUSE_001", [diff], current_score=0.60, locked_constraints=["roof"])
        self.assertEqual(dec.status, CriticStatus.BLOCKED)
        self.assertIn("CRITICAL_CONSTRAINT_VIOLATION", dec.stop_reason)

    def test_09_acceptance_9_tool_timeout_handling(self):
        """Acceptance Test 9: Timeout en MCP se clasifica como error recuperable (RETRY_WITH_BACKOFF)."""
        res = self.api.handle_tool_failure("MCP_TIMEOUT_ERROR")
        self.assertEqual(res, "RETRY_WITH_BACKOFF")

    def test_10_acceptance_10_candidate_branch_selection(self):
        """Acceptance Test 10: Selecciona la rama de candidato con mayor puntuación predicha."""
        p1 = CorrectionPlan(plan_id="P1", target_asset="H1")
        p2 = CorrectionPlan(plan_id="P2", target_asset="H1")
        c1 = CandidateBranch(branch_id="B1", plan=p1, predicted_score=0.88)
        c2 = CandidateBranch(branch_id="B2", plan=p2, predicted_score=0.94)
        best = self.api.iteration_ctrl.select_best_candidate([c1, c2])
        self.assertEqual(best.branch_id, "B2")

    def test_11_acceptance_11_root_cause_symptom_grouping(self):
        """Acceptance Test 11: Múltiples síntomas de tejado se agrupan en una única causa raíz."""
        d1 = DifferenceRecord(target="HOUSE.ROOF_HEIGHT", diff_type=DifferenceType.WRONG_SIZE, severity=DifferenceSeverity.HIGH, expected=0.30, actual=0.50, metric="roof_height")
        d2 = DifferenceRecord(target="HOUSE.ROOF_CHIMNEY", diff_type=DifferenceType.WRONG_POSITION, severity=DifferenceSeverity.MEDIUM, expected="CENTER", actual="EDGE", metric="chimney_pos")
        dec = self.api.diagnose_and_plan("HOUSE_001", [d1, d2], current_score=0.70)
        self.assertEqual(len(dec.diagnosis), 1)
        self.assertEqual(dec.diagnosis[0].cause_id, "RC_ROOF_GEOMETRY")

    def test_12_acceptance_12_low_confidence_human_review(self):
        """Acceptance Test 12: Diagnóstico con baja confianza (<0.60) deriva a HUMAN_REVIEW."""
        d1 = DifferenceRecord(target="HOUSE.ROOF", diff_type=DifferenceType.WRONG_SHAPE, severity=DifferenceSeverity.HIGH, expected="GABLE", actual="HIP", metric="roof_shape")
        dec = self.api.diagnose_and_plan("HOUSE_001", [d1], current_score=0.70, confidence=0.45)
        self.assertEqual(dec.status, CriticStatus.HUMAN_REVIEW)
        self.assertEqual(dec.next_action, "REQUEST_HUMAN_FEEDBACK")

    def test_13_acceptance_13_deadlock_detection(self):
        """Acceptance Test 13: Sin correcciones ejecutables y bajo score genera DEADLOCK."""
        dec = self.api.diagnose_and_plan("HOUSE_001", [], current_score=0.60)
        self.assertEqual(dec.status, CriticStatus.DEADLOCK)

    def test_14_acceptance_14_preservation_contract_protection(self):
        """Acceptance Test 14: Plan de corrección incluye contrato de preservación de propiedades no afectadas."""
        diff = DifferenceRecord(target="HOUSE.ROOF", diff_type=DifferenceType.WRONG_SIZE, severity=DifferenceSeverity.HIGH, expected=0.30, actual=0.50, metric="roof_height")
        dec = self.api.diagnose_and_plan("HOUSE_001", [diff], current_score=0.75)
        self.assertIn("dimensions.footprint", dec.plan.preservation_contract.preserve_properties)

    def test_15_acceptance_15_critic_strategy_memory(self):
        """Acceptance Test 15: CriticMemory recuerda estrategias fallidas para no repetirlas."""
        self.api.memory.record_failure("STRATEGY_REBUILD_ROOF_FLAT")
        self.assertTrue(self.api.memory.is_failed_strategy("STRATEGY_REBUILD_ROOF_FLAT"))

    def test_16_acceptance_16_pass_on_high_score(self):
        """Acceptance Test 16: Activo con score >= 0.90 y sin fallos críticos emite estado PASS."""
        dec = self.api.diagnose_and_plan("HOUSE_001", [], current_score=0.95)
        self.assertEqual(dec.status, CriticStatus.PASS)
        self.assertEqual(dec.next_action, "DONE")

if __name__ == "__main__":
    unittest.main()
