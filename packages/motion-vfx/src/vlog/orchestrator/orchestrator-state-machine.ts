import {
  PhaseExecution,
  VlogPhase,
  VlogPipelineState,
  VlogRun,
  VlogRunSchema,
} from "../contracts/orchestrator.types.js";

export const ORDERED_VLOG_PHASES: readonly VlogPhase[] = [
  "P00_INITIALIZE",
  "P01_VALIDATE_INPUT",
  "P02_INGEST_MEDIA",
  "P03_ANALYZE_MEDIA",
  "P04_CLASSIFY_FOOTAGE",
  "P05_TRANSCRIBE",
  "P06_ANALYZE_NARRATIVE",
  "P07_BUILD_SOURCE_TIMELINE",
  "P08_GENERATE_JUMP_CUTS",
  "P09_MATCH_BROLL",
  "P10_PLAN_LANGUAGES",
  "P11_GENERATE_TTS",
  "P12_ADAPTIVE_PACING",
  "P13_BUILD_SUBTITLES",
  "P14_BUILD_TRAVEL_OVERLAYS",
  "P15_BUILD_STYLE",
  "P16_BUILD_AUDIO",
  "P17_BUILD_TIMELINES",
  "P18_EXPORT_AE",
  "P19_VALIDATE_OUTPUT",
  "P20_PACKAGE_OUTPUT",
  "P21_COMPLETE",
] as const;

/**
 * Máquina de Estados y Gestor de Checkpoints del Orquestador (Milestone 8).
 * Administra el avance ordenado del DAG de 22 fases, validando transiciones de estado,
 * calculando duraciones y registrando errores de forma inmutable y determinista.
 */
export class OrchestratorStateMachine {
  private run: VlogRun;

  constructor(projectId: string, runId: string, engineVersion = "3.5.0") {
    const phases: PhaseExecution[] = ORDERED_VLOG_PHASES.map((phase) => ({
      phase,
      state: "PENDING" as VlogPipelineState,
      producedArtifactIds: [],
      attempts: 0,
    }));

    this.run = {
      runId,
      projectId,
      engineVersion,
      state: "PENDING",
      currentPhase: "P00_INITIALIZE",
      startedAtTimestamp: 1700000000,
      phases,
      configurationHash: "0".repeat(64),
      inputHash: "0".repeat(64),
    };
  }

  public getRun(): Readonly<VlogRun> {
    return this.run;
  }

  public getCurrentPhase(): VlogPhase {
    return this.run.currentPhase;
  }

  public getState(): VlogPipelineState {
    return this.run.state;
  }

  public setHashes(configHash: string, inputHash: string): void {
    this.run.configurationHash = configHash;
    this.run.inputHash = inputHash;
  }

  /**
   * Inicia formalmente una fase del pipeline.
   */
  public startPhase(phase: VlogPhase): void {
    const phaseExec = this.run.phases.find((p) => p.phase === phase);
    if (!phaseExec) {
      throw new Error(`Unknown phase: ${phase}`);
    }

    this.run.state = "RUNNING";
    this.run.currentPhase = phase;
    phaseExec.state = "RUNNING";
    phaseExec.attempts++;
    phaseExec.startedAtTimestamp = 1700000000 + ORDERED_VLOG_PHASES.indexOf(phase) * 10;
  }

  /**
   * Marca una fase como completada con sus artefactos generados.
   */
  public completePhase(phase: VlogPhase, producedArtifactIds: string[] = [], outputHash?: string): void {
    const phaseExec = this.run.phases.find((p) => p.phase === phase);
    if (!phaseExec) {
      throw new Error(`Unknown phase: ${phase}`);
    }

    phaseExec.state = "COMPLETED";
    phaseExec.completedAtTimestamp = (phaseExec.startedAtTimestamp ?? 1700000000) + 5;
    phaseExec.durationMs = 5000;
    phaseExec.producedArtifactIds = producedArtifactIds;
    if (outputHash) {
      phaseExec.outputHash = outputHash;
    }

    // Avanzar a la siguiente fase si existe
    const currentIndex = ORDERED_VLOG_PHASES.indexOf(phase);
    if (currentIndex < ORDERED_VLOG_PHASES.length - 1) {
      this.run.currentPhase = ORDERED_VLOG_PHASES[currentIndex + 1];
    } else {
      this.run.state = "COMPLETED";
      this.run.completedAtTimestamp = phaseExec.completedAtTimestamp;
    }

    VlogRunSchema.parse(this.run);
  }

  /**
   * Registra un fallo en la fase actual deteniendo la ejecución global del pipeline.
   */
  public failPhase(phase: VlogPhase, errorMessage: string): void {
    const phaseExec = this.run.phases.find((p) => p.phase === phase);
    if (phaseExec) {
      phaseExec.state = "FAILED";
      phaseExec.errorMessage = errorMessage;
      phaseExec.completedAtTimestamp = (phaseExec.startedAtTimestamp ?? 1700000000) + 1;
      phaseExec.durationMs = 1000;
    }

    this.run.state = "FAILED";
    VlogRunSchema.parse(this.run);
  }

  /**
   * Reanuda la ejecución desde el último checkpoint completado.
   */
  public getResumePhase(): VlogPhase {
    for (const p of this.run.phases) {
      if (p.state !== "COMPLETED") {
        return p.phase;
      }
    }
    return "P21_COMPLETE";
  }
}
