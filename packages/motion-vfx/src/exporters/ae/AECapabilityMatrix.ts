import { Composition } from "../../core/composition.js";
import { CapabilityEntry, CapabilityReport, ExportPlan, ExportPlanItem } from "../common/CapabilityMatrix.js";

export const AECapabilityEntries: CapabilityEntry[] = [
  {
    feature: "Composition",
    status: "exact",
    fallback: "none",
    description: "Creación nativa de CompItem con dimensiones, duración, fps y pixel aspect ratio.",
  },
  {
    feature: "SolidLayer",
    status: "exact",
    fallback: "none",
    description: "Creación nativa de capas sólidas con color RGBA y dimensiones.",
  },
  {
    feature: "TextLayer",
    status: "exact",
    fallback: "none",
    description: "Creación de TextLayer con fuente, tamaño, color de relleno, trazo y alineación.",
  },
  {
    feature: "FootageLayer",
    status: "exact",
    fallback: "none",
    description: "Importación de assets de imagen y video vía footage item de After Effects.",
  },
  {
    feature: "AudioLayer",
    status: "exact",
    fallback: "none",
    description: "Capas de audio con niveles de volumen en decibelios y switches de mute.",
  },
  {
    feature: "ShapeLayer",
    status: "exact",
    fallback: "none",
    description: "Capas de formas vectoriales (rectángulos, elipses, trazo y relleno).",
  },
  {
    feature: "Transforms",
    status: "exact",
    fallback: "none",
    description: "Transformaciones completas: Position, Scale, Rotation, Opacity y Anchor Point en píxeles.",
  },
  {
    feature: "Hierarchy",
    status: "exact",
    fallback: "none",
    description: "Enlace jerárquico parent/child sin ciclos.",
  },
  {
    feature: "Keyframes",
    status: "exact",
    fallback: "none",
    description: "Interpolación de keyframes lineales y curvas Bezier con KeyframeEase.",
  },
  {
    feature: "Masks",
    status: "exact",
    fallback: "none",
    description: "Máscaras vectoriales con vértices y tangentes Bezier.",
  },
  {
    feature: "Effects",
    status: "exact",
    fallback: "none",
    description: "Mapeo de efectos nativos (Drop Shadow, Gaussian Blur, Glow, Color Control).",
  },
  {
    feature: "KineticCaptions",
    status: "approximate",
    fallback: "convert-to-keyframes",
    description: "Animación de palabras cinéticas convertida a keyframes continuos de escala y color.",
    notes: "AE no tiene animadores analíticos continuos nativos para presets virales; se aproxima mediante keyframes.",
  },
  {
    feature: "ProceduralParticles",
    status: "lossy",
    fallback: "drop-effect",
    description: "Partículas procedurales complejas aproximadas o degradadas a capas sólidas.",
  },
];

/**
 * Analizador determinista de capacidades de exportación para After Effects (Fase 17).
 */
export class AECapabilityAnalyzer {
  /**
   * Genera el reporte general de capacidades de After Effects.
   */
  public static getCapabilityReport(): CapabilityReport {
    const exactCount = AECapabilityEntries.filter((e) => e.status === "exact").length;
    const approximateCount = AECapabilityEntries.filter((e) => e.status === "approximate").length;
    const lossyCount = AECapabilityEntries.filter((e) => e.status === "lossy").length;
    const unsupportedCount = AECapabilityEntries.filter((e) => e.status === "unsupported").length;

    return {
      target: "after-effects",
      version: "ExtendScript CC 2026",
      totalFeatures: AECapabilityEntries.length,
      exactCount,
      approximateCount,
      lossyCount,
      unsupportedCount,
      entries: AECapabilityEntries,
      warnings: [],
    };
  }

  /**
   * Analiza una composición IR y genera un ExportPlan antes de compilar.
   */
  public static createExportPlan(comp: Composition, strict = false, dryRun = false): ExportPlan {
    const items: ExportPlanItem[] = [];
    const warnings: string[] = [];
    const errors: string[] = [];

    let exact = 0;
    let approximate = 0;
    let lossy = 0;
    let unsupported = 0;

    // 1. Analizar composición
    items.push({
      entityId: comp.id,
      entityType: "Composition",
      feature: "Composition",
      status: "exact",
      fallback: "none",
      actionSummary: `Crear CompItem '${comp.name}' (${comp.width}x${comp.height} @ ${comp.fps}fps, ${comp.duration}s)`,
    });
    exact++;

    const layers = comp.getLayers();
    const elements = comp.getElements();
    const totalItems = elements.length > 0 ? elements : layers;

    // 2. Analizar capas / elementos
    for (const item of totalItems) {
      const entry = AECapabilityEntries.find((e) => e.feature === "SolidLayer")!;
      items.push({
        entityId: item.id,
        entityType: "Layer",
        feature: item.name,
        status: entry.status,
        fallback: entry.fallback,
        actionSummary: `Exportar capa '${item.name}'`,
      });
      exact++;
    }

    const canProceed = strict ? errors.length === 0 && approximate === 0 && lossy === 0 && unsupported === 0 : errors.length === 0;

    return {
      target: "after-effects",
      strict,
      dryRun,
      canProceed,
      items,
      warnings,
      errors,
      summary: { exact, approximate, lossy, unsupported },
    };
  }
}
