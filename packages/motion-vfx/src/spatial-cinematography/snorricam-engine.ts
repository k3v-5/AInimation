import {
  SnorricamSpec,
  SnorricamSpecInput,
  SnorricamSpecSchema,
} from "./spatial-types.js";

/**
 * Motor de simulación y anclaje corporal Snorricam (Dave Free / Kendrick Lamar / Darren Aronofsky).
 */
export class SnorricamEngine {
  /**
   * Calcula la transformación geométrica necesaria para anclar al sujeto en el centro de pantalla.
   */
  public static calculateAnchorAndPosition(
    subjectAnchor: [number, number],
    compWidth: number = 1080,
    compHeight: number = 1920
  ): {
    anchorPoint: [number, number];
    position: [number, number];
  } {
    return {
      anchorPoint: subjectAnchor,
      position: [compWidth / 2.0, compHeight / 2.0],
    };
  }

  /**
   * Genera las sentencias ExtendScript para bloquear al sujeto al centro y transferir la inercia al fondo.
   */
  public static exportToExtendScript(
    specInput: SnorricamSpecInput,
    options: { compVarName?: string; layerVarName?: string } = {}
  ): string[] {
    const spec = SnorricamSpecSchema.parse(specInput);
    const compVar = options.compVarName ?? "comp";
    const layerVar = options.layerVarName ?? "videoLyr";
    const lines: string[] = [];

    lines.push(`  // === SNORRICAM BODY-RIG LOCK: ${spec.id} ===`);
    lines.push(`  try {`);
    lines.push(`    if (${layerVar}) {`);
    lines.push(`      ${layerVar}.motionBlur = true; // Invariante obligatoria`);
    lines.push(``);

    // 1. Motion Tile Mirror para proteger bordes
    if (spec.motionTileMirror) {
      lines.push(`      // 1. Protección de bordes con Motion Tile espejado`);
      lines.push(`      var tileFx = ${layerVar}.property("Effects").addProperty("ADBE Motion2");`);
      lines.push(`      if (tileFx) {`);
      lines.push(`        tileFx.property("Output Width").setValue(250.0);`);
      lines.push(`        tileFx.property("Output Height").setValue(250.0);`);
      lines.push(`        tileFx.property("Mirror Edges").setValue(true);`);
      lines.push(`      }`);
      lines.push(``);
    }

    // 2. Anclaje y Posición
    lines.push(`      // 2. Fijación geométrica al centro de pantalla`);
    lines.push(
      `      ${layerVar}.property("Transform").property("Anchor Point").setValue([${spec.subjectAnchorPoint[0].toFixed(1)}, ${spec.subjectAnchorPoint[1].toFixed(1)}]);`
    );
    lines.push(
      `      ${layerVar}.property("Transform").property("Position").setValue([${compVar}.width / 2.0, ${compVar}.height / 2.0]);`
    );

    // 3. Margen de escala de amortiguación
    lines.push(
      `      ${layerVar}.property("Transform").property("Scale").setValue([${spec.scaleBufferPercent.toFixed(1)}, ${spec.scaleBufferPercent.toFixed(1)}]);`
    );

    // 4. Inyección de micro-vaivén corporal orgánico (Chest/Footstep sway)
    if (spec.stabilizationSmoothingFrames === 0) {
      lines.push(`      // Rigidez absoluta del torso con micro-inercia reactiva`);
      lines.push(
        `      ${layerVar}.property("Transform").property("Rotation").expression = "wiggle(2.2, 1.8);";`
      );
    }

    lines.push(`    }`);
    lines.push(`  } catch(e) {`);
    lines.push(`    alert('Error in SnorricamEngine: ' + e.toString());`);
    lines.push(`  }`);

    return lines;
  }
}
