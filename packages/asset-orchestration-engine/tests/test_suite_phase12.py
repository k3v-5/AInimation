import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    AssetMemoryAPI, FailureCategory, FailureTypeRegistry, SimilarityEngine
)

class TestAssetMemoryPhase12(unittest.TestCase):
    def setUp(self):
        self.mem = AssetMemoryAPI(":memory:")

    def tearDown(self):
        self.mem.store.close()

    def test_01_store_failure_and_strategy(self):
        """Test 1: Store and Retrieve - Almacena fallo y estrategia en SQLite y los recupera."""
        fail = self.mem.record_failure("sword_01", "SWORD", "BLADE", "BLADE_TOO_SHORT", 0.50, 0.72)
        strat = self.mem.register_strategy("strat_scale_blade", "BLADE_TOO_SHORT", "SWORD", "BLADE", "SET_DIMENSIONS", {"length": 0.72}, confidence=0.70)
        
        stored = self.mem.store.get_strategy("strat_scale_blade")
        self.assertIsNotNone(stored)
        self.assertEqual(stored.failure_type, "BLADE_TOO_SHORT")
        self.assertEqual(stored.confidence, 0.70)

    def test_02_strategy_retrieval_by_failure(self):
        """Test 2: Retrieval - Consulta por BLADE_TOO_SHORT devuelve la estrategia recomendada."""
        self.mem.register_strategy("strat_01", "BLADE_TOO_SHORT", "SWORD", "BLADE", "SET_DIMENSIONS", {"length": 0.72}, confidence=0.85)
        rec = self.mem.retrieve_recommended_strategy("BLADE_TOO_SHORT", "SWORD", "BLADE")
        self.assertTrue(rec["memory_hit"])
        self.assertEqual(rec["strategy_id"], "strat_01")
        self.assertEqual(rec["preferred_operation"], "SET_DIMENSIONS")

    def test_03_similarity_engine_calculation(self):
        """Test 3: Similarity Engine - Calcula similitud ponderada."""
        q = {"failure_type": "BLADE_TOO_SHORT", "asset_type": "SWORD", "component_type": "BLADE"}
        r_exact = {"failure_type": "BLADE_TOO_SHORT", "asset_type": "SWORD", "component_type": "BLADE"}
        r_diff = {"failure_type": "BLADE_TOO_SHORT", "asset_type": "AXE", "component_type": "HANDLE"}

        sim_exact = SimilarityEngine.calculate_similarity(q, r_exact)
        sim_diff = SimilarityEngine.calculate_similarity(q, r_diff)
        self.assertEqual(sim_exact, 1.0)
        self.assertLess(sim_diff, sim_exact)

    def test_04_cold_start_baseline(self):
        """Test 4: Cold Start - Memoria vacía devuelve fallback de la Fase 11 con memory_hit=False."""
        rec = self.mem.retrieve_recommended_strategy("UNKNOWN_FAILURE_TYPE", "SWORD", "BLADE")
        self.assertFalse(rec["memory_hit"])
        self.assertEqual(rec["preferred_operation"], "SET_DIMENSIONS")

    def test_05_repeated_success_confidence_increase(self):
        """Test 5: Repeated Success - 5 éxitos consecutivos incrementan la confianza gradualmente."""
        self.mem.register_strategy("strat_conf", "BLADE_TOO_SHORT", "SWORD", "BLADE", "SET_DIMENSIONS", confidence=0.50)
        for _ in range(5):
            self.mem.record_correction_outcome("fail_1", "strat_conf", "SET_DIMENSIONS", "blade", {}, 0.70, 0.95)

        updated = self.mem.store.get_strategy("strat_conf")
        self.assertEqual(updated.sample_count, 6)
        self.assertGreater(updated.confidence, 0.70)
        self.assertEqual(updated.success_rate, 1.0)

    def test_06_repeated_failure_confidence_decrease(self):
        """Test 6: Repeated Failure - Fallos reducen la confianza."""
        self.mem.register_strategy("strat_fail", "BLADE_TOO_SHORT", "SWORD", "BLADE", "SET_DIMENSIONS", confidence=0.80)
        self.mem.record_correction_outcome("fail_1", "strat_fail", "SET_DIMENSIONS", "blade", {}, 0.70, 0.60) # Regresión / Fallo

        updated = self.mem.store.get_strategy("strat_fail")
        self.assertLess(updated.confidence, 0.80)

    def test_07_rollback_learning(self):
        """Test 7: Rollback learning - Una corrección revertida cuenta como intento fallido."""
        self.mem.register_strategy("strat_rb", "BLADE_TOO_SHORT", "SWORD", "BLADE", "SET_DIMENSIONS", confidence=0.80)
        self.mem.record_correction_outcome("fail_1", "strat_rb", "SET_DIMENSIONS", "blade", {}, 0.70, 0.70, is_rollback=True)

        updated = self.mem.store.get_strategy("strat_rb")
        self.assertEqual(updated.failure_count, 1)
        self.assertLess(updated.confidence, 0.80)

    def test_08_systematic_bias_detection(self):
        """Test 8: Systematic Bias - 5 fallos idénticos activan alerta de bias de generación."""
        for i in range(5):
            self.mem.record_failure(f"sword_{i}", "SWORD", "BLADE", "BLADE_TOO_SHORT", 0.50, 0.72)

        recs = self.mem.get_generation_recommendations("SWORD")
        self.assertGreaterEqual(len(recs), 1)
        self.assertEqual(recs[0]["type"], "PARAMETER_ADJUSTMENT")
        self.assertEqual(recs[0]["recommended_scale_multiplier"], 1.25)

    def test_09_strategy_ranking_best_first(self):
        """Test 9: Ranking - Ordena estrategias con mayor confianza y tasa de éxito primero."""
        self.mem.register_strategy("strat_low", "BLADE_TOO_SHORT", "SWORD", "BLADE", "SCALE_OBJECT", confidence=0.30)
        self.mem.register_strategy("strat_high", "BLADE_TOO_SHORT", "SWORD", "BLADE", "SET_DIMENSIONS", confidence=0.90)

        rec = self.mem.retrieve_recommended_strategy("BLADE_TOO_SHORT", "SWORD", "BLADE")
        self.assertEqual(rec["strategy_id"], "strat_high")

    def test_10_failure_taxonomy_registry(self):
        """Test 10: Taxonomy - Clasifica tipos de fallos en categorías ontológicas."""
        self.assertEqual(FailureTypeRegistry.get_category("BLADE_TOO_SHORT"), FailureCategory.PROPORTION)
        self.assertEqual(FailureTypeRegistry.get_category("MATERIAL_METALLIC_MISMATCH"), FailureCategory.MATERIAL)
        self.assertEqual(FailureTypeRegistry.get_category("NON_MANIFOLD_TOPOLOGY"), FailureCategory.TOPOLOGY)

    def test_11_full_learning_cycle(self):
        """Test 11: Full Cycle - Registro de fallo -> Recuperación -> Registro de éxito -> Re-consulta."""
        # 1. Registrar fallo
        f_rec = self.mem.record_failure("sword_100", "SWORD", "BLADE", "BLADE_TOO_SHORT", 0.40, 0.72)
        # 2. Registrar estrategia base
        self.mem.register_strategy("strat_opt", "BLADE_TOO_SHORT", "SWORD", "BLADE", "SET_DIMENSIONS", {"length": 0.72}, confidence=0.60)
        # 3. Consultar recomendación
        rec1 = self.mem.retrieve_recommended_strategy("BLADE_TOO_SHORT", "SWORD", "BLADE")
        self.assertEqual(rec1["confidence"], 0.60)
        # 4. Registrar resultado de corrección
        self.mem.record_correction_outcome(f_rec.failure_id, "strat_opt", "SET_DIMENSIONS", "blade", {"length": 0.72}, 0.50, 0.98)
        # 5. Re-consultar recomendación (debe tener mayor confianza)
        rec2 = self.mem.retrieve_recommended_strategy("BLADE_TOO_SHORT", "SWORD", "BLADE")
        self.assertGreater(rec2["confidence"], 0.60)

if __name__ == "__main__":
    unittest.main()
