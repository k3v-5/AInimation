import {
  ParallaxOcclusionWipeSpec,
  ParallaxOcclusionWipeSpecInput,
  ParallaxOcclusionWipeSpecSchema,
} from "./spatial-types.js";

/**
 * Motor de transición por oclusión de primer plano en perspectiva (Hiro Murai / Dave Free).
 */
export class ParallaxOcclusionWipeEngine {
  /**
   * Calcula los vértices de la máscara en el inicio y final del barrido según la dirección.
   */
  public static calculateWipeBounds(
    specInput: ParallaxOcclusionWipeSpecInput,
    compWidth: number = 1080,
    compHeight: number = 1920
  ): {
    startVertices: Array<[number, number]>;
    endVertices: Array<[number, number]>;
  } {
    const spec = ParallaxOcclusionWipeSpecSchema.parse(specInput);
    const m = 100.0; // Margen extra de seguridad

    switch (spec.direction) {
      case "RIGHT_TO_LEFT":
        return {
          startVertices: [
            [compWidth + m, -m],
            [compWidth + m, -m],
            [compWidth + m, compHeight + m],
            [compWidth + m, compHeight + m],
          ],
          endVertices: [
            [-m, -m],
            [compWidth + m, -m],
            [compWidth + m, compHeight + m],
            [-m, compHeight + m],
          ],
        };

      case "TOP_TO_BOTTOM":
        return {
          startVertices: [
            [-m, -m],
            [compWidth + m, -m],
            [compWidth + m, -m],
            [-m, -m],
          ],
          endVertices: [
            [-m, -m],
            [compWidth + m, -m],
            [compWidth + m, compHeight + m],
            [-m, compHeight + m],
          ],
        };

      case "BOTTOM_TO_TOP":
        return {
          startVertices: [
            [-m, compHeight + m],
            [compWidth + m, compHeight + m],
            [compWidth + m, compHeight + m],
            [-m, compHeight + m],
          ],
          endVertices: [
            [-m, -m],
            [compWidth + m, -m],
            [compWidth + m, compHeight + m],
            [-m, compHeight + m],
          ],
        };

      case "LEFT_TO_RIGHT":
      default:
        return {
          startVertices: [
            [-m, -m],
            [-m, -m],
            [-m, compHeight + m],
            [-m, compHeight + m],
          ],
          endVertices: [
            [-m, -m],
            [compWidth + m, -m],
            [compWidth + m, compHeight + m],
            [-m, compHeight + m],
          ],
        };
    }
  }

  /**
   * Genera el código ExtendScript para crear y animar la máscara de oclusión con calado suave.
   */
  public static exportToExtendScript(
    specInput: ParallaxOcclusionWipeSpecInput,
    options: { destLayerVarName?: string; compVarName?: string } = {}
  ): string[] {
    const spec = ParallaxOcclusionWipeSpecSchema.parse(specInput);
    const destLayerVar = options.destLayerVarName ?? "destLayer";
    const compVar = options.compVarName ?? "comp";
    const bounds = this.calculateWipeBounds(spec, 1080, 1920);
    const tStart = spec.startTimeSeconds;
    const tEnd = Number((spec.startTimeSeconds + spec.durationSeconds).toFixed(5));
    const lines: string[] = [];

    lines.push(`  // === PARALLAX OCCLUSION WIPE: ${spec.id} (${spec.direction}) ===`);
    lines.push(`  try {`);
    lines.push(`    if (${destLayerVar}) {`);
    lines.push(`      ${destLayerVar}.motionBlur = true; // Invariante obligatoria`);
    lines.push(`      var maskGroup = ${destLayerVar}.property("Masks");`);
    lines.push(`      var occMask = maskGroup.addProperty("Mask");`);
    lines.push(`      occMask.maskMode = MaskMode.ADD;`);
    lines.push(`      occMask.property("Mask Feather").setValue([${spec.featherPx.toFixed(1)}, ${spec.featherPx.toFixed(1)}]);`);
    lines.push(``);
    lines.push(`      // Configurar Keyframes de Máscara de Revelado`);
    lines.push(`      var mShapeProp = occMask.property("Mask Path");`);
    lines.push(`      var shapeStart = new Shape();`);
    lines.push(`      shapeStart.vertices = ${JSON.stringify(bounds.startVertices)};`);
    lines.push(`      shapeStart.closed = true;`);
    lines.push(`      mShapeProp.setValueAtTime(${tStart.toFixed(4)}, shapeStart);`);
    lines.push(``);
    lines.push(`      var shapeEnd = new Shape();`);
    lines.push(`      shapeEnd.vertices = ${JSON.stringify(bounds.endVertices)};`);
    lines.push(`      shapeEnd.closed = true;`);
    lines.push(`      mShapeProp.setValueAtTime(${tEnd.toFixed(4)}, shapeEnd);`);
    lines.push(`    }`);
    lines.push(`  } catch(e) {`);
    lines.push(`    alert('Error in ParallaxOcclusionWipeEngine: ' + e.toString());`);
    lines.push(`  }`);

    return lines;
  }
}
