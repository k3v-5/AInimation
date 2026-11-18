import sys
import os
import unittest
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.orchestration import (
    MultiAgentOrchestrationAPI, OrchestrationEngine, OrchestrationPlan, OrchestrationPolicy,
    AgentRegistry, AgentContract, AgentContext, AgentResult, AssetMutation, Agent,
    Task, TaskGraph, TaskScheduler, OrchestrationEvent, OrchestrationEventLog,
    AgentState, AgentPermission, TaskStatus, TaskPriority, FailureAction,
    CyclicDependencyError, ToolAccessDeniedError, PermissionDeniedError, AgentNotFoundError,
    PerceptionAgent, DesignAnalysisAgent, StrategyAgent, GeometryAgent,
    MaterialAgent, BlenderExecutionAgent, VisualCriticAgent, QAAgent, CorrectionAgent,
    PackagingAgent
)

class DummyTestAgent(Agent):
    def __init__(self, agent_id="agent.dummy", forbidden_tools=None):
        contract = AgentContract(
            agent_id=agent_id,
            version="1.0.0",
            capabilities=["dummy.action"],
            permissions=[AgentPermission.READ_PROJECT],
            allowed_tools=["dummy_tool"],
            forbidden_tools=forbidden_tools or ["forbidden_tool"]
        )
        super().__init__(agent_id=agent_id, agent_type="DUMMY", version="1.0.0", contract=contract)

    def execute(self, task_input, context):
        return AgentResult(
            success=True,
            status=TaskStatus.COMPLETED,
            agent_id=self.agent_id,
            agent_version=self.version,
            task_id=context.task_id,
            outputs={"result": "OK"}
        )

