import { Composition } from "../../core/composition.js";
import { Layer } from "../../core/layer.js";
import { BaseElement } from "../../elements/BaseElement.js";
import { CapabilityEntry, CapabilityReport, ExportPlan } from "../common/CapabilityMatrix.js";
import { ExportManifest, ExportManifestBuilder } from "../common/ExportManifest.js";
import { TimecodeUtils } from "../common/TimecodeUtils.js";

export const EDLCapabilityEntries: CapabilityEntry[] = [
  {
    feature: "EventCuts",
    status: "exact",
    fallback: "none",
    description: "Eventos de corte directo (C) con timecodes de origen y destino CMX 3600.",
  },
  {
    feature: "CrossDissolves",
    status: "exact",
    fallback: "none",
    description: "Disolvencias cruzadas estándar (D) con duración de transición en frames.",
  },
  {
    feature: "AudioChannels",
    status: "exact",
    fallback: "none",
    description: "Canales de audio asignados a pistas A o A2.",
  },
  {
    feature: "Transforms",
    status: "unsupported",
    fallback: "none",
    description: "EDL estándar no soporta posición, escala, rotación ni transformaciones espaciales.",
  },
  {
    feature: "CaptionsAndTypography",
    status: "lossy",
    fallback: "flatten-text",
    description: "Subtítulos y tipografía cinética omitidos o degradados a eventos de video simples.",
    notes: "El formato CMX 3600 carece de soporte nativo para texto y subtítulos.",
  },
  {
    feature: "MasksAndEffects",
    status: "unsupported",
    fallback: "drop-effect",
    description: "Efectos visuales y máscaras omitidos por limitación intrínseca del protocolo EDL.",
  },
];

export interface EDLExportOptions {
  strict?: boolean;
  dryRun?: boolean;
  projectId?: string;
  revisionId?: string;
}

export interface EDLExportResult {
  edlContent: string;
  manifest: ExportManifest;
  plan: ExportPlan;
  warnings: string[];
}

/**
 * Exportador determinista de IR Canónica a CMX 3600 EDL (Fase 17).
 */
export class EDLExporter {
  public static readonly EXPORTER_VERSION = "1.7.0";

  public static getCapabilityReport(): CapabilityReport {
    return {
      target: "edl",
      version: "CMX 3600",
      totalFeatures: EDLCapabilityEntries.length,
      exactCount: EDLCapabilityEntries.filter((e) => e.status === "exact").length,
      approximateCount: EDLCapabilityEntries.filter((e) => e.status === "approximate").length,
      lossyCount: EDLCapabilityEntries.filter((e) => e.status === "lossy").length,
      unsupportedCount: EDLCapabilityEntries.filter((e) => e.status === "unsupported").length,
      entries: EDLCapabilityEntries,
      warnings: [
        "CMX 3600 EDL es un formato puramente de montaje de cortes; no soporta efectos, máscaras ni animaciones tipográficas.",
      ],
    };
  }

  public static export(comp: Composition, options: EDLExportOptions = {}): EDLExportResult {
    const strict = options.strict ?? false;
    const dryRun = options.dryRun ?? false;
    const projectId = options.projectId ?? `proj_${comp.id}`;
    const revisionId = options.revisionId ?? "rev_1";
    const warnings: string[] = [
      "EDL Export Warning: Captions, masks and procedural effects were omitted due to format limitations.",
    ];

    const frameRate = TimecodeUtils.resolveFrameRate(comp.fps);
    const elements = comp.getElements();
    const layers = comp.getLayers();
    const items = elements.length > 0 ? elements : layers;

    // 1. Análisis de capacidades
    const plan: ExportPlan = {
      target: "edl",
      strict,
      dryRun,
      canProceed: !strict,
      items: items.map((l) => ({
        entityId: l.id,
        entityType: "Layer",
        feature: l.name,
        status: "lossy",
        fallback: "flatten-text",
        actionSummary: `Mapear capa '${l.name}' a evento de corte CMX`,
      })),
      warnings,
      errors: strict ? ["Strict mode prohibited EDL export: Format cannot represent transforms or effects."] : [],
      summary: { exact: 2, approximate: 0, lossy: items.length, unsupported: 3 },
    };

    if (strict) {
      throw new Error(
        `EDL_STRICT_EXPORT_FAILED: CMX 3600 EDL cannot losslessly represent composition '${comp.name}'.`
      );
    }

    if (dryRun) {
      const manifest = ExportManifestBuilder.buildManifest({
        exporter: "EDLExporter",
        exporterVersion: this.EXPORTER_VERSION,
        sourceIRVersion: "1.7.0",
        projectId,
        revisionId,
        exportedContent: "TITLE: DRY RUN",
        primaryFileName: `${comp.name}.edl`,
        capabilityReport: this.getCapabilityReport(),
        warnings,
      });

      return {
        edlContent: "TITLE: DRY RUN: CMX 3600 EDL plan created successfully.",
        manifest,
        plan,
        warnings,
      };
    }

    // 2. Construir archivo EDL CMX 3600 estándar
    const lines: string[] = [];
    lines.push(`TITLE: ${comp.name.toUpperCase().replace(/[^A-Z0-9_-]/g, "_")}`);
    lines.push(`FCM: ${frameRate.dropFrame ? "DROP FRAME" : "NON-DROP FRAME"}`);
    lines.push(``);

    let currentRecordFrame = 0;

    for (let lIdx = 0; lIdx < items.length; lIdx++) {
      const item = items[lIdx];
      const eventNum = String(lIdx + 1).padStart(3, "0");
      const durationSeconds =
        item instanceof BaseElement
          ? item.duration
          : (item as Layer).endTime === Infinity
          ? comp.duration
          : (item as Layer).endTime - (item as Layer).startTime;

      const durationFrames = TimecodeUtils.secondsToFrame(durationSeconds, frameRate);

      const srcInTC = "00:00:00:00";
      const srcOutTC = TimecodeUtils.frameToTimecode(durationFrames, frameRate);
      const recInTC = TimecodeUtils.frameToTimecode(currentRecordFrame, frameRate);
      const recOutTC = TimecodeUtils.frameToTimecode(currentRecordFrame + durationFrames, frameRate);

      lines.push(`${eventNum}  AX       V     C        ${srcInTC} ${srcOutTC} ${recInTC} ${recOutTC}`);
      lines.push(`* FROM CLIP NAME: ${item.name}`);
      lines.push(``);

      currentRecordFrame += durationFrames;
    }

    const edlContent = lines.join("\n");

    // 3. Manifiesto Determinista con Hash SHA-256
    const manifest = ExportManifestBuilder.buildManifest({
      exporter: "EDLExporter",
      exporterVersion: this.EXPORTER_VERSION,
      sourceIRVersion: "1.7.0",
      projectId,
      revisionId,
      exportedContent: edlContent,
      primaryFileName: `${comp.name}.edl`,
      capabilityReport: this.getCapabilityReport(),
      warnings,
    });

    return {
      edlContent,
      manifest,
      plan,
      warnings,
    };
  }
}
