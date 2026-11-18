import { ShutterFlickerSpec, ShutterFlickerSpecInput, ShutterFlickerSpecSchema } from "./film-types.js";

/**
 * Motor de fluctuación de obturador rotativo (Shutter Flicker) y arrastre de celuloide (Gate Weave).
 */
export class FilmShutterFlickerEngine {
  /**
   * Genera las sentencias ExtendScript para inyectar flicker y gate weave en After Effects.
   */
  public static exportToExtendScript(
    specInput: ShutterFlickerSpecInput,
    options: { layerVarName?: string } = {}
  ): string[] {
    const spec = ShutterFlickerSpecSchema.parse(specInput);
    const layerVar = options.layerVarName ?? "targetLayer";
    const lines: string[] = [];

    lines.push(`  // === SHUTTER FLICKER & GATE WEAVE ENGINE ===`);
    lines.push(`  try {`);
    lines.push(`    // 1. Gate Weave (Micro-vaivén de arrastre analógico en la ventanilla de cámara)`);
    lines.push(
      `    ${layerVar}.property("Transform").property("Position").expression = "wiggle(${spec.frequencyHz.toFixed(1)}, ${spec.gateWeavePx.toFixed(1)});";`
    );
    lines.push(`    // 2. Shutter Exposure Flicker (Variación analógica de obturador rotativo)`);
    lines.push(
      `    ${layerVar}.property("Transform").property("Opacity").expression = "value + (wiggle(${spec.frequencyHz.toFixed(1)}, ${(spec.amplitudeEv * 40.0).toFixed(1)}) - value);";`
    );
    lines.push(`  } catch(e) {}`);

    return lines;
  }
}
