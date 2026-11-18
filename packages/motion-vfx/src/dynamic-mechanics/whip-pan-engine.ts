import {
  WhipPanMatchCutSpec,
  WhipPanMatchCutSpecInput,
  WhipPanMatchCutSpecSchema,
} from "./mechanics-types.js";

/**
 * Motor de transición invisible por barrido direccional ultrarrápido (Directional Whip-Pan Match Cut).
 */
export class WhipPanEngine {
  /**
   * Resuelve el ángulo de desenfoque direccional según la orientación del barrido.
   */
  public static getDirectionAngleDegrees(
    direction: "PAN_LEFT" | "PAN_RIGHT" | "TILT_UP" | "TILT_DOWN"
  ): number {
    switch (direction) {
      case "PAN_LEFT":
      case "PAN_RIGHT":
        return 90.0; // Desenfoque horizontal
      case "TILT_UP":
      case "TILT_DOWN":
        return 0.0; // Desenfoque vertical
    }
  }

  /**
   * Genera el código ExtendScript para orquestar el whip-pan simétrico entre dos tomas.
   */
  public static exportToExtendScript(
    specInput: WhipPanMatchCutSpecInput,
    options: {
      sourceLayerVarName?: string;
      destLayerVarName?: string;
      compVarName?: string;
    } = {}
  ): string[] {
    const spec = WhipPanMatchCutSpecSchema.parse(specInput);
    const srcVar = options.sourceLayerVarName ?? "sourceLayer";
    const destVar = options.destLayerVarName ?? "destLayer";
    const compVar = options.compVarName ?? "comp";

    const halfDur = spec.transitionDurationSeconds / 2.0;
    const tStart = Number((spec.cutTimeSeconds - halfDur).toFixed(5));
    const tCut = spec.cutTimeSeconds;
    const tEnd = Number((spec.cutTimeSeconds + halfDur).toFixed(5));
    const angle = this.getDirectionAngleDegrees(spec.direction);

    // Desplazamiento posicional de cámara
    const isHorizontal = spec.direction === "PAN_LEFT" || spec.direction === "PAN_RIGHT";
    const sign = spec.direction === "PAN_RIGHT" || spec.direction === "TILT_DOWN" ? 1.0 : -1.0;
    const offsetX = isHorizontal ? sign * spec.seamlessOffsetPx : 0.0;
    const offsetY = !isHorizontal ? sign * spec.seamlessOffsetPx : 0.0;

    const lines: string[] = [];

    lines.push(`  // === DIRECTIONAL WHIP-PAN MATCH CUT: ${spec.id} (${spec.direction}) ===`);
    lines.push(`  try {`);

    // 1. Configuración de Toma Saliente (Source Layer)
    lines.push(`    // 1. Toma Saliente A: aceleración hacia el corte`);
    lines.push(`    if (${srcVar}) {`);
    lines.push(`      ${srcVar}.motionBlur = true;`);
    lines.push(`      ${srcVar}.outPoint = ${tCut.toFixed(4)};`);
    lines.push(`      var blurA = ${srcVar}.property("Effects").addProperty("ADBE Directional Blur");`);
    lines.push(`      if (blurA) {`);
    lines.push(`        blurA.property("Direction").setValue(${angle.toFixed(1)});`);
    lines.push(`        var blPropA = blurA.property("Blur Length");`);
    lines.push(`        blPropA.setValueAtTime(${tStart.toFixed(4)}, 0.0);`);
    lines.push(`        blPropA.setValueAtTime(${tCut.toFixed(4)}, ${spec.maxBlurLengthPx.toFixed(1)});`);
    lines.push(`      }`);
    lines.push(`      var posPropA = ${srcVar}.property("Transform").property("Position");`);
    lines.push(`      var basePosA = posPropA.value;`);
    lines.push(`      posPropA.setValueAtTime(${tStart.toFixed(4)}, basePosA);`);
    lines.push(
      `      posPropA.setValueAtTime(${tCut.toFixed(4)}, [basePosA[0] - (${offsetX.toFixed(1)}), basePosA[1] - (${offsetY.toFixed(1)})]);`
    );
    lines.push(`    }`);
    lines.push(``);

    // 2. Configuración de Toma Entrante (Dest Layer)
    lines.push(`    // 2. Toma Entrante B: desaceleración desde el corte`);
    lines.push(`    if (${destVar}) {`);
    lines.push(`      ${destVar}.motionBlur = true;`);
    lines.push(`      ${destVar}.inPoint = ${tCut.toFixed(4)};`);
    lines.push(`      var blurB = ${destVar}.property("Effects").addProperty("ADBE Directional Blur");`);
    lines.push(`      if (blurB) {`);
    lines.push(`        blurB.property("Direction").setValue(${angle.toFixed(1)});`);
    lines.push(`        var blPropB = blurB.property("Blur Length");`);
    lines.push(`        blPropB.setValueAtTime(${tCut.toFixed(4)}, ${spec.maxBlurLengthPx.toFixed(1)});`);
    lines.push(`        blPropB.setValueAtTime(${tEnd.toFixed(4)}, 0.0);`);
    lines.push(`      }`);
    lines.push(`      var posPropB = ${destVar}.property("Transform").property("Position");`);
    lines.push(`      var basePosB = posPropB.value;`);
    lines.push(
      `      posPropB.setValueAtTime(${tCut.toFixed(4)}, [basePosB[0] + (${offsetX.toFixed(1)}), basePosB[1] + (${offsetY.toFixed(1)})]);`
    );
    lines.push(`      posPropB.setValueAtTime(${tEnd.toFixed(4)}, basePosB);`);
    lines.push(`    }`);

    lines.push(`  } catch(e) {`);
    lines.push(`    alert('Error in WhipPanEngine: ' + e.toString());`);
    lines.push(`  }`);

    return lines;
  }
}
