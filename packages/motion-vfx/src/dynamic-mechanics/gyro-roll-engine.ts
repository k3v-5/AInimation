import {
  CentrifugalGyroRollSpec,
  CentrifugalGyroRollSpecInput,
  CentrifugalGyroRollSpecSchema,
} from "./mechanics-types.js";

/**
 * Motor de rotación giroscópica centrífuga en eje Z (Hanumankind / Big Dawgs).
 */
export class GyroRollEngine {
  /**
   * Calcula el ángulo de rotación instantáneo theta(t) en función del progreso temporal normalizado tau en [0, 1].
   */
  public static evaluateRollAngle(
    tau: number,
    totalDegrees: number,
    direction: "CLOCKWISE" | "COUNTER_CLOCKWISE" = "CLOCKWISE",
    easing: "SMOOTH" | "EXPONENTIAL" | "LINEAR" = "SMOOTH"
  ): number {
    const clampedTau = Math.max(0.0, Math.min(1.0, tau));
    let progress = clampedTau;

    if (easing === "SMOOTH") {
      progress = (1.0 - Math.cos(Math.PI * clampedTau)) / 2.0;
    } else if (easing === "EXPONENTIAL") {
      progress = Math.pow(clampedTau, 2.0);
    }

    const sign = direction === "CLOCKWISE" ? 1.0 : -1.0;
    return Number((sign * totalDegrees * progress).toFixed(2));
  }

  /**
   * Genera los keyframes discretos de rotación Z para After Effects.
   */
  public static generateRotationKeyframes(
    specInput: CentrifugalGyroRollSpecInput,
    fps: number
  ): Array<{ timeSeconds: number; angleDegrees: number }> {
    const spec = CentrifugalGyroRollSpecSchema.parse(specInput);
    const totalFrames = Math.max(2, Math.round(spec.durationSeconds * fps));
    const kfs: Array<{ timeSeconds: number; angleDegrees: number }> = [];

    for (let f = 0; f <= totalFrames; f++) {
      const tau = f / totalFrames;
      const t = Number((spec.startTimeSeconds + (f / fps)).toFixed(5));
      const angle = this.evaluateRollAngle(tau, spec.totalRollDegrees, spec.direction, spec.easing);
      kfs.push({ timeSeconds: t, angleDegrees: angle });
    }

    return kfs;
  }

  /**
   * Genera el código ExtendScript para ensamblar el giro giroscópico $360^\circ$ sin costuras.
   */
  public static exportToExtendScript(
    specInput: CentrifugalGyroRollSpecInput,
    fps: number,
    options: { layerVarName?: string } = {}
  ): string[] {
    const spec = CentrifugalGyroRollSpecSchema.parse(specInput);
    const layerVar = options.layerVarName ?? "videoLyr";
    const kfs = this.generateRotationKeyframes(spec, fps);
    const lines: string[] = [];

    lines.push(`  // === CENTRIFUGAL GYRO ROLL: ${spec.id} (${spec.totalRollDegrees}deg ${spec.direction}) ===`);
    lines.push(`  try {`);
    lines.push(`    if (${layerVar}) {`);
    lines.push(`      ${layerVar}.motionBlur = true; // Invariante obligatoria`);
    lines.push(``);

    // 1. Motion Tile con replicación de bordes para evitar franjas negras
    if (spec.mirrorEdges) {
      lines.push(`      // 1. Replicación en espejo Motion Tile para rotaciones angulares`);
      lines.push(`      var tileFx = ${layerVar}.property("Effects").addProperty("ADBE Motion2");`);
      lines.push(`      if (tileFx) {`);
      lines.push(`        tileFx.property("Output Width").setValue(250.0);`);
      lines.push(`        tileFx.property("Output Height").setValue(250.0);`);
      lines.push(`        tileFx.property("Mirror Edges").setValue(true);`);
      lines.push(`      }`);
      lines.push(``);
    }

    // 2. Escala mínima circunscrita
    lines.push(`      // 2. Escala circunscrita mínima (sqrt(2) * 100 ~ 141.42%)`);
    lines.push(
      `      ${layerVar}.property("Transform").property("Scale").setValue([${spec.scaleBufferPercent.toFixed(1)}, ${spec.scaleBufferPercent.toFixed(1)}]);`
    );
    lines.push(``);

    // 3. Keyframes de rotación en Z
    lines.push(`      // 3. Keyframes de rotación giroscópica continua`);
    lines.push(`      var rotProp = ${layerVar}.property("Transform").property("Rotation");`);
    for (const kf of kfs) {
      lines.push(
        `      rotProp.setValueAtTime(${kf.timeSeconds.toFixed(4)}, ${kf.angleDegrees.toFixed(1)});`
      );
    }

    lines.push(`    }`);
    lines.push(`  } catch(e) {`);
    lines.push(`    alert('Error in GyroRollEngine: ' + e.toString());`);
    lines.push(`  }`);

    return lines;
  }
}
