export interface AEShapeRectDefinition {
  type: "rect";
  size: [number, number];
  position?: [number, number];
  roundness?: number;
}

export interface AEShapeEllipseDefinition {
  type: "ellipse";
  size: [number, number];
  position?: [number, number];
}

export interface AEShapeTrimPathsDefinition {
  type: "trim_paths";
  start?: number; // 0..100
  end?: number;   // 0..100
  offset?: number;// degrees
}

export interface AEShapeRepeaterDefinition {
  type: "repeater";
  copies: number;
  offset?: number;
  transform?: {
    position?: [number, number];
    scale?: [number, number];
    rotation?: number;
    startOpacity?: number;
    endOpacity?: number;
  };
}

export interface AEShapeDefinition {
  name: string;
  contents: Array<AEShapeRectDefinition | AEShapeEllipseDefinition | AEShapeTrimPathsDefinition | AEShapeRepeaterDefinition>;
  fillColor?: [number, number, number]; // 0..1 RGB
  strokeColor?: [number, number, number];
  strokeWidth?: number;
}

export class AEShapeCompiler {
  /**
   * Compila una definición de Shape Layer a código ExtendScript JSX.
   */
  public static compileShapeLayer(
    compVar: string,
    layerName: string,
    shapes: AEShapeDefinition[]
  ): string[] {
    const lines: string[] = [];
    const layerVar = `shapeLayer_${layerName.replace(/[^a-zA-Z0-9_]/g, "_")}`;

    lines.push(`var ${layerVar} = ${compVar}.layers.addShape();`);
    lines.push(`${layerVar}.name = "${layerName}";`);

    for (let sIdx = 0; sIdx < shapes.length; sIdx++) {
      const shape = shapes[sIdx];
      const groupVar = `group_${sIdx}_${layerVar}`;

      lines.push(`var ${groupVar} = ${layerVar}.property("Contents").addProperty("ADBE Vector Group");`);
      lines.push(`${groupVar}.name = "${shape.name}";`);
      lines.push(`var ${groupVar}_contents = ${groupVar}.property("Contents");`);

      for (const item of shape.contents) {
        if (item.type === "rect") {
          const rectVar = `rect_${groupVar}`;
          lines.push(`var ${rectVar} = ${groupVar}_contents.addProperty("ADBE Vector Shape - Rect");`);
          lines.push(`${rectVar}.property("Size").setValue([${item.size[0]}, ${item.size[1]}]);`);
          if (item.position) {
            lines.push(`${rectVar}.property("Position").setValue([${item.position[0]}, ${item.position[1]}]);`);
          }
          if (item.roundness !== undefined) {
            lines.push(`${rectVar}.property("Roundness").setValue(${item.roundness});`);
          }
        } else if (item.type === "ellipse") {
          const ellVar = `ell_${groupVar}`;
          lines.push(`var ${ellVar} = ${groupVar}_contents.addProperty("ADBE Vector Shape - Ellipse");`);
          lines.push(`${ellVar}.property("Size").setValue([${item.size[0]}, ${item.size[1]}]);`);
          if (item.position) {
            lines.push(`${ellVar}.property("Position").setValue([${item.position[0]}, ${item.position[1]}]);`);
          }
        } else if (item.type === "trim_paths") {
          const trimVar = `trim_${groupVar}`;
          lines.push(`var ${trimVar} = ${groupVar}_contents.addProperty("ADBE Vector Filter - Trim");`);
          if (item.start !== undefined) lines.push(`${trimVar}.property("Start").setValue(${item.start});`);
          if (item.end !== undefined) lines.push(`${trimVar}.property("End").setValue(${item.end});`);
          if (item.offset !== undefined) lines.push(`${trimVar}.property("Offset").setValue(${item.offset});`);
        } else if (item.type === "repeater") {
          const repVar = `rep_${groupVar}`;
          lines.push(`var ${repVar} = ${groupVar}_contents.addProperty("ADBE Vector Filter - Repeater");`);
          lines.push(`${repVar}.property("Copies").setValue(${item.copies});`);
          if (item.offset !== undefined) lines.push(`${repVar}.property("Offset").setValue(${item.offset});`);
          if (item.transform) {
            const repTrans = `${repVar}.property("Transform")`;
            if (item.transform.position) {
              lines.push(`${repTrans}.property("Position").setValue([${item.transform.position[0]}, ${item.transform.position[1]}]);`);
            }
            if (item.transform.scale) {
              lines.push(`${repTrans}.property("Scale").setValue([${item.transform.scale[0]}, ${item.transform.scale[1]}]);`);
            }
            if (item.transform.rotation !== undefined) {
              lines.push(`${repTrans}.property("Rotation").setValue(${item.transform.rotation});`);
            }
          }
        }
      }

      if (shape.fillColor) {
        const fillVar = `fill_${groupVar}`;
        lines.push(`var ${fillVar} = ${groupVar}_contents.addProperty("ADBE Vector Graphic - Fill");`);
        lines.push(`${fillVar}.property("Color").setValue([${shape.fillColor[0]}, ${shape.fillColor[1]}, ${shape.fillColor[2]}]);`);
      }

      if (shape.strokeColor) {
        const strokeVar = `stroke_${groupVar}`;
        lines.push(`var ${strokeVar} = ${groupVar}_contents.addProperty("ADBE Vector Graphic - Stroke");`);
        lines.push(`${strokeVar}.property("Color").setValue([${shape.strokeColor[0]}, ${shape.strokeColor[1]}, ${shape.strokeColor[2]}]);`);
        if (shape.strokeWidth !== undefined) {
          lines.push(`${strokeVar}.property("Stroke Width").setValue(${shape.strokeWidth});`);
        }
      }
    }

    return lines;
  }
}
