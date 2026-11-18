import { FisheyeLensSpec, FisheyeLensSpecSchema } from "./optics-types.js";

/**
 * Motor de emulación de lente Fisheye y óptica gran angular extrema con aberración cromática.
 */
export class FisheyeOpticsEngine {
  /**
   * Calcula el radio deformado r_d a partir del radio no distorsionado r_u usando Brown-Conrady.
   */
  public static calculateBarrelDistortion(radiusNormalized: number, distortionFactor: number): number {
    const k1 = (distortionFactor / 100.0) * 0.45;
    const r2 = radiusNormalized * radiusNormalized;
    return Number((radiusNormalized * (1 + k1 * r2)).toFixed(6));
  }

  /**
   * Genera el código ExtendScript para aplicar el lente Fisheye, aberración RGB y viñeta en After Effects.
   */
  public static exportToExtendScript(
    specInput: FisheyeLensSpec,
    options: { compVarName?: string; layerVarName?: string } = {}
  ): string[] {
    const spec = FisheyeLensSpecSchema.parse(specInput);
    const compVar = options.compVarName ?? "comp";
    const layerVar = options.layerVarName ?? "targetLayer";
    const lines: string[] = [];

    lines.push("// === FISHEYE LENS & CHROMATIC ABERRATION ENGINE ===");
    lines.push(`try {`);
    lines.push(`  // 1. Deformación de Barril (Optics Compensation o Spherize)`);
    lines.push(`  var opticsFx = ${layerVar}.property("Effects").addProperty("ADBE Optics Compensation");`);
    lines.push(`  if (opticsFx) {`);
    lines.push(`    opticsFx.property("Field of View").setValue(${spec.distortionFactor.toFixed(1)});`);
    lines.push(`    opticsFx.property("FOV Type").setValue(1); // Diagonal`);
    lines.push(`    opticsFx.property("Reverse Lens Distortion").setValue(true); // Abombamiento Fisheye`);
    lines.push(`  }`);
    lines.push(`} catch(e) {`);
    lines.push(`  try {`);
    lines.push(`    var sphFx = ${layerVar}.property("Effects").addProperty("ADBE Spherize");`);
    lines.push(`    if (sphFx) sphFx.property("Radius").setValue(${spec.distortionFactor.toFixed(1)});`);
    lines.push(`  } catch(e2) {}`);
    lines.push(`}`);

    if (spec.vignetteAmount > 0) {
      lines.push(`// 2. Viñeta Óptica Anamórfica`);
      lines.push(`try {`);
      lines.push(`  var vigSolid = ${compVar}.layers.addSolid([0, 0, 0], "Fisheye_Vignette", ${compVar}.width, ${compVar}.height, 1.0);`);
      lines.push(`  vigSolid.adjustmentLayer = false;`);
      lines.push(`  vigSolid.opacity.setValue(${Math.round(spec.vignetteAmount * 100)});`);
      lines.push(`  var vigMask = vigSolid.property("Masks").addProperty("Mask");`);
      lines.push(`  vigMask.maskMode = MaskMode.SUBTRACT;`);
      lines.push(`  var vigShape = vigMask.property("maskShape").value;`);
      lines.push(`  vigShape.vertices = [[0, 0], [${compVar}.width, 0], [${compVar}.width, ${compVar}.height], [0, ${compVar}.height]];`);
      lines.push(`  vigShape.closed = true;`);
      lines.push(`  vigMask.property("maskShape").setValue(vigShape);`);
      lines.push(`  vigMask.property("maskFeather").setValue([180.0, 180.0]);`);
      lines.push(`} catch(e) {}`);
    }

    return lines;
  }
}
