import {
  ActiveSpeakerReframingEngine,
  FocalPointSample,
  ReframingMode,
} from "../../automation/reframing/ActiveSpeakerReframingEngine.js";
import { McpValidationError } from "../errors/mcp-errors.js";

export interface AutoReframeVideoArgs {
  mode?: ReframingMode;
  focalPoints?: FocalPointSample[];
  sourceWidth?: number;
  sourceHeight?: number;
  targetWidth?: number;
  targetHeight?: number;
  deadzonePx?: number;
}

/**
 * Handler de la herramienta MCP `auto_reframe_video`.
 * Calcula keyframes de reencuadre dinámico 16:9 a 9:16 con deadzones anti-jitter o split-screen.
 */
export async function handleAutoReframeVideo(rawArgs: unknown) {
  const args = (rawArgs ?? {}) as AutoReframeVideoArgs;
  const mode = args.mode ?? "dynamic_pan_and_scan";
  const sW = args.sourceWidth ?? 1920;
  const sH = args.sourceHeight ?? 1080;
  const tW = args.targetWidth ?? 1080;
  const tH = args.targetHeight ?? 1920;

  const result = ActiveSpeakerReframingEngine.calculateReframing(
    mode,
    args.focalPoints ?? [],
    sW,
    sH,
    tW,
    tH,
    args.deadzonePx ?? 45.0
  );

  return {
    status: "success",
    mode: result.mode,
    targetResolution: result.targetResolution,
    keyframesCount: result.keyframes.length,
    reframing: result,
  };
}
