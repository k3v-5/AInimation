import os
import sys
import unittest
import time
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.memory import (
    ContextMemoryAPI, MemoryRecord, MemoryType, MemoryScope, MemoryStatus, MemorySource,
    MemoryStore, ContextRelevanceEngine, ContextConflictDetector, ContextBuilder, ExecutionContext,
    ContextSnapshot, ContextSnapshotManager, MemoryConsolidator, MemoryGovernanceGuard,
    MemoryPermissionDeniedError
)

class TestSuitePhase73ContextMemoryManagement(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.api = ContextMemoryAPI(persistence_path=self.temp_file.name)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            try:
                os.remove(self.temp_file.name)
            except Exception:
                pass

    def test_01_memory_creation_and_hash_integrity(self):
        rec = MemoryRecord(
            memory_id="mem_001",
            memory_type=MemoryType.STYLE_MEMORY,
            scope=MemoryScope.PROJECT,
            content={"style": "Cyberpunk Tactical"},
            source=MemorySource.USER
        )
        self.assertTrue(len(rec.memory_hash) == 64)
        computed = rec.compute_hash()
        self.assertEqual(rec.memory_hash, computed)

    def test_02_memory_store_crud_and_disk_persistence(self):
        rec = MemoryRecord(
            memory_id="mem_crud",
            memory_type=MemoryType.DECISION_MEMORY,
            scope=MemoryScope.ASSET,
            semantic_id="weapon.darx.vandal.001",
            content={"barrel_length": 550},
            source=MemorySource.STRATEGY_ENGINE
        )
        self.api.store.create(rec)
        fetched = self.api.store.get("mem_crud")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.content["barrel_length"], 550)

        # Reload store from disk
        store2 = MemoryStore(self.temp_file.name)
        fetched2 = store2.get("mem_crud")
        self.assertIsNotNone(fetched2)
        self.assertEqual(fetched2.content["barrel_length"], 550)

    def test_03_memory_scopes_isolation(self):
        rec_asset = MemoryRecord(
            memory_id="mem_asset_a", memory_type=MemoryType.ASSET_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.rifle.alpha",
            content={"receiver": "alpha_mesh"}, source=MemorySource.BLENDER
        )
        rec_asset_b = MemoryRecord(
            memory_id="mem_asset_b", memory_type=MemoryType.ASSET_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.rifle.beta",
            content={"receiver": "beta_mesh"}, source=MemorySource.BLENDER
        )
        self.api.store.create(rec_asset)
        self.api.store.create(rec_asset_b)

        recs_a = self.api.store.list_by_asset("weapon.rifle.alpha")
        sem_ids = [r.semantic_id for r in recs_a if r.semantic_id]
        self.assertIn("weapon.rifle.alpha", sem_ids)
        self.assertNotIn("weapon.rifle.beta", sem_ids)

    def test_04_memory_versioning_and_supersede(self):
        v1 = MemoryRecord(
            memory_id="dim_v1", memory_type=MemoryType.DECISION_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.vandal.001",
            content={"length": 880}, source=MemorySource.USER, version=1
        )
        self.api.store.create(v1)

        v2 = MemoryRecord(
            memory_id="dim_v2", memory_type=MemoryType.DECISION_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.vandal.001",
            content={"length": 920}, source=MemorySource.USER
        )
        self.api.store.supersede("dim_v1", v2)

        v1_updated = self.api.store.get("dim_v1")
        v2_updated = self.api.store.get("dim_v2")

        self.assertEqual(v1_updated.status, MemoryStatus.SUPERSEDED)
        self.assertEqual(v1_updated.superseded_by, "dim_v2")
        self.assertEqual(v2_updated.status, MemoryStatus.ACTIVE)
        self.assertEqual(v2_updated.version, 2)

    def test_05_memory_invalidation(self):
        rec = MemoryRecord(
            memory_id="temp_rule", memory_type=MemoryType.CONSTRAINT_MEMORY,
            scope=MemoryScope.PROJECT, content={"temporary_rule": True},
            source=MemorySource.AGENT
        )
        self.api.store.create(rec)
        self.api.store.invalidate("temp_rule", "Replaced by project mandate")

        invalidated = self.api.store.get("temp_rule")
        self.assertEqual(invalidated.status, MemoryStatus.INVALIDATED)
        self.assertEqual(invalidated.metadata["invalidation_reason"], "Replaced by project mandate")

        # Excluded from active queries
        active_list = self.api.store.list_all(status=MemoryStatus.ACTIVE)
        self.assertNotIn("temp_rule", [r.memory_id for r in active_list])

    def test_06_source_tracking_and_confidence(self):
        user_mem = MemoryRecord(
            memory_id="user_spec", memory_type=MemoryType.CONSTRAINT_MEMORY,
            scope=MemoryScope.ASSET, content={"required": True},
            source=MemorySource.USER, confidence=1.0, importance=1.0
        )
        agent_mem = MemoryRecord(
            memory_id="agent_guess", memory_type=MemoryType.ASSET_MEMORY,
            scope=MemoryScope.ASSET, content={"guess": True},
            source=MemorySource.AGENT, confidence=0.35, importance=0.4
        )
        self.api.store.create(user_mem)
        self.api.store.create(agent_mem)

        self.assertEqual(self.api.store.get("user_spec").confidence, 1.0)
        self.assertEqual(self.api.store.get("agent_guess").confidence, 0.35)

    def test_07_context_relevance_ranking(self):
        engine = ContextRelevanceEngine()
        rec_match = MemoryRecord(
            memory_id="rec_m", memory_type=MemoryType.ASSET_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.vandal.001",
            content={"part": "stock"}, source=MemorySource.BLENDER, importance=0.9
        )
        rec_other = MemoryRecord(
            memory_id="rec_o", memory_type=MemoryType.ASSET_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="boss.robot.001",
            content={"boss_armor": 500}, source=MemorySource.BLENDER, importance=0.2
        )
        score_match = engine.compute_relevance(rec_match, target_semantic_id="weapon.vandal.001")
        score_other = engine.compute_relevance(rec_other, target_semantic_id="weapon.vandal.001")

        self.assertGreater(score_match, score_other)
        self.assertGreaterEqual(score_match, 0.7)

    def test_08_context_builder_execution_context_assembly(self):
        self.api.record_asset_decision(
            semantic_id="weapon.vandal.001",
            decision_data={"sight_type": "Holographic Reflex"},
            agent_id="agent.strategy"
        )
        self.api.record_critic_findings(
            semantic_id="weapon.vandal.001",
            findings={"defect": "stock_too_short"},
            task_id="T_V1"
        )

        ctx = self.api.build_execution_context(
            project_id="DarX",
            task_id="T_V2",
            agent_id="agent.blender.execution",
            semantic_id="weapon.vandal.001"
        )
        self.assertIsInstance(ctx, ExecutionContext)
        self.assertGreater(len(ctx.active_constraints), 0)
        self.assertGreater(len(ctx.active_decisions), 0)
        self.assertGreater(len(ctx.known_errors), 0)

    def test_09_context_budgeting_and_limits(self):
        for i in range(20):
            self.api.store.create(MemoryRecord(
                memory_id=f"bulk_mem_{i}",
                memory_type=MemoryType.ASSET_MEMORY,
                scope=MemoryScope.ASSET,
                semantic_id="weapon.bulk.test",
                content={"idx": i},
                source=MemorySource.AGENT,
                importance=0.1 * (i % 10)
            ))

        ctx = self.api.build_execution_context(
            project_id="DarX", task_id="T_BUDGET", agent_id="agent.geometry",
            semantic_id="weapon.bulk.test", max_memories=5
        )
        self.assertLessEqual(len(ctx.relevant_memories), 5)

    def test_10_conflict_detection_and_resolution(self):
        detector = ContextConflictDetector()
        mem_agent = MemoryRecord(
            memory_id="mem_a", memory_type=MemoryType.DECISION_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.vandal.001",
            content={"length": 880}, source=MemorySource.AGENT, confidence=0.6
        )
        mem_user = MemoryRecord(
            memory_id="mem_u", memory_type=MemoryType.DECISION_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.vandal.001",
            content={"length": 920}, source=MemorySource.USER, confidence=1.0
        )
        conflicts = detector.detect_conflicts([mem_agent, mem_user])
        self.assertGreaterEqual(len(conflicts), 1)

        resolved = detector.resolve_conflict(mem_agent, mem_user)
        self.assertEqual(resolved.memory_id, "mem_u")
        self.assertEqual(resolved.content["length"], 920)

    def test_11_memory_consolidation(self):
        c1 = MemoryRecord(
            memory_id="crit_1", memory_type=MemoryType.ERROR_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.vandal.001",
            content={"issue": "grip_angle_too_steep"}, source=MemorySource.CRITIC
        )
        c2 = MemoryRecord(
            memory_id="crit_2", memory_type=MemoryType.ERROR_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.vandal.001",
            content={"issue": "grip_texture_slippery"}, source=MemorySource.CRITIC
        )
        self.api.store.create(c1)
        self.api.store.create(c2)

        dec = self.api.consolidator.consolidate_critiques_to_decision(
            semantic_id="weapon.vandal.001",
            critique_memory_ids=["crit_1", "crit_2"],
            consolidated_action={"grip_redesign": "Ergonomic 15-degree textured grip"}
        )
        self.assertEqual(dec.memory_type, MemoryType.DECISION_MEMORY)
        self.assertIn("grip_redesign", dec.content["action_plan"])
        self.assertEqual(len(dec.content["source_findings"]), 2)

    def test_12_context_snapshot_capture_and_recovery(self):
        ctx = self.api.build_execution_context(
            project_id="DarX", task_id="T_SNAP", agent_id="agent.strategy",
            semantic_id="weapon.vandal.001"
        )
        snap = self.api.capture_context_snapshot("SNAP_F73_001", ctx)
        self.assertEqual(snap.snapshot_id, "SNAP_F73_001")
        self.assertTrue(len(snap.snapshot_hash) == 64)

        retrieved = self.api.snapshots.get_snapshot("SNAP_F73_001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.snapshot_hash, snap.snapshot_hash)

    def test_13_cross_agent_context_propagation(self):
        # 1. Perception Agent stores reference findings
        self.api.store.create(MemoryRecord(
            memory_id="ref_analysis_01", memory_type=MemoryType.REFERENCE_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.vandal.001",
            content={"palette": ["Titanium", "Carbon"], "primary_shape": "Angular"},
            source=MemorySource.REFERENCE_ANALYSIS, agent_id="agent.perception"
        ))
        # 2. Strategy Agent retrieves it automatically
        ctx_strat = self.api.build_execution_context(
            project_id="DarX", task_id="T_STRATEGY", agent_id="agent.strategy",
            semantic_id="weapon.vandal.001"
        )
        self.assertIn({"palette": ["Titanium", "Carbon"], "primary_shape": "Angular"}, ctx_strat.relevant_references)

    def test_14_cross_task_iterative_improvement(self):
        # Task 1: Record critic findings
        self.api.record_critic_findings(
            semantic_id="weapon.vandal.001",
            findings={"silueta": "demasiado delgada", "biseles": "ausentes"},
            task_id="T1_Generate"
        )
        # Task 2: Build context for iteration 2
        ctx_t2 = self.api.build_execution_context(
            project_id="DarX", task_id="T2_Improve", agent_id="agent.strategy",
            semantic_id="weapon.vandal.001"
        )
        self.assertIn(str({"silueta": "demasiado delgada", "biseles": "ausentes"}), ctx_t2.known_errors)

    def test_15_governance_permission_enforcement(self):
        guard = MemoryGovernanceGuard()
        # Invalid agent writing project memory
        with self.assertRaises(MemoryPermissionDeniedError):
            guard.validate_write_access("agent.qa.validator", MemoryScope.PROJECT)

    def test_16_semantic_id_persistence_across_file_renaming(self):
        # Memory is tied to semantic_id
        rec = MemoryRecord(
            memory_id="sem_track", memory_type=MemoryType.ASSET_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.darx.001",
            content={"approved_parts": ["Barrel", "Stock"]}, source=MemorySource.BLENDER
        )
        self.api.store.create(rec)
        
        # Querying by semantic_id returns it regardless of filename
        recs = self.api.store.list_by_asset("weapon.darx.001")
        self.assertEqual(len(recs), 3) # 2 project defaults + 1 asset

    def test_17_no_cross_asset_leakage(self):
        self.api.store.create(MemoryRecord(
            memory_id="secret_boss_lore", memory_type=MemoryType.ASSET_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="boss.final.omega",
            content={"weakness": "core_emitter"}, source=MemorySource.USER
        ))
        
        ctx_weapon = self.api.build_execution_context(
            project_id="DarX", task_id="T_WEAPON", agent_id="agent.geometry",
            semantic_id="weapon.vandal.001"
        )
        for mem in ctx_weapon.relevant_memories:
            self.assertNotEqual(mem["memory_id"], "secret_boss_lore")

    def test_18_restart_persistence(self):
        self.api.record_asset_decision(
            semantic_id="weapon.persistent.001",
            decision_data={"color": "Amber Glow"},
            agent_id="agent.strategy"
        )
        
        # Simulate clean restart by creating brand new API instance
        api_restarted = ContextMemoryAPI(persistence_path=self.temp_file.name)
        recs = api_restarted.store.list_by_asset("weapon.persistent.001")
        decisions = [r.content for r in recs if r.memory_type == MemoryType.DECISION_MEMORY]
        self.assertIn({"color": "Amber Glow"}, decisions)

    def test_19_idempotent_memory_updates(self):
        rec = MemoryRecord(
            memory_id="idem_01", memory_type=MemoryType.STYLE_MEMORY,
            scope=MemoryScope.PROJECT, content={"version": 1}, source=MemorySource.USER
        )
        self.api.store.create(rec)
        h1 = rec.memory_hash
        self.api.store.update(rec)
        h2 = rec.memory_hash
        self.assertEqual(h1, h2)

    def test_20_false_memory_unverified_exclusion(self):
        # 1. Add verified high-confidence asset memories
        self.api.store.create(MemoryRecord(
            memory_id="verified_part_1", memory_type=MemoryType.ASSET_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.vandal.001",
            content={"receiver": "vandal_receiver"}, source=MemorySource.BLENDER,
            confidence=1.0, importance=0.9
        ))
        self.api.store.create(MemoryRecord(
            memory_id="verified_part_2", memory_type=MemoryType.ASSET_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.vandal.001",
            content={"barrel": "vandal_barrel"}, source=MemorySource.BLENDER,
            confidence=1.0, importance=0.9
        ))
        # 2. Add unverified false guess
        self.api.store.create(MemoryRecord(
            memory_id="false_guess", memory_type=MemoryType.ASSET_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.vandal.001",
            content={"guess": "maybe_shotgun"}, source=MemorySource.AGENT,
            confidence=0.1, importance=0.1
        ))
        
        ctx = self.api.build_execution_context(
            project_id="DarX", task_id="T_STRICT", agent_id="agent.geometry",
            semantic_id="weapon.vandal.001"
        )
        # Low confidence memories should rank at the bottom and not be in top 3
        mem_ids = [m["memory_id"] for m in ctx.relevant_memories]
        self.assertNotIn("false_guess", mem_ids[:3])
        self.assertEqual(mem_ids[-1], "false_guess")

    def test_21_memory_promotion_agent_to_project(self):
        rec_agent = MemoryRecord(
            memory_id="bevel_tip", memory_type=MemoryType.AGENT_MEMORY,
            scope=MemoryScope.AGENT, agent_id="agent.geometry",
            content={"tip": "0.002 bevel on dark titanium prevents harsh aliasing"},
            source=MemorySource.AGENT, confidence=0.7
        )
        self.api.store.create(rec_agent)
        
        # Promote to project style memory
        rec_promoted = MemoryRecord(
            memory_id="style_bevel_promoted", memory_type=MemoryType.STYLE_MEMORY,
            scope=MemoryScope.PROJECT,
            content=rec_agent.content,
            source=MemorySource.SYSTEM,
            confidence=0.95,
            importance=0.85
        )
        self.api.store.supersede("bevel_tip", rec_promoted)
        self.assertEqual(self.api.store.get("bevel_tip").status, MemoryStatus.SUPERSEDED)
        self.assertEqual(self.api.store.get("style_bevel_promoted").status, MemoryStatus.ACTIVE)

    def test_22_cross_agent_strategy_to_blender_propagation(self):
        # Strategy agent records MSP
        self.api.record_asset_decision(
            semantic_id="weapon.darx.carbine.001",
            decision_data={"assembly_mode": "MODULAR_SLOT_BASED"},
            agent_id="agent.strategy"
        )
        
        # Blender agent builds execution context
        ctx = self.api.build_execution_context(
            project_id="DarX", task_id="T_BUILD", agent_id="agent.blender.execution",
            semantic_id="weapon.darx.carbine.001"
        )
        decision_contents = [d["content"] for d in ctx.active_decisions]
        self.assertIn({"assembly_mode": "MODULAR_SLOT_BASED"}, decision_contents)

    def test_23_iterative_three_stage_feedback_loop(self):
        sem_id = "weapon.iteration.test"
        # Stage 1: V1 Generation + Critic 1
        self.api.record_asset_result(sem_id, {"version": "v1", "polygon_count": 1200}, "T1", "agent.blender")
        self.api.record_critic_findings(sem_id, {"defect": "barrel_too_thin"}, "T1", "agent.critic")
        
        # Stage 2: V2 Context Building & Improvement
        ctx_v2 = self.api.build_execution_context("DarX", "T2", "agent.strategy", sem_id)
        self.assertIn(str({"defect": "barrel_too_thin"}), ctx_v2.known_errors)
        self.api.record_asset_result(sem_id, {"version": "v2", "barrel_diameter": "thickened"}, "T2", "agent.blender")
        self.api.record_critic_findings(sem_id, {"defect": "sight_alignment_low"}, "T2", "agent.critic")
        
        # Stage 3: V3 Context Building & Final Polish
        ctx_v3 = self.api.build_execution_context("DarX", "T3", "agent.strategy", sem_id)
        self.assertEqual(len(ctx_v3.known_errors), 2)
        self.assertIn(str({"defect": "sight_alignment_low"}), ctx_v3.known_errors)

    def test_24_f70_recovery_snapshot_association(self):
        ctx = self.api.build_execution_context("DarX", "T_CRASH", "agent.geometry", "weapon.vandal.001")
        snap = self.api.capture_context_snapshot("SNAP_F70_CP3", ctx)
        
        # Simulate Crash and Recovery lookup
        recovered_snap = self.api.snapshots.get_snapshot("SNAP_F70_CP3")
        self.assertIsNotNone(recovered_snap)
        self.assertEqual(recovered_snap.semantic_id, "weapon.vandal.001")
        self.assertEqual(recovered_snap.snapshot_hash, snap.snapshot_hash)

    def test_25_context_relevance_audit_trail(self):
        ctx = self.api.build_execution_context("DarX", "T_AUDIT", "agent.strategy", "weapon.vandal.001")
        self.assertGreater(len(ctx.relevance_audit), 0)
        first_audit = ctx.relevance_audit[0]
        self.assertIn("memory_id", first_audit)
        self.assertIn("relevance_score", first_audit)
        self.assertIn("source", first_audit)

    def test_26_memory_query_by_tag(self):
        self.api.store.create(MemoryRecord(
            memory_id="tag_test_mem", memory_type=MemoryType.STYLE_MEMORY,
            scope=MemoryScope.PROJECT, content={"theme": "stealth"},
            source=MemorySource.USER, tags=["stealth_tag"]
        ))
        res = self.api.store.query(tag="stealth_tag")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].memory_id, "tag_test_mem")

    def test_27_memory_archive_lifecycle(self):
        rec = MemoryRecord(
            memory_id="archive_me", memory_type=MemoryType.TASK_MEMORY,
            scope=MemoryScope.TASK, content={"temp": True}, source=MemorySource.SYSTEM
        )
        self.api.store.create(rec)
        self.api.store.archive("archive_me")
        self.assertEqual(self.api.store.get("archive_me").status, MemoryStatus.ARCHIVED)
        active_recs = self.api.store.list_all(status=MemoryStatus.ACTIVE)
        self.assertNotIn("archive_me", [r.memory_id for r in active_recs])

    def test_28_f72_governance_integration_memory_invalidation_denial(self):
        guard = MemoryGovernanceGuard()
        with self.assertRaises(MemoryPermissionDeniedError):
            guard.validate_invalidation_access("agent.perception")

    def test_29_provenance_lineage_chain(self):
        r1 = self.api.store_memory(MemoryRecord(
            memory_id="ref_01", memory_type=MemoryType.REFERENCE_MEMORY,
            scope=MemoryScope.ASSET, content={"ref": "photo"}, source=MemorySource.REFERENCE_ANALYSIS
        ))
        r2 = self.api.store_memory(MemoryRecord(
            memory_id="dec_01", memory_type=MemoryType.DECISION_MEMORY,
            scope=MemoryScope.ASSET, content={"dec": "use_photo_proportions"},
            source=MemorySource.AOE, parent_memory_id="ref_01"
        ), derived_from=["ref_01"])

        lineage = self.api.provenance.get_lineage("dec_01")
        self.assertEqual(len(lineage), 2)
        self.assertEqual(lineage[0].memory_id, "dec_01")
        self.assertEqual(lineage[1].memory_id, "ref_01")

    def test_30_context_recovery_service_all_scopes(self):
        # Seed asset & job data
        self.api.store_memory(MemoryRecord(
            memory_id="op_job_1", memory_type=MemoryType.OPERATION_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.rec.001", job_id="JOB_999",
            task_id="T_REC", agent_id="agent.blender.execution", content={"objects": ["Barrel"]}
        ))
        
        ctx_proj = self.api.recover_context("PROJECT", "DarX")
        ctx_asset = self.api.recover_context("ASSET", "weapon.rec.001")
        ctx_job = self.api.recover_context("JOB", "JOB_999")
        ctx_agent = self.api.recover_context("AGENT", "agent.blender.execution")
        ctx_task = self.api.recover_context("TASK", "T_REC")

        self.assertEqual(ctx_proj.project_id, "DarX")
        self.assertEqual(ctx_asset.semantic_id, "weapon.rec.001")
        self.assertEqual(ctx_job.job_id, "JOB_999")
        self.assertIn("op_job_1", ctx_job.completed_operations)
        self.assertEqual(ctx_agent.agent_id, "agent.blender.execution")
        self.assertEqual(ctx_task.task_id, "T_REC")

    def test_31_context_packaging_with_priority_and_filtering(self):
        pkg = self.api.context_manager.build_context_package(
            task_id="T_MAT", agent_id="agent.material", semantic_id="weapon.rec.001",
            task_objective="Assign PBR materials"
        )
        self.assertEqual(pkg.task_id, "T_MAT")
        self.assertIn("task_id", pkg.required_context)
        self.assertIn("agent_id", pkg.required_context)

    def test_32_context_conflict_detection_and_resolution(self):
        m1 = MemoryRecord(
            memory_id="len_user", memory_type=MemoryType.REQUIREMENT_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.conflict.test",
            content={"total_length": 920}, source=MemorySource.USER
        )
        m2 = MemoryRecord(
            memory_id="len_agent", memory_type=MemoryType.DECISION_MEMORY,
            scope=MemoryScope.ASSET, semantic_id="weapon.conflict.test",
            content={"total_length": 880}, source=MemorySource.AGENT
        )
        self.api.store_memory(m1)
        self.api.store_memory(m2)

        conflicts = self.api.detect_conflicts()
        self.assertGreaterEqual(len(conflicts), 1)
        resolved = self.api.context_manager.conflicts.resolve_conflict(conflicts[0], m1, m2)
        self.assertEqual(resolved.memory_id, "len_user")
        self.assertEqual(resolved.content["total_length"], 920)

    def test_33_agent_handoff_and_task_continuation(self):
        # Agent A registers progress
        self.api.store_memory(MemoryRecord(
            memory_id="step_a", memory_type=MemoryType.OPERATION_MEMORY,
            scope=MemoryScope.TASK, task_id="T_HANDOFF", agent_id="agent.geometry.worker.001",
            content={"completed_part": "Receiver", "pending_actions": ["Barrel", "Stock"]}
        ))
        
        # Agent B takes over task and recovers state
        ctx_b = self.api.recover_context("TASK", "T_HANDOFF")
        self.assertEqual(ctx_b.task_id, "T_HANDOFF")
        self.assertIn("step_a", ctx_b.completed_steps)

    def test_34_integrity_verification_and_corruption_detection(self):
        rec = MemoryRecord(
            memory_id="integrity_test", memory_type=MemoryType.REQUIREMENT_MEMORY,
            scope=MemoryScope.PROJECT, content={"secure": "data"}
        )
        self.assertTrue(rec.verify_integrity())
        
        # Tamper with content without updating hash
        rec.content = {"tampered": True}
        self.assertFalse(rec.verify_integrity())

    def test_35_api_section_26_methods(self):
        # Create and restore snapshot via API
        snap = self.api.create_snapshot("SNAP_API_001", {"state": "OK", "step": 3})
        self.assertEqual(snap.snapshot_id, "SNAP_API_001")
        
        restored = self.api.restore_snapshot("SNAP_API_001")
        self.assertEqual(restored["state"], "OK")
        self.assertEqual(restored["step"], 3)

if __name__ == "__main__":
    unittest.main()
