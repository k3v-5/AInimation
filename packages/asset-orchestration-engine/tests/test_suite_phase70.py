import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.long_running_job_recovery import (
    LongRunningJobAPI, JobType, JobState, JobPriority,
    ErrorCategory, RecoveryAction, JobError
)

class TestLongRunningJobRecoveryPhase70(unittest.TestCase):
    def setUp(self):
        self.job_api = LongRunningJobAPI()

    def test_01_case_a_full_job_lifecycle(self):
        """Case A: Ciclo completo: Creación -> Inicio -> Checkpointing -> Completado."""
        job = self.job_api.create_and_start_job(JobType.FULL_PIPELINE, "barrel_01", "barrel_01.root")
        self.assertEqual(job.state, JobState.RUNNING)

        ckpt1 = self.job_api.create_checkpoint(job.identity.job_id, "PERCEPTION", "F55_DONE", "HASH_F55", progress_percent=20.0)
        self.assertEqual(ckpt1.phase, "PERCEPTION")

        ckpt2 = self.job_api.create_checkpoint(job.identity.job_id, "GEOMETRY", "F58_DONE", "HASH_F58", progress_percent=50.0)
        self.assertEqual(ckpt2.previous_checkpoint_id, ckpt1.checkpoint_id)

        completed_job = self.job_api.complete_job(job.identity.job_id)
        self.assertEqual(completed_job.state, JobState.COMPLETED)
        self.assertEqual(completed_job.progress.overall_percent, 100.0)

    def test_02_case_b_crash_detection_and_startup_recovery(self):
        """Case B: Detección y recuperación automática de jobs interrumpidos por crash."""
        job = self.job_api.create_and_start_job(JobType.ASSET_GENERATION, "barrel_crash", "barrel_crash.root")
        _ = self.job_api.create_checkpoint(job.identity.job_id, "SURFACE", "F59_DONE", "HASH_F59", progress_percent=60.0)
        
        # Simular crash (job permanece en RUNNING en el store)
        reports = self.job_api.recover_interrupted_jobs()
        self.assertEqual(len(reports), 1)
        self.assertTrue(reports[0].recovered)
        self.assertEqual(reports[0].final_state, JobState.RESUMING)

    def test_03_case_c_pause_and_safe_resume(self):
        """Case C: Pausa segura y reanudación con actualización de worker y heartbeat."""
        job = self.job_api.create_and_start_job(JobType.ASSET_OPTIMIZATION, "barrel_pause", "barrel_pause.root")
        paused = self.job_api.pause_job(job.identity.job_id)
        self.assertEqual(paused.state, JobState.PAUSED)

        resumed = self.job_api.resume_job(job.identity.job_id, worker_id="WORKER_RELOADED")
        self.assertEqual(resumed.state, JobState.RUNNING)
        self.assertEqual(resumed.worker_id, "WORKER_RELOADED")

    def test_04_case_d_cooperative_cancellation(self):
        """Case D: Cancelación cooperativa de un job en ejecución."""
        job = self.job_api.create_and_start_job(JobType.PACKAGE_BUILD, "barrel_cancel", "barrel_cancel.root")
        cancelled = self.job_api.cancel_job(job.identity.job_id)
        self.assertEqual(cancelled.state, JobState.CANCELLED)

    def test_05_case_e_retry_decision_engine(self):
        """Case E: El motor de decisión de recovery clasifica errores reintentables y fatales."""
        from src.long_running_job_recovery.recovery.recovery_decision_engine import RecoveryDecisionEngine
        job = self.job_api.create_and_start_job(JobType.ASSET_GENERATION, "barrel_err", "barrel_err.root")
        
        err_transient = JobError("E1", "BlenderTimeout", ErrorCategory.BLENDER_ERROR, "Socket timeout", "GEOMETRY", "F58", True)
        action1 = RecoveryDecisionEngine.decide_recovery(job, err_transient)
        self.assertEqual(action1, RecoveryAction.RETRY)

        err_fatal = JobError("E2", "FatalCrash", ErrorCategory.USER_ERROR, "Invalid Prompt", "PERCEPTION", "F55", False)
        action2 = RecoveryDecisionEngine.decide_recovery(job, err_fatal)
        self.assertEqual(action2, RecoveryAction.FAIL)

    def test_06_case_f_checkpoint_hash_chain_integrity(self):
        """Case F: La cadena de checkpoints preserva referencias cruzadas."""
        job = self.job_api.create_and_start_job(JobType.ASSET_GENERATION, "barrel_chain", "barrel_chain.root")
        c1 = self.job_api.create_checkpoint(job.identity.job_id, "P1", "S1", "H1")
        c2 = self.job_api.create_checkpoint(job.identity.job_id, "P2", "S2", "H2")
        self.assertEqual(c2.previous_checkpoint_id, c1.checkpoint_id)

    def test_07_case_g_heartbeat_and_stale_lease_detection(self):
        """Case G: Detección de leases expirados por falta de heartbeat."""
        from src.long_running_job_recovery.scheduler.job_scheduler import JobScheduler
        store = self.job_api._service.store
        scheduler = JobScheduler(store, lease_duration_sec=0.01)
        job = self.job_api.create_and_start_job(JobType.ASSET_GENERATION, "barrel_lease", "barrel_lease.root")
        job.last_heartbeat = 0.0 # Forzar expirado
        store.save_job(job)

        stale = scheduler.detect_stale_leases()
        self.assertIn(job.identity.job_id, [j.identity.job_id for j in stale])

    def test_08_case_h_priority_scheduling(self):
        """Case H: Planificador ordena por prioridad (CRITICAL antes de LOW)."""
        store = self.job_api._service.store
        scheduler = self.job_api._service.scheduler
        
        j_low = self.job_api._service.create_and_start_job(JobType.ASSET_GENERATION, "barrel_low", "b.root", priority=JobPriority.LOW)
        j_low.state = JobState.QUEUED
        store.save_job(j_low)

        j_crit = self.job_api._service.create_and_start_job(JobType.ASSET_GENERATION, "barrel_crit", "b.root", priority=JobPriority.CRITICAL)
        j_crit.state = JobState.QUEUED
        store.save_job(j_crit)

        acquired = scheduler.acquire_next_job("WORKER_TEST")
        self.assertEqual(acquired.identity.job_id, j_crit.identity.job_id)

    def test_09_case_i_manual_recovery_from_checkpoint(self):
        """Case I: Recuperación manual desde un checkpoint específico."""
        job = self.job_api.create_and_start_job(JobType.ASSET_GENERATION, "barrel_man", "barrel_man.root")
        c1 = self.job_api.create_checkpoint(job.identity.job_id, "PHASE_A", "STEP_A", "HA")
        _ = self.job_api.create_checkpoint(job.identity.job_id, "PHASE_B", "STEP_B", "HB")

        report = self.job_api.recover_job_manually(job.identity.job_id, checkpoint_id=c1.checkpoint_id)
        self.assertTrue(report.recovered)
        self.assertEqual(report.checkpoint_used, c1.checkpoint_id)

    def test_10_case_j_export_recoverable_job_for_f71(self):
        """Case J: Exportación de RecoverableJob para orquestación multi-agente en F71."""
        job = self.job_api.create_and_start_job(JobType.FULL_PIPELINE, "barrel_f71", "barrel_f71.root")
        self.job_api.create_checkpoint(job.identity.job_id, "READINESS", "F68_DONE", "HASH_F68", progress_percent=90.0)
        
        rec_job = self.job_api.export_recoverable_job(job.identity.job_id)
        self.assertIsNotNone(rec_job)
        self.assertEqual(rec_job.current_phase, "READINESS")
        self.assertEqual(rec_job.progress.overall_percent, 90.0)

    def test_11_progress_tracking_no_false_completion(self):
        """Test 11: Progreso no marca 100% antes de estado COMPLETED."""
        job = self.job_api.create_and_start_job(JobType.ASSET_GENERATION, "barrel_prog", "b.root")
        self.assertLess(job.progress.overall_percent, 100.0)

    def test_12_validation_clean_result(self):
        """Test 12: Validación de job en estado correcto retorna is_valid = True."""
        job = self.job_api.create_and_start_job(JobType.ASSET_GENERATION, "barrel_val", "b.root")
        val = self.job_api.validate_job(job)
        self.assertTrue(val.is_valid)

    def test_13_preservation_of_ids(self):
        """Test 13: Preservación de asset_id y semantic_id."""
        job = self.job_api.create_and_start_job(JobType.ASSET_GENERATION, "barrel_01", "barrel_01.root")
        self.assertEqual(job.identity.asset_id, "barrel_01")
        self.assertEqual(job.identity.semantic_id, "barrel_01.root")

    def test_14_event_log_immutability(self):
        """Test 14: Registro inmutable de eventos durante la vida del job."""
        job = self.job_api.create_and_start_job(JobType.ASSET_GENERATION, "barrel_evt", "b.root")
        self.job_api.create_checkpoint(job.identity.job_id, "P1", "S1", "H1")
        self.job_api.complete_job(job.identity.job_id)
        events = self.job_api._service.store.get_events(job.identity.job_id)
        self.assertGreaterEqual(len(events), 3)

    def test_15_optimistic_concurrency_state_version(self):
        """Test 15: Incremento de state_version en cada actualización de estado."""
        job = self.job_api.create_and_start_job(JobType.ASSET_GENERATION, "barrel_ver", "b.root")
        v1 = job.state_version
        self.job_api.create_checkpoint(job.identity.job_id, "P1", "S1", "H1")
        self.assertGreater(job.state_version, v1)

    def test_16_recovery_report_structure(self):
        """Test 16: Estructura y campos del RecoveryReport."""
        job = self.job_api.create_and_start_job(JobType.ASSET_GENERATION, "barrel_rep", "b.root")
        self.job_api.create_checkpoint(job.identity.job_id, "P1", "S1", "H1")
        report = self.job_api.recover_job_manually(job.identity.job_id)
        self.assertEqual(report.job_id, job.identity.job_id)
        self.assertTrue(report.recovered)

    def test_17_isolation_between_multiple_jobs(self):
        """Test 17: Aislamiento entre múltiples jobs concurrentes."""
        j1 = self.job_api.create_and_start_job(JobType.ASSET_GENERATION, "barrel_j1", "b1.root")
        j2 = self.job_api.create_and_start_job(JobType.PACKAGE_BUILD, "barrel_j2", "b2.root")
        self.job_api.cancel_job(j1.identity.job_id)
        self.assertEqual(j1.state, JobState.CANCELLED)
        self.assertEqual(j2.state, JobState.RUNNING)

    def test_18_job_type_enumeration(self):
        """Test 18: Enumeración de tipos de jobs soportados."""
        self.assertEqual(JobType.FULL_PIPELINE.value, "FULL_PIPELINE")
        self.assertEqual(JobType.ENGINE_PREPARATION.value, "ENGINE_PREPARATION")

    def test_19_heartbeat_renewal(self):
        """Test 19: Renovación exitosa de heartbeat."""
        job = self.job_api.create_and_start_job(JobType.ASSET_GENERATION, "barrel_hb", "b.root", worker_id="WORKER_A")
        ok = self.job_api._service.scheduler.heartbeat(job.identity.job_id, "WORKER_A")
        self.assertTrue(ok)

    def test_20_end_to_end_job_and_recovery_contract_for_f71(self):
        """Test 20: Flujo E2E Completo: Prompt -> F56 -> F57 -> F58 -> F59 -> F60 -> F61 -> F62 -> F63 -> F64 -> F65 -> F66 -> F67 -> F68 -> F69 -> F70 -> Listo para F71 Multi-Agent Layer."""
        job = self.job_api.create_and_start_job(JobType.FULL_PIPELINE, "barrel_hero", "barrel_hero.root")
        self.job_api.create_checkpoint(job.identity.job_id, "F67_OPT", "OPTIMIZE", "HASH_OPT", progress_percent=70.0)
        self.job_api.create_checkpoint(job.identity.job_id, "F68_READINESS", "PREPARE", "HASH_READY", progress_percent=85.0)
        self.job_api.create_checkpoint(job.identity.job_id, "F69_PACKAGING", "DELIVER", "HASH_PKG", progress_percent=95.0)
        completed = self.job_api.complete_job(job.identity.job_id)
        
        rec = self.job_api.export_recoverable_job(job.identity.job_id)
        self.assertEqual(completed.state, JobState.COMPLETED)
        self.assertEqual(rec.state, JobState.COMPLETED)
        self.assertEqual(rec.progress.overall_percent, 100.0)

if __name__ == "__main__":
    unittest.main()
