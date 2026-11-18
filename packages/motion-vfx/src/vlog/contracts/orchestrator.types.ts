import { z } from "zod";
import { SupportedLocaleSchema } from "./language.types.js";
import { SupportedLocale } from "./vlog.constants.js";

/** Las 22 fases del DAG del Production Orchestrator (Doc 20) */
export type VlogPhase =
  | "P00_INITIALIZE"
  | "P01_VALIDATE_INPUT"
  | "P02_INGEST_MEDIA"
  | "P03_ANALYZE_MEDIA"
  | "P04_CLASSIFY_FOOTAGE"
  | "P05_TRANSCRIBE"
  | "P06_ANALYZE_NARRATIVE"
  | "P07_BUILD_SOURCE_TIMELINE"
  | "P08_GENERATE_JUMP_CUTS"
  | "P09_MATCH_BROLL"
  | "P10_PLAN_LANGUAGES"
  | "P11_GENERATE_TTS"
  | "P12_ADAPTIVE_PACING"
  | "P13_BUILD_SUBTITLES"
  | "P14_BUILD_TRAVEL_OVERLAYS"
  | "P15_BUILD_STYLE"
  | "P16_BUILD_AUDIO"
  | "P17_BUILD_TIMELINES"
  | "P18_EXPORT_AE"
  | "P19_VALIDATE_OUTPUT"
  | "P20_PACKAGE_OUTPUT"
  | "P21_COMPLETE";

export const VlogPhaseSchema = z.enum([
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
]);

/** Estados del pipeline de producción */
export type VlogPipelineState =
  | "PENDING"
  | "RUNNING"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED"
  | "BLOCKED"
  | "SKIPPED";

export const VlogPipelineStateSchema = z.enum([
  "PENDING",
  "RUNNING",
  "COMPLETED",
  "FAILED",
  "CANCELLED",
  "BLOCKED",
  "SKIPPED",
]);

/** Contrato inmutable para artefactos producidos por fases intermedias */
export interface VlogArtifact {
  artifactId: string;
  type: string; // ej. "transcript", "voiceover", "timeline", "jsx_script"
  producerPhase: VlogPhase;
  engineVersion: string;
  inputHash: string;
  configurationHash: string;
  checksumSha256: string;
  dependencies: string[]; // IDs de artefactos de los que depende
  filePath: string;
  createdAtTimestamp: number;
}

export const VlogArtifactSchema = z.object({
  artifactId: z.string().min(1),
  type: z.string().min(1),
  producerPhase: VlogPhaseSchema,
  engineVersion: z.string().min(1),
  inputHash: z.string().min(64).max(64),
  configurationHash: z.string().min(64).max(64),
  checksumSha256: z.string().min(64).max(64),
  dependencies: z.array(z.string()),
  filePath: z.string().min(1),
  createdAtTimestamp: z.number().positive(),
});

/** Registro de ejecución de una fase individual */
export interface PhaseExecution {
  phase: VlogPhase;
  state: VlogPipelineState;
  startedAtTimestamp?: number;
  completedAtTimestamp?: number;
  durationMs?: number;
  inputHash?: string;
  outputHash?: string;
  producedArtifactIds: string[];
  attempts: number;
  errorMessage?: string;
}

export const PhaseExecutionSchema = z.object({
  phase: VlogPhaseSchema,
  state: VlogPipelineStateSchema,
  startedAtTimestamp: z.number().positive().optional(),
  completedAtTimestamp: z.number().positive().optional(),
  durationMs: z.number().nonnegative().optional(),
  inputHash: z.string().optional(),
  outputHash: z.string().optional(),
  producedArtifactIds: z.array(z.string()).default([]),
  attempts: z.number().int().min(0).default(0),
  errorMessage: z.string().optional(),
});

/** Registro global de ejecución (Production Run) */
export interface VlogRun {
  runId: string;
  projectId: string;
  engineVersion: string;
  state: VlogPipelineState;
  currentPhase: VlogPhase;
  startedAtTimestamp: number;
  completedAtTimestamp?: number;
  phases: PhaseExecution[];
  configurationHash: string;
  inputHash: string;
}

export const VlogRunSchema = z.object({
  runId: z.string().min(1),
  projectId: z.string().min(1),
  engineVersion: z.string().min(1),
  state: VlogPipelineStateSchema,
  currentPhase: VlogPhaseSchema,
  startedAtTimestamp: z.number().positive(),
  completedAtTimestamp: z.number().positive().optional(),
  phases: z.array(PhaseExecutionSchema),
  configurationHash: z.string().min(64).max(64),
  inputHash: z.string().min(64).max(64),
});

/** Manifiesto final de entrega de la producción multilingüe */
export interface VlogManifest {
  projectId: string;
  runId: string;
  engineVersion: string;
  createdAtTimestamp: number;
  configurationHash: string;
  productionHash: string;
  sourceLocale: SupportedLocale;
  targetLocales: SupportedLocale[];
  deliverables: {
    baseDirectory: string;
    audioMasters: Record<string, string>;
    subtitles: Record<string, string>;
    jsxScripts: Record<string, string>;
    reportPath: string;
  };
  artifacts: VlogArtifact[];
  validation: {
    passed: boolean;
    checkedAtTimestamp: number;
    metrics: {
      totalDurationSeconds: number;
      scenesCount: number;
      cutsCount: number;
      brollCount: number;
      overlaysCount: number;
    };
  };
}

export const VlogManifestSchema = z.object({
  projectId: z.string().min(1),
  runId: z.string().min(1),
  engineVersion: z.string().min(1),
  createdAtTimestamp: z.number().positive(),
  configurationHash: z.string().min(64).max(64),
  productionHash: z.string().min(64).max(64),
  sourceLocale: SupportedLocaleSchema,
  targetLocales: z.array(SupportedLocaleSchema),
  deliverables: z.object({
    baseDirectory: z.string().min(1),
    audioMasters: z.record(z.string()),
    subtitles: z.record(z.string()),
    jsxScripts: z.record(z.string()),
    reportPath: z.string().min(1),
  }),
  artifacts: z.array(VlogArtifactSchema),
  validation: z.object({
    passed: z.boolean(),
    checkedAtTimestamp: z.number().positive(),
    metrics: z.object({
      totalDurationSeconds: z.number().positive(),
      scenesCount: z.number().int().nonnegative(),
      cutsCount: z.number().int().nonnegative(),
      brollCount: z.number().int().nonnegative(),
      overlaysCount: z.number().int().nonnegative(),
    }),
  }),
});
