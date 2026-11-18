import {
  PerspectiveAnchorSpec,
  PerspectiveAnchorSpecInput,
  PerspectiveAnchorSpecSchema,
} from "./kinetic-typography-types.js";

/**
 * Motor de anclaje espacial de tipografía en perspectiva 3D (Spatial Geometry Anchoring).
 */
export class PerspectiveAnchorEngine {
  /**
   * Resuelve la posición y rotación 3D canónicas en función del alineamiento con puntos de fuga.
   */
  public static resolveTransform3D(specInput: PerspectiveAnchorSpecInput): {
    position: [number, number, number];
    rotation: [number, number, number];
  } {
    const spec = PerspectiveAnchorSpecSchema.parse(specInput);

    switch (spec.vanishingPointAlign) {
      case "FLOOR_RECEDING":
        // Plano de suelo en retroceso (acostado sobre el asfalto / calle)
        return {
          position: [spec.position3D[0], spec.position3D[1] + 350, spec.position3D[2] + 400],
          rotation: [72.0, spec.rotation3D[1], spec.rotation3D[2]],
        };

      case "WALL_LEFT":
        // Pared lateral izquierda en perspectiva de fuga
        return {
          position: [spec.position3D[0] - 300, spec.position3D[1], spec.position3D[2] + 200],
          rotation: [spec.rotation3D[0], 55.0, spec.rotation3D[2]],
        };

      case "WALL_RIGHT":
        // Pared lateral derecha
        return {
          position: [spec.position3D[0] + 300, spec.position3D[1], spec.position3D[2] + 200],
          rotation: [spec.rotation3D[0], -55.0, spec.rotation3D[2]],
        };

      case "CENTER":
      default:
        return {
          position: spec.position3D,
          rotation: spec.rotation3D,
        };
    }
  }

  /**
   * Genera el código ExtendScript para activar 3D y orientar la capa en perspectiva.
   */
  public static exportToExtendScript(
    specInput: PerspectiveAnchorSpecInput,
    options: { layerVarName?: string } = {}
  ): string[] {
    const spec = PerspectiveAnchorSpecSchema.parse(specInput);
    const layerVar = options.layerVarName ?? "textLyr";
    const xform = this.resolveTransform3D(spec);
    const lines: string[] = [];

    lines.push(`  // === 3D PERSPECTIVE ANCHOR: ${spec.id} (${spec.vanishingPointAlign}) ===`);
    lines.push(`  try {`);
    lines.push(`    ${layerVar}.threeDLayer = true;`);
    lines.push(
      `    ${layerVar}.property("Transform").property("Position").setValue([${xform.position[0].toFixed(1)}, ${xform.position[1].toFixed(1)}, ${xform.position[2].toFixed(1)}]);`
    );
    lines.push(
      `    ${layerVar}.property("Transform").property("X Rotation").setValue(${xform.rotation[0].toFixed(1)});`
    );
    lines.push(
      `    ${layerVar}.property("Transform").property("Y Rotation").setValue(${xform.rotation[1].toFixed(1)});`
    );
    lines.push(
      `    ${layerVar}.property("Transform").property("Z Rotation").setValue(${xform.rotation[2].toFixed(1)});`
    );
    lines.push(`  } catch(e) {`);
    lines.push(`    alert('Error in PerspectiveAnchorEngine: ' + e.toString());`);
    lines.push(`  }`);

    return lines;
  }
}
