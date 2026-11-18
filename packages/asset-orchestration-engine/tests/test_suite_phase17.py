import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    AssetMemorySystemAPI, MockBlenderProvider, ProceduralTemplatesAPI,
    PatternStatus, ReproductionStatus, VersionManager, ReuseStrategyDecision
)

class TestAssetMemoryPhase17(unittest.TestCase):
    def setUp(self):
        self.mem_sys = AssetMemorySystemAPI(":memory:")
        self.provider = MockBlenderProvider()
        self.templates_api = ProceduralTemplatesAPI(self.provider)

    def tearDown(self):
        self.mem_sys.close()

    def test_01_create_asset_and_version(self):
        """Test 1: Create Asset & Version - Almacena asset y versión 1.0.0."""
        rec = self.mem_sys.create_asset("SM_Sword_001", "Medieval Sword", "SWORD", "weapon.sword.standard")
        self.assertIsNotNone(rec)
        self.assertEqual(rec.asset_id, "SM_Sword_001")

        v_rec, is_dup = self.mem_sys.create_version("SM_Sword_001", "1.0.0", {"blade_length": 0.90, "blade_width": 0.05})
        self.assertFalse(is_dup)
        self.assertEqual(v_rec.version_number, "1.0.0")

    def test_02_version_lineage_and_branching(self):
        """Test 2: Lineage - Crea versión derivada registrando parent_version_id y branch."""
        self.mem_sys.create_asset("SM_Sword_002", "Sword", "SWORD", "weapon.sword.standard")
        v1, _ = self.mem_sys.create_version("SM_Sword_002", "1.0.0", {"blade_length": 0.90})
        v2, _ = self.mem_sys.create_version("SM_Sword_002", "1.1.0", {"blade_length": 1.00}, parent_version_id=v1.version_id, branch="experimental")
        self.assertEqual(v2.parent_version_id, v1.version_id)
        self.assertEqual(v2.branch, "experimental")

    def test_03_duplicate_detection(self):
        """Test 3: Duplicate Detection - Parámetros idénticos devuelven is_duplicate=True."""
        self.mem_sys.create_asset("SM_Sword_003", "Sword", "SWORD", "weapon.sword.standard")
        v1, is_dup1 = self.mem_sys.create_version("SM_Sword_003", "1.0.0", {"blade_length": 0.90})
        self.assertFalse(is_dup1)
        v2, is_dup2 = self.mem_sys.create_version("SM_Sword_003", "1.0.0", {"blade_length": 0.90})
        self.assertTrue(is_dup2)
        self.assertEqual(v1.version_id, v2.version_id)

    def test_04_similarity_search_and_reuse_strategy(self):
        """Test 4: Reuse Strategy - Clasifica similitud en REUSE, ADAPT, GENERATE."""
        self.assertEqual(ReuseStrategyDecision.determine_strategy(0.98)[0], "REUSE")
        self.assertEqual(ReuseStrategyDecision.determine_strategy(0.85)[0], "ADAPT")
        self.assertEqual(ReuseStrategyDecision.determine_strategy(0.50)[0], "GENERATE")
        self.assertEqual(ReuseStrategyDecision.determine_strategy(0.98, user_forces_generate=True)[0], "GENERATE")

    def test_05_learning_from_corrections_candidate_pattern(self):
        """Test 5: Learning - Corrección exitosa genera CandidatePattern."""
        pat = self.mem_sys.record_correction_and_learn(
            template_id="weapon.sword.standard",
            trigger_issue="blade_too_narrow",
            target_parameter="blade_width",
            recommended_action="SET blade_width = 0.075",
            is_success=True
        )
        self.assertEqual(pat.status, PatternStatus.CANDIDATE)
        self.assertEqual(pat.target_parameter, "blade_width")

    def test_06_pattern_promotion_lifecycle(self):
        """Test 6: Promotion - 3 éxitos consecutivos promueven CANDIDATE -> VALIDATED."""
        pat1 = self.mem_sys.record_correction_and_learn("weapon.sword.standard", "blade_too_short", "blade_length", "SET 0.95", True)
        pat2 = self.mem_sys.record_correction_and_learn("weapon.sword.standard", "blade_too_short", "blade_length", "SET 0.95", True)
        pat3 = self.mem_sys.record_correction_and_learn("weapon.sword.standard", "blade_too_short", "blade_length", "SET 0.95", True)
        self.assertEqual(pat3.status, PatternStatus.VALIDATED)
        self.assertEqual(pat3.success_count, 3)

    def test_07_negative_knowledge_warning(self):
        """Test 7: Negative Knowledge - Registra fallo y advierte si se repite KNOWN_FAILURE_REGION."""
        self.mem_sys.record_failure("sword_fail", "weapon.sword.standard", {"guard_width": 0.50}, error_type="COLLISION")
        is_fail_reg, msg = self.mem_sys.check_negative_knowledge("weapon.sword.standard", {"guard_width": 0.55})
        self.assertTrue(is_fail_reg)
        self.assertIn("KNOWN_FAILURE_REGION", msg)

    def test_08_deterministic_reproduction(self):
        """Test 8: Reproduction - Reproduce versión exactamente desde seed y parámetros."""
        self.mem_sys.create_asset("sword_repro", "Sword", "SWORD", "weapon.sword.standard")
        v_rec, _ = self.mem_sys.create_version("sword_repro", "1.0.0", {"blade_length": 0.90}, seed=100)
        status, msg = self.mem_sys.reproduce_version("sword_repro", v_rec, self.provider, self.templates_api)
        self.assertEqual(status, ReproductionStatus.EXACT)

    def test_09_memoryless_fallback_mode(self):
        """Test 9: Memoryless - Modo memoryless funciona sin base de datos ni excepciones."""
        m_less = AssetMemorySystemAPI(is_memoryless=True)
        res = m_less.create_asset("SM_Sword_999", "Sword")
        self.assertIsNone(res)
        v_rec, is_dup = m_less.create_version("SM_Sword_999", "1.0.0")
        self.assertFalse(is_dup)

    def test_10_semver_bumping(self):
        """Test 10: SemVer - Incrementa versiones PATCH, MINOR, MAJOR."""
        self.assertEqual(VersionManager.bump_version("1.0.0", "PATCH"), "1.0.1")
        self.assertEqual(VersionManager.bump_version("1.0.1", "MINOR"), "1.1.0")
        self.assertEqual(VersionManager.bump_version("1.1.0", "MAJOR"), "2.0.0")

if __name__ == "__main__":
    unittest.main()
