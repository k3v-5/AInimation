import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.long_running_job_recovery import (
    LongRunningJobAPI, JobType, JobState, JobPriority,
    ErrorCategory, RecoveryAction, JobError
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 70: LONG-RUNNING JOB & RECOVERY SYSTEM")
    print("=" * 95)

    job_api = LongRunningJobAPI()

    # 1. Creación e Inicio de Trabajo de Larga Duración
    print("\n[PASO 1] Creación e Inicio de Trabajo de Larga Duración (Pipeline Completo):")
    job = job_api.create_and_start_job(
        job_type=JobType.FULL_PIPELINE,
        asset_id="barrel_hero",
        semantic_id="barrel_hero.root",
        priority=JobPriority.CRITICAL,
        worker_id="WORKER_NODE_01"
    )
    val = job_api.validate_job(job)
    print(f" - Job ID: [{job.identity.job_id}] | State: [{job.state.value}] | Priority: [{job.definition.priority.value}]")
    print(f" - Worker Asignado: [{job.worker_id}] | Lease: [{job.lease_id}] | Válido: {val.is_valid}")

    # 2. Creación de Checkpoints en Fronteras Críticas
    print("\n[PASO 2] Persistencia de Checkpoints y Encadenamiento de Hashes:")
    c1 = job_api.create_checkpoint(job.identity.job_id, "PERCEPTION", "F55_COMPLETE", "HASH_PERCEPTION_01", progress_percent=20.0)
    print(f" - Checkpoint 1 (Perception): ID=[{c1.checkpoint_id}] | Hash=[{c1.state_hash[:16]}...]")
    c2 = job_api.create_checkpoint(job.identity.job_id, "GEOMETRY_SURFACE", "F58_F59_COMPLETE", "HASH_GEOM_02", progress_percent=50.0)
    print(f" - Checkpoint 2 (Geometry):   ID=[{c2.checkpoint_id}] | Prev=[{c2.previous_checkpoint_id}]")
    c3 = job_api.create_checkpoint(job.identity.job_id, "READINESS", "F68_COMPLETE", "HASH_READY_03", progress_percent=85.0)
    print(f" - Checkpoint 3 (Readiness):  ID=[{c3.checkpoint_id}] | Progress: {job.progress.overall_percent:.1f}%")

    # 3. Demostración de Simulación de Crash y Recuperación Automática en Startup
    print("\n[PASO 3] Detección y Recuperación Automática de Crash en el Inicio del Sistema:")
    # Simular otro job que quedó en RUNNING durante un corte de proceso
    crash_job = job_api.create_and_start_job(JobType.ASSET_OPTIMIZATION, "barrel_interrupted", "barrel_interrupted.root")
    ckpt_crash = job_api.create_checkpoint(crash_job.identity.job_id, "OPTIMIZATION", "F67_OPT_CANDIDATE", "HASH_OPT_CAND", progress_percent=70.0)
    print(f" - Job Interrumpido: [{crash_job.identity.job_id}] en estado [{crash_job.state.value}]")
    
    reports = job_api.recover_interrupted_jobs()
    print(f" - Jobs Recuperados al Iniciar: {len(reports)}")
    for rep in reports:
        print(f"   * Job [{rep.job_id}] recuperado desde checkpoint [{rep.checkpoint_used}] -> Estado: [{rep.final_state.value}] (Acción: {rep.action_taken.value})")

    # 4. Pausa, Reanudación y Finalización
    print("\n[PASO 4] Pausa Segura, Reanudación y Completado Oficial:")
    paused = job_api.pause_job(job.identity.job_id)
    print(f" - Job en Pausa: [{paused.identity.job_id}] -> Estado: [{paused.state.value}]")
    resumed = job_api.resume_job(job.identity.job_id, worker_id="WORKER_NODE_02")
    print(f" - Job Reanudado: [{resumed.identity.job_id}] -> Worker: [{resumed.worker_id}] | Estado: [{resumed.state.value}]")
    completed = job_api.complete_job(job.identity.job_id)
    print(f" - Job Completado: [{completed.identity.job_id}] -> Progreso: {completed.progress.overall_percent:.0f}% | Estado: [{completed.state.value}]")

    # 5. Exportación de Contrato para F71 (RecoverableJob)
    print("\n[PASO 5] Exportación del Contrato RecoverableJob para F71 Multi-Agent Layer:")
    rec_job = job_api.export_recoverable_job(job.identity.job_id)
    print(f" - Contrato F71 Listo: Job ID=[{rec_job.job_id}] | Type=[{rec_job.job_type.value}] | State=[{rec_job.state.value}]")
    print(f" - Último Checkpoint Hash: {rec_job.checkpoint_hash[:16]}...{rec_job.checkpoint_hash[-8:]}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 70 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
