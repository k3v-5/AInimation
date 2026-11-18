import { Composition } from "../core/composition.js";
import { StyleProfileManager, StylePresetId } from "../styles/StyleProfileManager.js";
import { SupportedAspectRatio } from "../exporters/omni/OmniChannelMultiExporter.js";
import { SupportedLocale } from "../vlog/contracts/language.types.js";
import { GeoBadge, LocationCard } from "../vlog/contracts/travel-overlays.types.js";

export interface VlogProductionDSLConfig {
  enabled: boolean;
  aRollSource?: string;
  bRollDirectory?: string;
  transcriptText?: string;
  sourceLocale?: SupportedLocale;
  targetLanguages?: SupportedLocale[];
  autoJumpCut?: boolean;
  punchInScale?: number;
  travelOverlays?: {
    geoBadge?: GeoBadge;
    locationCard?: LocationCard;
  };
}

export interface DeclarativeProductionIntent {
  video: {
    format: SupportedAspectRatio;
    durationSec: number;
    fps?: number;
    projectName?: string;
  };
  style: {
    preset: StylePresetId;
    title: string;
    badgeText?: string;
  };
  editing: {
    pacing: "aggressive" | "balanced" | "cinematic_slow";
    beatSync: boolean;
    speedRamping: boolean;
    depthSandwich: boolean;
  };
  captions?: {
    enabled: boolean;
    text: string;
  };
  soundDesign?: {
    enabled: boolean;
    autoDucking: boolean;
  };
  vlog?: VlogProductionDSLConfig;
  dataviz?: {
    type: "BAR_CHART" | "LINE_GRAPH" | "BIG_STAT" | "CHRONOLOGY";
    dataset: any;
    orientation?: "VERTICAL" | "HORIZONTAL";
    durationSeconds?: number;
  };
}

export function dataviz(config: {
  type: "BAR_CHART" | "LINE_GRAPH" | "BIG_STAT" | "CHRONOLOGY";
  dataset: any;
  orientation?: "VERTICAL" | "HORIZONTAL";
  durationSeconds?: number;
}) {
  return config;
}
export const dataViz = dataviz;

export interface VisualizationDSLConfig {
  type: "BAR_CHART" | "TREND_LINE" | "LINE_GRAPH" | "BIG_STAT" | "TIMELINE" | "CHRONOLOGY";
  dataset?: any;
  value?: number;
  unit?: string;
  label?: string;
  start?: number;
  duration?: number;
  orientation?: "VERTICAL" | "HORIZONTAL";
  showValues?: boolean;
  [key: string]: unknown;
}

export function visualization(config: VisualizationDSLConfig) {
  return {
    ...config,
    type: config.type === "TIMELINE" ? "CHRONOLOGY" : config.type === "LINE_GRAPH" ? "TREND_LINE" : config.type,
  };
}

export interface CompiledDSLResult {
  composition: Composition;
  appliedProfile: string;
  estimatedRenderDurationSec: number;
  metadata: {
    targetFormat: SupportedAspectRatio;
    totalDuration: number;
    layersCount: number;
  };
  vlogMetadata?: {
    vlogModeActive: boolean;
    targetLanguages: SupportedLocale[];
    autoJumpCut: boolean;
    punchInScale: number;
    hasTravelOverlays: boolean;
  };
}

/**
 * Compilador de Intención Audiovisual Declarativa (Production DSL) (Autonomous MCP v2 / REQ-034).
 * Convierte un bloque compacto de intención de la IA en un proyecto canónico ProjectIR en 1 solo paso.
 */
export class ProductionDSLCompiler {
  /**
   * Compila una intención declarativa en una Composición canónica de producción.
   */
  public static compile(intent: DeclarativeProductionIntent): CompiledDSLResult {
    const profile = StyleProfileManager.getProfile(intent.style.preset);

    const dims =
      intent.video.format === "9:16"
        ? { width: 1080, height: 1920 }
        : intent.video.format === "16:9"
        ? { width: 1920, height: 1080 }
        : { width: 1080, height: 1080 };

    const compName = intent.video.projectName ?? `Comp_${intent.style.preset}_${intent.video.format.replace(":", "x")}`;
    const comp = new Composition({
      name: compName,
      width: dims.width,
      height: dims.height,
      fps: intent.video.fps ?? 60,
      duration: intent.video.durationSec,
    });

    const isVlog = Boolean(intent.vlog?.enabled);
    const vlogMetadata = isVlog
      ? {
          vlogModeActive: true,
          targetLanguages: intent.vlog?.targetLanguages ?? [intent.vlog?.sourceLocale ?? "es-MX"],
          autoJumpCut: intent.vlog?.autoJumpCut ?? true,
          punchInScale: intent.vlog?.punchInScale ?? 1.15,
          hasTravelOverlays: Boolean(intent.vlog?.travelOverlays?.geoBadge || intent.vlog?.travelOverlays?.locationCard),
        }
      : undefined;

    return {
      composition: comp,
      appliedProfile: profile.name,
      estimatedRenderDurationSec: Number((intent.video.durationSec * 0.85).toFixed(1)),
      metadata: {
        targetFormat: intent.video.format,
        totalDuration: intent.video.durationSec,
        layersCount: comp.getLayers().length,
      },
      vlogMetadata,
    };
  }
}
