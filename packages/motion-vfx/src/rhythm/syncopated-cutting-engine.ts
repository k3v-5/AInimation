import {
  SyncopatedCutPoint,
  SyncopatedCutPointInput,
  SyncopatedCutPointSchema,
  SyncopatedSequenceSpec,
  SyncopatedSequenceSpecInput,
  SyncopatedSequenceSpecSchema,
} from "./rhythm-types.js";
import { MusicalGrid } from "./musical-grid.js";

/**
 * Motor de montaje secuencial sincopado y ensamblado de cortes en línea de tiempo.
 */
export class SyncopatedCuttingEngine {
  /**
   * Cuantiza y ordena cronológicamente una lista de puntos de corte rítmico.
   */
  public static validateAndSnapCuts(
    cutsInput: SyncopatedCutPointInput[],
    fps: number
  ): SyncopatedCutPoint[] {
    const rawCuts = cutsInput.map((c) => SyncopatedCutPointSchema.parse(c));
    // Ordenar cronológicamente
    rawCuts.sort((a, b) => a.timeSeconds - b.timeSeconds);

    return rawCuts.map((cut) => {
      const snappedTime = MusicalGrid.snapToFrame(cut.timeSeconds, fps);
      const snappedDuration = MusicalGrid.snapToFrame(cut.durationSeconds, fps);
      return {
        timeSeconds: snappedTime,
        mediaAssetPath: cut.mediaAssetPath,
        sourceInPointSeconds: cut.sourceInPointSeconds,
        durationSeconds: Math.max(1.0 / fps, snappedDuration),
      };
    });
  }

  /**
   * Genera las sentencias ExtendScript para colocar los clips de video en orden rítmico sincopado.
   */
  public static exportToExtendScript(
    specInput: SyncopatedSequenceSpecInput,
    options: { compVarName?: string } = {}
  ): string[] {
    const spec = SyncopatedSequenceSpecSchema.parse(specInput);
    const compVar = options.compVarName ?? "comp";
    const snappedCuts = this.validateAndSnapCuts(spec.cuts, spec.fps);
    const lines: string[] = [];

    lines.push(`  // === SYNCOPATED RHYTHMIC CUTTING SEQUENCE: ${spec.id} (BPM: ${spec.bpm}) ===`);
    lines.push(`  try {`);

    snappedCuts.forEach((cut, idx) => {
      const normalizedPath = cut.mediaAssetPath.replace(/\\/g, "/");
      const outPoint = MusicalGrid.snapToFrame(cut.timeSeconds + cut.durationSeconds, spec.fps);

      lines.push(`    // Cut #${idx + 1} @ t = ${cut.timeSeconds.toFixed(4)}s (dur: ${cut.durationSeconds.toFixed(4)}s)`);
      lines.push(`    var fileRef_${idx} = new File('${normalizedPath}');`);
      lines.push(`    if (fileRef_${idx}.exists) {`);
      lines.push(`      var item_${idx} = app.project.importFile(new ImportOptions(fileRef_${idx}));`);
      lines.push(`      if (item_${idx}) {`);
      lines.push(`        var lyr_${idx} = ${compVar}.layers.add(item_${idx});`);
      lines.push(`        lyr_${idx}.name = '[RHYTHM CUT ${idx + 1}] ' + fileRef_${idx}.displayName;`);
      lines.push(`        lyr_${idx}.startTime = ${(cut.timeSeconds - cut.sourceInPointSeconds).toFixed(4)};`);
      lines.push(`        lyr_${idx}.inPoint = ${cut.timeSeconds.toFixed(4)};`);
      lines.push(`        lyr_${idx}.outPoint = ${outPoint.toFixed(4)};`);
      lines.push(`        lyr_${idx}.motionBlur = true;`);
      lines.push(`      }`);
      lines.push(`    }`);
    });

    lines.push(`  } catch(e) {`);
    lines.push(`    alert('Error in SyncopatedCuttingEngine: ' + e.toString());`);
    lines.push(`  }`);

    return lines;
  }
}
