export type SubjectExtractionMode = "luma_extract" | "chroma_contrast" | "bezier_roto" | "depth_matte";

export interface DepthLayerSandwichConfig {
  backgroundLayerId: string;
  textLayerId: string;
  foregroundSubjectLayerId: string;
  extractionMode: SubjectExtractionMode;
  thresholds?: {
    blackPoint?: number; // Para Luma Extract (default: 45)
    whitePoint?: number; // Para Luma Extract (default: 190)
    feather?: number; // Suavizado de bordes en px (default: 5.0)
    colorKeyTolerance?: number; // Para Chroma (default: 25)
  };
  blurTransition?: {
    enabled: boolean;
    transitionTimeSec: number;
    maxBlurPx: number; // default: 35
    textShiftToFront: boolean; // Si true, pasa el texto al frente al aplicar blur
  };
}

export interface RenderableDepthHierarchy {
  layersInZOrder: string[]; // [Fondo, Plano Medio/Texto, Primer Plano/Sujeto]
  effectsConfig: {
    layerId: string;
    effectName: string;
    parameters: Record<string, unknown>;
  }[];
}

/**
 * Motor de segmentación de sujetos y composición de profundidad 3D (Fase 12 / Mejoras).
 * Administra la jerarquía visual de capas ("Text Behind Subject"), modos de recorte y transiciones de desenfoque de fondo.
 */
export class SubjectMaskingEngine {
  /**
   * Construye la jerarquía canónica de capas 3D (DepthLayerSandwich) para componer texto detrás de personas.
   */
  public static buildDepthSandwich(config: DepthLayerSandwichConfig): RenderableDepthHierarchy {
    const layersInZOrder = [
      config.backgroundLayerId,
      config.textLayerId,
      config.foregroundSubjectLayerId,
    ];

    const effectsConfig: RenderableDepthHierarchy["effectsConfig"] = [];

    const bp = config.thresholds?.blackPoint ?? 45;
    const wp = config.thresholds?.whitePoint ?? 190;
    const feather = config.thresholds?.feather ?? 5.0;

    if (config.extractionMode === "luma_extract") {
      effectsConfig.push({
        layerId: config.foregroundSubjectLayerId,
        effectName: "ADBE Extract",
        parameters: {
          "Black Point": bp,
          "White Point": wp,
          "Black Softness": feather,
          "White Softness": feather,
        },
      });
    } else if (config.extractionMode === "chroma_contrast") {
      effectsConfig.push({
        layerId: config.foregroundSubjectLayerId,
        effectName: "ADBE Linear Color Key",
        parameters: {
          Tolerance: config.thresholds?.colorKeyTolerance ?? 25,
          Feather: feather,
        },
      });
    }

    if (config.blurTransition?.enabled) {
      effectsConfig.push({
        layerId: config.backgroundLayerId,
        effectName: "ADBE Fast Blur",
        parameters: {
          Blurriness: config.blurTransition.maxBlurPx,
          "Repeat Edge Pixels": true,
        },
      });
    }

    return {
      layersInZOrder,
      effectsConfig,
    };
  }

  /**
   * Genera el código ExtendScript para ensamblar automáticamente el Depth Sandwich en After Effects.
   */
  public static generateExtendScriptSandwich(
    compVar: string,
    footageVar: string,
    textLayerVar: string,
    inTime: number,
    outTime: number,
    config: Partial<DepthLayerSandwichConfig> = {}
  ): string {
    const bp = config.thresholds?.blackPoint ?? 45;
    const wp = config.thresholds?.whitePoint ?? 190;

    return [
      `// === DEPTH LAYER SANDWICH (TEXT BEHIND SUBJECT) ===`,
      `var fgLayer = ${compVar}.layers.add(${footageVar});`,
      `fgLayer.name = "Foreground_Subject_Cutout";`,
      `fgLayer.motionBlur = true;`,
      `fgLayer.audioEnabled = false;`,
      `fgLayer.startTime = ${inTime};`,
      `fgLayer.inPoint = ${inTime};`,
      `fgLayer.outPoint = ${outTime};`,
      `try {`,
      `  var extEffect = fgLayer.property("Effects").addProperty("ADBE Extract");`,
      `  if (extEffect) {`,
      `    extEffect.property("Black Point").setValue(${bp});`,
      `    extEffect.property("White Point").setValue(${wp});`,
      `  }`,
      `} catch(e) {}`,
    ].join("\n");
  }
}
