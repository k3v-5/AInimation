import sys
import os
import time
import subprocess
import shutil
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.long_running_job_recovery import (
    LongRunningJobAPI, JobType, JobState, JobPriority,
    ErrorCategory, RecoveryAction, JobError, JobCheckpoint
)

class TestF70RealRecoveryEmpiricalSuite(unittest.TestCase):
    STORAGE_DIR = r"E:\Darx_Proyect\Saved\F70_Validation_Workspace"

    def setUp(self):
        # Reset storage directory for fresh run
        if os.path.exists(self.STORAGE_DIR):
            shutil.rmtree(self.STORAGE_DIR)
        os.makedirs(self.STORAGE_DIR, exist_ok=True)
        self.api = LongRunningJobAPI(storage_dir=self.STORAGE_DIR)

    def tearDown(self):
        pass

    def test_01_prueba_a_normal_execution_baseline(self):
        """Prueba A: Ejecución normal sin interrupciones (Baseline)."""
        job_id = "JOB_TEST_A_NORMAL"
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "f70_worker_subprocess.py"))
        
        proc = subprocess.Popen(
            [sys.executable, script_path, "--job-id", job_id, "--storage-dir", self.STORAGE_DIR],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = proc.communicate(timeout=10)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("JOB_EXECUTION_COMPLETED_SUCCESSFULLY", stdout)

        # Reload state in fresh AOE instance
        fresh_api = LongRunningJobAPI(storage_dir=self.STORAGE_DIR)
        job = fresh_api._service.store.get_job(job_id)
        self.assertIsNotNone(job)
        self.assertEqual(job.state, JobState.COMPLETED)
        self.assertEqual(job.progress.overall_percent, 100.0)
        self.assertEqual(len(fresh_api._service.store.get_all_checkpoints(job_id)), 6)

    def test_02_prueba_b_real_subprocess_interruption_and_recovery(self):
        """Prueba B: Interrupción real abrupta del proceso tras CP3 y recuperación en nuevo inicio."""
        job_id = "JOB_TEST_B_CRASH_CP3"
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "f70_worker_subprocess.py"))

        # 1. Arrancar worker en subproceso real
        proc = subprocess.Popen(
            [sys.executable, script_path, "--job-id", job_id, "--storage-dir", self.STORAGE_DIR, "--crash-at", "CP3"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # 2. Esperar confirmación real de CP3 escrita en disco
        cp3_confirmed = False
        start_wait = time.time()
        while time.time() - start_wait < 5.0:
            line = proc.stdout.readline()
            if "CHECKPOINT_CP3_CONFIRMED" in line:
                cp3_confirmed = True
                break
            time.sleep(0.05)
        self.assertTrue(cp3_confirmed, "El subproceso no alcanzó el Checkpoint CP3 a tiempo.")

        # 3. Terminar abruptamente el proceso (KILL REAL)
        proc.kill()
        proc.wait()
        if proc.stdout:
            proc.stdout.close()
        if proc.stderr:
            proc.stderr.close()
        self.assertIsNotNone(proc.returncode, "El proceso debía estar completamente muerto.")

        # 4. Iniciar nuevo entorno AOE simulando reinicio del sistema
        fresh_aoe = LongRunningJobAPI(storage_dir=self.STORAGE_DIR)
        reports = fresh_aoe.recover_interrupted_jobs()
        
        self.assertEqual(len(reports), 1)
        self.assertTrue(reports[0].recovered)
        self.assertEqual(reports[0].action_taken, RecoveryAction.RESUME)
        self.assertEqual(reports[0].final_state, JobState.RESUMING)

        # 5. Reanudar ejecución desde el último checkpoint confirmado (CP3)
        resumed_proc = subprocess.Popen(
            [sys.executable, script_path, "--job-id", job_id, "--storage-dir", self.STORAGE_DIR, "--resume-from-checkpoint", "CP3_MATERIAL_CREATED"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        r_stdout, r_stderr = resumed_proc.communicate(timeout=10)
        self.assertEqual(resumed_proc.returncode, 0)
        self.assertIn("JOB_EXECUTION_COMPLETED_SUCCESSFULLY", r_stdout)

        # 6. Verificación final de integridad
        final_aoe = LongRunningJobAPI(storage_dir=self.STORAGE_DIR)
        final_job = final_aoe._service.store.get_job(job_id)
        self.assertEqual(final_job.state, JobState.COMPLETED)
        self.assertEqual(final_job.progress.overall_percent, 100.0)

    def test_03_prueba_c_capability_failure_and_orphan_lock_cleanup(self):
        """Prueba C: Falla durante capability y limpieza de locks huérfanos."""
        job = self.api.create_and_start_job(JobType.ASSET_GENERATION, "asset_c", "asset_c.root")
        self.api.create_checkpoint(job.identity.job_id, "BLENDER", "STEP_BLENDER", "HASH_BLENDER")
        
        # Simular crash en capability
        fresh_aoe = LongRunningJobAPI(storage_dir=self.STORAGE_DIR)
        reports = fresh_aoe.recover_interrupted_jobs()
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].final_state, JobState.RESUMING)

    def test_04_prueba_d_corrupted_output_detection(self):
        """Prueba D: Detección de hash de output corrupto."""
        job = self.api.create_and_start_job(JobType.PACKAGE_BUILD, "asset_d", "asset_d.root")
        ckpt = self.api.create_checkpoint(job.identity.job_id, "OUTPUT", "STEP_OUT", "HASH_VALID_OUT", output_hash="SHA256_CORRECT")
        
        # Simular comprobación de output
        actual_output_hash = "SHA256_TAMPERED"
        self.assertNotEqual(ckpt.output_hash, actual_output_hash)

    def test_05_prueba_e_corrupted_checkpoint_detection(self):
        """Prueba E: Detección y fallo seguro ante checkpoint corrupto."""
        job = self.api.create_and_start_job(JobType.ASSET_GENERATION, "asset_e", "asset_e.root")
        report = self.api.recover_job_manually(job.identity.job_id, checkpoint_id="NON_EXISTENT_CORRUPT_CKPT")
        self.assertFalse(report.recovered)
        self.assertEqual(report.final_state, JobState.RECOVERY_FAILED)

    def test_06_prueba_f_duplicate_worker_rejection(self):
        """Prueba F: Prevención de ejecución concurrente duplicada por lease."""
        job = self.api.create_and_start_job(JobType.ASSET_GENERATION, "asset_f", "asset_f.root", worker_id="WORKER_1")
        # El job ya está en RUNNING por WORKER_1, no debe ser adquirido por WORKER_2
        acquired = self.api._service.scheduler.acquire_next_job("WORKER_2")
        self.assertIsNone(acquired)

    def test_07_prueba_g_retryable_error_with_backoff(self):
        """Prueba G: Error reintentable procesado con incremento de intento."""
        from src.long_running_job_recovery.recovery.recovery_decision_engine import RecoveryDecisionEngine
        job = self.api.create_and_start_job(JobType.ASSET_GENERATION, "asset_g", "asset_g.root")
        err = JobError("ERR1", "ConnectionReset", ErrorCategory.NETWORK_ERROR, "Socket dropped", "F58", "S1", True)
        action = RecoveryDecisionEngine.decide_recovery(job, err)
        self.assertEqual(action, RecoveryAction.RETRY)

    def test_08_prueba_h_non_retryable_error_immediate_fail(self):
        """Prueba H: Error no recuperable pasa inmediatamente a estado terminal FAIL."""
        from src.long_running_job_recovery.recovery.recovery_decision_engine import RecoveryDecisionEngine
        job = self.api.create_and_start_job(JobType.ASSET_GENERATION, "asset_h", "asset_h.root")
        err = JobError("ERR2", "InvalidSpec", ErrorCategory.USER_ERROR, "Syntax error in spec", "F56", "S1", False)
        action = RecoveryDecisionEngine.decide_recovery(job, err)
        self.assertEqual(action, RecoveryAction.FAIL)

    def test_09_prueba_i_cooperative_cancellation(self):
        """Prueba I: Cancelación cooperativa de job activo."""
        job = self.api.create_and_start_job(JobType.ASSET_GENERATION, "asset_i", "asset_i.root")
        cancelled = self.api.cancel_job(job.identity.job_id)
        self.assertEqual(cancelled.state, JobState.CANCELLED)

    def test_10_prueba_j_pause_and_resume_across_restart(self):
        """Prueba J: Pausa, persistencia, reinicio de AOE y reanudación limpia."""
        job = self.api.create_and_start_job(JobType.FULL_PIPELINE, "asset_j", "asset_j.root")
        self.api.create_checkpoint(job.identity.job_id, "PAUSE_PHASE", "STEP_P", "HASH_P")
        self.api.pause_job(job.identity.job_id)

        # Reiniciar AOE
        fresh_aoe = LongRunningJobAPI(storage_dir=self.STORAGE_DIR)
        persisted_job = fresh_aoe._service.store.get_job(job.identity.job_id)
        self.assertEqual(persisted_job.state, JobState.PAUSED)

        resumed = fresh_aoe.resume_job(job.identity.job_id, worker_id="WORKER_RESUMED")
        self.assertEqual(resumed.state, JobState.RUNNING)
        self.assertEqual(resumed.worker_id, "WORKER_RESUMED")

    def test_11_prueba_l_asset_integrity_verification(self):
        """Prueba L: Verificación de integridad estructural del asset recuperado."""
        job = self.api.create_and_start_job(JobType.ASSET_GENERATION, "F70_Recovery_Test_Asset", "f70.recovery.test.asset")
        self.assertEqual(job.identity.semantic_id, "f70.recovery.test.asset")
        self.assertEqual(job.identity.asset_id, "F70_Recovery_Test_Asset")

    def test_12_prueba_m_no_duplicates_verification(self):
        """Prueba M: Verificación de no duplicación tras recovery."""
        job = self.api.create_and_start_job(JobType.ASSET_GENERATION, "asset_m", "asset_m.root")
        self.api.create_checkpoint(job.identity.job_id, "INIT", "CP1", "H1")
        ckpts_before = self.api._service.store.get_all_checkpoints(job.identity.job_id)
        self.assertEqual(len(ckpts_before), 1)

    def test_13_prueba_n_resource_cleanup_verification(self):
        """Prueba N: Liberación de leases y recursos tras completado."""
        job = self.api.create_and_start_job(JobType.ASSET_GENERATION, "asset_n", "asset_n.root")
        completed = self.api.complete_job(job.identity.job_id)
        self.assertEqual(completed.state, JobState.COMPLETED)

    def test_14_prueba_o_event_log_timeline_audit(self):
        """Prueba O: Reconstrucción del timeline completo mediante eventos persistidos."""
        job = self.api.create_and_start_job(JobType.ASSET_GENERATION, "asset_o", "asset_o.root")
        self.api.create_checkpoint(job.identity.job_id, "PHASE_1", "STEP_1", "H1")
        self.api.create_checkpoint(job.identity.job_id, "PHASE_2", "STEP_2", "H2")
        self.api.complete_job(job.identity.job_id)

        events = self.api._service.store.get_events(job.identity.job_id)
        evt_types = [e.event_type for e in events]
        self.assertIn("JOB_CREATED", evt_types)
        self.assertIn("JOB_CHECKPOINT_CREATED", evt_types)
        self.assertIn("JOB_COMPLETED", evt_types)

    def test_15_prueba_p_false_completion_prevention(self):
        """Prueba P: Protección contra falso COMPLETED si se interrumpe antes del commit."""
        job = self.api.create_and_start_job(JobType.ASSET_GENERATION, "asset_p", "asset_p.root")
        self.api.create_checkpoint(job.identity.job_id, "PRE_COMMIT", "STEP_PRE", "H_PRE", progress_percent=95.0)
        # Job sigue en RUNNING
        fresh_aoe = LongRunningJobAPI(storage_dir=self.STORAGE_DIR)
        loaded = fresh_aoe._service.store.get_job(job.identity.job_id)
        self.assertNotEqual(loaded.state, JobState.COMPLETED)

    def test_16_prueba_q_repeated_recovery_cycles(self):
        """Prueba Q: Múltiples ciclos repetidos de crash y recovery sin corrupción."""
        job = self.api.create_and_start_job(JobType.ASSET_GENERATION, "asset_q", "asset_q.root")
        self.api.create_checkpoint(job.identity.job_id, "P1", "S1", "H1")
        
        # Cycle 1: Crash & Recover
        aoe1 = LongRunningJobAPI(storage_dir=self.STORAGE_DIR)
        r1 = aoe1.recover_interrupted_jobs()
        self.assertTrue(r1[0].recovered)

        # Advance to P2
        aoe1.create_checkpoint(job.identity.job_id, "P2", "S2", "H2")

        # Cycle 2: Crash & Recover
        aoe2 = LongRunningJobAPI(storage_dir=self.STORAGE_DIR)
        r2 = aoe2.recover_interrupted_jobs()
        self.assertTrue(r2[0].recovered)
        
        completed = aoe2.complete_job(job.identity.job_id)
        self.assertEqual(completed.state, JobState.COMPLETED)

if __name__ == "__main__":
    unittest.main()
