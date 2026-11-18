import {
  TextBehindSubjectConfig,
  MultiTakeCloneConfig,
  TextBehindSubjectEngine,
  MultiTakeCloneEngine,
  ObjectDetectionEngine,
} from "../../compositing/subject/index.js";

/**
 * REQ-F19: Herramientas MCP para composición orientada a sujetos y objetos (Fase 19).
 */

export async function compose_text_behind_subject(params: TextBehindSubjectConfig) {
  const plan = TextBehindSubjectEngine.compile(params);
  return {
    success: true,
    plan,
  };
}

export async function compose_multi_take_clones(params: MultiTakeCloneConfig) {
  const plan = MultiTakeCloneEngine.compile(params);
  return {
    success: true,
    plan,
  };
}

export async function detect_subjects_in_clip(params: {
  frameIndex?: number;
  timestampSeconds?: number;
  compWidth?: number;
  compHeight?: number;
  zone?: "LEFT" | "CENTER" | "RIGHT";
}) {
  const subject = ObjectDetectionEngine.createProceduralPersonDetection({
    frameIndex: params.frameIndex ?? 0,
    timestampSeconds: params.timestampSeconds ?? 0.0,
    compWidth: params.compWidth ?? 1920,
    compHeight: params.compHeight ?? 1080,
    zone: params.zone ?? "CENTER",
  });

  return {
    success: true,
    subject,
  };
}