class TestSuitePhase71MultiAgentOrchestration(unittest.TestCase):

    def setUp(self):
        self.api = MultiAgentOrchestrationAPI()

    def test_01_agent_registry_registration_and_lookup(self):
        reg = AgentRegistry()
        agent = DummyTestAgent("agent.test.lookup")
        reg.register(agent)
        
        self.assertEqual(reg.get("agent.test.lookup").agent_id, "agent.test.lookup")
        self.assertIn(agent, reg.list_agents())
        self.assertTrue(reg.validate_agent("agent.test.lookup"))
        
        reg.unregister("agent.test.lookup")
        with self.assertRaises(AgentNotFoundError):
            reg.get("agent.test.lookup")

    def test_02_agent_registry_duplicate_rejection(self):
        reg = AgentRegistry()
        agent = DummyTestAgent("agent.duplicate")
        reg.register(agent)
        with self.assertRaises(ValueError):
            reg.register(agent)

    def test_03_agent_registry_find_by_capability_and_type(self):
        reg = AgentRegistry()
        p_agent = PerceptionAgent()
        g_agent = GeometryAgent()
        reg.register(p_agent)
        reg.register(g_agent)
        
        found = reg.find_by_capability("perception.analyze_reference")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].agent_id, "agent.perception")
        
        by_type = reg.find_by_type("GEOMETRY")
        self.assertEqual(len(by_type), 1)
        self.assertEqual(by_type[0].agent_id, "agent.geometry")

    def test_04_agent_contract_tool_access_validation(self):
        agent = DummyTestAgent("agent.tools", forbidden_tools=["dangerous_tool"])
        self.assertTrue(agent.contract.validate_tool_access("dummy_tool"))
        self.assertFalse(agent.contract.validate_tool_access("dangerous_tool"))

    def test_05_tool_governance_denial_raises_error(self):
        agent = DummyTestAgent("agent.governance", forbidden_tools=["banned_tool"])
        with self.assertRaises(ToolAccessDeniedError):
            agent.run_tool("banned_tool", lambda: "SHOULD_FAIL")

    def test_06_task_state_transitions(self):
        task = Task(task_id="T_STATE", task_type="TEST", description="State test")
        self.assertEqual(task.status, TaskStatus.PENDING)
        
        task.transition_to(TaskStatus.READY)
        self.assertEqual(task.status, TaskStatus.READY)
        
        task.transition_to(TaskStatus.RUNNING)
        self.assertEqual(task.status, TaskStatus.RUNNING)
        self.assertIsNotNone(task.started_at)
        
        task.transition_to(TaskStatus.COMPLETED)
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(task.completed_at)
        
        with self.assertRaises(ValueError):
            task.transition_to(TaskStatus.RUNNING) # Completed is terminal

    def test_07_task_graph_dag_and_layering(self):
        graph = TaskGraph()
        t1 = Task(task_id="T1", task_type="A", description="Step 1")
        t2 = Task(task_id="T2", task_type="B", description="Step 2", dependencies=["T1"])
        t3 = Task(task_id="T3", task_type="C", description="Step 3", dependencies=["T1"])
        t4 = Task(task_id="T4", task_type="D", description="Step 4", dependencies=["T2", "T3"])
        
        for t in [t1, t2, t3, t4]:
            graph.add_task(t)
            
        graph.validate_graph()
        layers = graph.get_execution_layers()
        self.assertEqual(len(layers), 3)
        self.assertEqual([t.task_id for t in layers[0]], ["T1"])
        self.assertEqual(sorted([t.task_id for t in layers[1]]), ["T2", "T3"])
        self.assertEqual([t.task_id for t in layers[2]], ["T4"])

    def test_08_task_graph_cycle_detection(self):
        graph = TaskGraph()
        t1 = Task(task_id="T1", task_type="A", description="1", dependencies=["T3"])
        t2 = Task(task_id="T2", task_type="B", description="2", dependencies=["T1"])
        t3 = Task(task_id="T3", task_type="C", description="3", dependencies=["T2"])
        
        for t in [t1, t2, t3]:
            graph.add_task(t)
            
        with self.assertRaises(CyclicDependencyError):
            graph.validate_graph()

    def test_09_task_graph_missing_dependency_rejection(self):
        graph = TaskGraph()
        t1 = Task(task_id="T1", task_type="A", description="1", dependencies=["NON_EXISTENT"])
        graph.add_task(t1)
        with self.assertRaises(ValueError):
            graph.validate_graph()

    def test_10_task_scheduler_priority_and_concurrency(self):
        reg = AgentRegistry()
        reg.register(DummyTestAgent("agent.dummy"))
        scheduler = TaskScheduler(reg, max_concurrency=2)
        
        graph = TaskGraph()
        t_low = Task(task_id="T_LOW", task_type="DUMMY", description="Low", priority=TaskPriority.LOW)
        t_crit = Task(task_id="T_CRIT", task_type="DUMMY", description="Crit", priority=TaskPriority.CRITICAL)
        t_norm = Task(task_id="T_NORM", task_type="DUMMY", description="Norm", priority=TaskPriority.NORMAL)
        
        for t in [t_low, t_crit, t_norm]:
            graph.add_task(t)
            
        schedulable = scheduler.get_schedulable_tasks(graph)
        self.assertEqual(len(schedulable), 2) # max concurrency 2
        self.assertEqual(schedulable[0].task_id, "T_CRIT")
        self.assertEqual(schedulable[1].task_id, "T_NORM")

    def test_11_task_scheduler_resource_locking_conflict(self):
        reg = AgentRegistry()
        reg.register(DummyTestAgent("agent.dummy"))
        scheduler = TaskScheduler(reg, max_concurrency=4)
        
        graph = TaskGraph()
        t1 = Task(task_id="T1", task_type="DUMMY", description="1", metadata={"required_locks": ["asset.lock:001"]})
        t2 = Task(task_id="T2", task_type="DUMMY", description="2", metadata={"required_locks": ["asset.lock:001"]})
        
        graph.add_task(t1)
        graph.add_task(t2)
        
        schedulable = scheduler.get_schedulable_tasks(graph)
        self.assertEqual(len(schedulable), 2)
        
        # Acquire lock for T1
        scheduler.acquire_locks_for_task(t1)
        
        # Now T2 should be blocked due to lock conflict
        schedulable_after = scheduler.get_schedulable_tasks(graph)
        self.assertEqual(len(schedulable_after), 0)
        
        scheduler.release_locks_for_task(t1)
        schedulable_released = scheduler.get_schedulable_tasks(graph)
        self.assertEqual(len(schedulable_released), 2)

    def test_12_perception_agent_execution(self):
        agent = PerceptionAgent()
        context = AgentContext(
            orchestration_id="ORCH_01", job_id="JOB_01", task_id="T_PERC",
            asset_id="WP_TEST", semantic_id="weapon.test.001"
        )
        res = agent.execute({"reference_data": {"test": 1}, "prompt": "Cyberpunk rifle"}, context)
        self.assertTrue(res.success)
        self.assertIn("reference_report", res.outputs)
        self.assertAlmostEqual(res.metrics["confidence"], 0.96)

    def test_13_design_analysis_agent_execution(self):
        agent = DesignAnalysisAgent()
        context = AgentContext(
            orchestration_id="ORCH_01", job_id="JOB_01", task_id="T_VAS",
            asset_id="WP_TEST", semantic_id="weapon.test.001"
        )
        res = agent.execute({"reference_report": {"palette": {}}}, context)
        self.assertTrue(res.success)
        self.assertIn("visual_specification", res.outputs)

    def test_14_strategy_agent_execution(self):
        agent = StrategyAgent()
        context = AgentContext(
            orchestration_id="ORCH_01", job_id="JOB_01", task_id="T_MSP",
            asset_id="WP_TEST", semantic_id="weapon.test.001"
        )
        res = agent.execute({"visual_specification": {"target_style": "DARX"}}, context)
        self.assertTrue(res.success)
        self.assertEqual(res.outputs["modeling_plan"]["target_poly_budget"], 12000)

    def test_15_geometry_agent_execution_and_mutations(self):
        agent = GeometryAgent()
        context = AgentContext(
            orchestration_id="ORCH_01", job_id="JOB_01", task_id="T_GEOM",
            asset_id="WP_TEST", semantic_id="weapon.test.001"
        )
        res = agent.execute({"modeling_plan": {}}, context)
        self.assertTrue(res.success)
        self.assertEqual(len(res.mutations), 1)
        self.assertEqual(res.mutations[0].operation, "CREATE_GEOMETRY_COMPONENTS")
        self.assertEqual(res.mutations[0].semantic_id, "weapon.test.001")

    def test_16_material_agent_execution_and_pbr(self):
        agent = MaterialAgent()
        context = AgentContext(
            orchestration_id="ORCH_01", job_id="JOB_01", task_id="T_MAT",
            asset_id="WP_TEST", semantic_id="weapon.test.001"
        )
        res = agent.execute({"visual_specification": {}}, context)
        self.assertTrue(res.success)
        self.assertEqual(len(res.outputs["surface_result"]["materials"]), 4)

    def test_17_blender_execution_agent_assembly(self):
        agent = BlenderExecutionAgent()
        context = AgentContext(
            orchestration_id="ORCH_01", job_id="JOB_01", task_id="T_BLENDER",
            asset_id="WP_TEST", semantic_id="weapon.test.001"
        )
        res = agent.execute({
            "geometry_result": {"components": ["Receiver", "Barrel"]},
            "surface_result": {"materials": [{"name": "M_GunMetal"}]}
        }, context)
        self.assertTrue(res.success)
        self.assertIn("scene_state", res.outputs)
        self.assertEqual(res.outputs["scene_state"]["collision_created"], "UCX_WP_Vandal_01")

    def test_18_visual_critic_agent_quality_rubric_enforcement(self):
        agent = VisualCriticAgent()
        context = AgentContext(
            orchestration_id="ORCH_01", job_id="JOB_01", task_id="T_CRITIC",
            asset_id="WP_TEST", semantic_id="weapon.test.001"
        )
        # Normal pass
        res_pass = agent.execute({"scene_state": {}, "visual_specification": {}}, context)
        self.assertTrue(res_pass.outputs["critic_report"]["meets_threshold"])
        self.assertGreater(res_pass.outputs["visual_score"], 85.0)
        
        # Defect detected
        res_fail = agent.execute({
            "scene_state": {}, "visual_specification": {},
            "injected_defects": ["ROUGHNESS_ERROR"]
        }, context)
        self.assertFalse(res_fail.outputs["critic_report"]["meets_threshold"])
        self.assertEqual(len(res_fail.outputs["defects"]), 1)

    def test_19_qa_validator_agent_engine_readiness(self):
        agent = QAAgent()
        context = AgentContext(
            orchestration_id="ORCH_01", job_id="JOB_01", task_id="T_QA",
            asset_id="WP_TEST", semantic_id="weapon.test.001"
        )
        res = agent.execute({"scene_state": {}}, context)
        self.assertTrue(res.success)
        self.assertEqual(res.outputs["qa_report"]["readiness_status"], "READY")
        self.assertEqual(res.outputs["qa_report"]["checks"]["zero_duplicates"], True)

    def test_20_correction_agent_surgical_repair(self):
        agent = CorrectionAgent()
        context = AgentContext(
            orchestration_id="ORCH_01", job_id="JOB_01", task_id="T_CORR",
            asset_id="WP_TEST", semantic_id="weapon.test.001"
        )
        critic_report = {
            "defects": [{"defect_id": "DEF_001", "target": "WP_Vandal_Magazine", "severity": "MEDIUM"}]
        }
        res = agent.execute({"critic_report": critic_report}, context)
        self.assertTrue(res.success)
        self.assertEqual(res.outputs["correction_result"]["count"], 1)
        self.assertEqual(res.mutations[0].operation, "APPLY_SURGICAL_CORRECTION")

    def test_21_packaging_agent_bundle_and_delivery(self):
        agent = PackagingAgent()
        context = AgentContext(
            orchestration_id="ORCH_01", job_id="JOB_01", task_id="T_PKG",
            asset_id="WP_TEST", semantic_id="weapon.test.001"
        )
        res = agent.execute({"qa_report": {"is_valid": True}}, context)
        self.assertTrue(res.success)
        self.assertEqual(res.outputs["delivered_package"]["delivery_status"], "DELIVERY_VERIFIED")
        self.assertEqual(res.outputs["delivery_receipt"]["verified_hash_match"], True)

    def test_22_full_multi_agent_pipeline_execution(self):
        plan = self.api.create_plan(asset_id="WP_DarX_Vandal", semantic_id="weapon.darx.vandal.001")
        result = self.api.execute_plan(plan)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["completed_tasks"], 9)
        self.assertIn("T9_Packaging", result["results"])
        self.assertIn("T7_VisualCritic", result["results"])
        self.assertIn("T8_QA", result["results"])
        self.assertGreater(result["events_count"], 10)

    def test_23_iterative_critic_correction_loop(self):
        engine = OrchestrationEngine()
        plan = OrchestrationPlan(
            orchestration_id="ORCH_LOOP_TEST",
            objective="Test Critic -> Correction -> Re-evaluation Loop",
            asset_id="WP_DEFECTIVE",
            semantic_id="weapon.defective.001"
        )
        
        # Step 1: Critic 1 detects defect
        t1 = Task(
            task_id="T1_Critic1", task_type="VISUAL_CRITIC", description="Initial evaluation",
            inputs={"scene_state": {}, "visual_specification": {}, "injected_defects": ["ROUGHNESS_ERROR"]}
        )
        # Step 2: Correction
        t2 = Task(task_id="T2_Correction", task_type="CORRECTION", description="Surgical fix", dependencies=["T1_Critic1"])
        # Step 3: Critic 2 re-evaluates cleanly
        t3 = Task(
            task_id="T3_Critic2", task_type="VISUAL_CRITIC", description="Re-evaluation",
            dependencies=["T2_Correction"], inputs={"scene_state": {}, "visual_specification": {}}
        )
        # Step 4: QA Validator
        t4 = Task(task_id="T4_QA", task_type="QA_VALIDATOR", description="Final QA", dependencies=["T3_Critic2"], inputs={"scene_state": {}})
        
        for t in [t1, t2, t3, t4]:
            plan.task_graph.add_task(t)
            
        out = engine.execute_plan(plan)
        self.assertTrue(out["success"])
        self.assertEqual(out["completed_tasks"], 4)
        
        # Verify critic 1 detected defect and critic 2 cleared it
        c1_res = out["results"]["T1_Critic1"]
        self.assertFalse(c1_res.outputs["critic_report"]["meets_threshold"])
        
        c2_res = out["results"]["T3_Critic2"]
        self.assertTrue(c2_res.outputs["critic_report"]["meets_threshold"])

    def test_24_semantic_identity_preservation_across_agents(self):
        plan = self.api.create_plan(asset_id="WP_SEMANTIC_TEST", semantic_id="weapon.darx.unique.999")
        out = self.api.execute_plan(plan)
        self.assertTrue(out["success"])
        
        # Check all agent results preserve the exact semantic_id
        for task_id, res in out["results"].items():
            for m in res.mutations:
                self.assertEqual(m.semantic_id, "weapon.darx.unique.999")

    def test_25_digital_twin_mutation_attribution(self):
        plan = self.api.create_plan(asset_id="WP_DT_TEST", semantic_id="weapon.darx.dt.001")
        out = self.api.execute_plan(plan)
        
        mutations = []
        for t_id, r in out["results"].items():
            mutations.extend(r.mutations)
            
        self.assertGreaterEqual(len(mutations), 3)
        ops = [m.operation for m in mutations]
        self.assertIn("CREATE_GEOMETRY_COMPONENTS", ops)
        self.assertIn("ASSIGN_PBR_MATERIALS", ops)
        self.assertIn("ASSEMBLE_BLENDER_SCENE", ops)

if __name__ == "__main__":
    unittest.main()
