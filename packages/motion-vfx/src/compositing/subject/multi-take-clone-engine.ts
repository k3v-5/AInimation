import crypto from "crypto";
import {
  CloneTakeSpec,
  MultiTakeCloneConfig,
  MultiTakeCloneConfigSchema,
  SubjectCompositingPlan,
  SubjectCompositingPlanSchema,
} from "./detection-types.js";

/**
 * Motor de fusión multi-toma para el efecto "Clones" del mismo sujeto (Fase 19).
 */
export class MultiTakeCloneEngine {
  /**
   * Compila un plan de composición para fusionar múltiples tomas del mismo sujeto en un solo plano.
   */
  public static compile(configInput: MultiTakeCloneConfig): SubjectCompositingPlan {
    const config = MultiTakeCloneConfigSchema.parse(configInput);
    const extendScriptLines = this.generateExtendScript(config);

    const hashContent = JSON.stringify({
      type: "MULTI_TAKE_CLONES",
      takesCount: config.takes.length,
      edgeFeatherPx: config.edgeFeatherPx,
      duration: config.totalDurationSeconds,
      audioMode: config.audioMode,
    });
    const checksumSha256 = crypto.createHash("sha256").update(hashContent).digest("hex");

    return SubjectCompositingPlanSchema.parse({
      id: `plan_clones_${config.id}`,
      type: "MULTI_TAKE_CLONES",
      totalDurationSeconds: config.totalDurationSeconds,
      layersCount: config.takes.length,
      extendScriptLines,
      checksumSha256,
    });
  }

  /**
   * Calcula los intervalos espaciales horizontales de cada toma [xMin, xMax] en píxeles.
   */
  public static calculateSplitBounds(
    takes: CloneTakeSpec[],
    compWidth: number
  ): Array<{ takeId: string; xMin: number; xMax: number }> {
    const count = takes.length;
    return takes.map((take, idx) => {
      let xMin = 0;
      let xMax = compWidth;

      if (take.customSplitXNormalized !== undefined) {
        const split = take.customSplitXNormalized * compWidth;
        if (take.subjectZone === "LEFT") {
          xMin = 0;
          xMax = split;
        } else {
          xMin = split;
          xMax = compWidth;
        }
      } else {
        // Partición equitativa por número de tomas
        const colWidth = compWidth / count;
        xMin = Math.round(idx * colWidth);
        xMax = Math.round((idx + 1) * colWidth);
      }

      return { takeId: take.takeId, xMin, xMax };
    });
  }

  /**
   * Genera el código ExtendScript nativo para After Effects que fusiona las tomas como clones.
   */
  public static generateExtendScript(config: MultiTakeCloneConfig): string[] {
    const { compWidth, compHeight, fps, totalDurationSeconds, takes, edgeFeatherPx, audioMode } = config;
    const splitBounds = this.calculateSplitBounds(takes, compWidth);

    const lines: string[] = [
      "// ============================================================================",
      "//  MULTI-TAKE CLONE COMPOSITOR (SAME SUBJECT IN MULTIPLE POSITIONS)",
      `//  Takes: ${takes.length} | Resolution: ${compWidth}x${compHeight} @ ${fps}fps`,
      "// ============================================================================",
      "",
      `app.beginUndoGroup('Build Multi-Take Clones: ${config.id}');`,
      "try {",
      "  var project = app.project || app.newProject();",
      `  var cloneComp = project.items.addComp('Clones - ${config.id}', ${compWidth}, ${compHeight}, 1.0, ${totalDurationSeconds.toFixed(3)}, ${fps});`,
      "  cloneComp.bgColor = [0.02, 0.02, 0.03];",
      "  cloneComp.motionBlur = true;",
      "",
      "  function importTakeFile(pathStr) {",
      "    var f = new File(pathStr);",
      "    return f.exists ? project.importFile(new ImportOptions(f)) : null;",
      "  }",
      "",
    ];

    takes.forEach((take, idx) => {
      const normPath = take.assetPath.replace(/\\/g, "/");
      const bounds = splitBounds[idx];
      const isMasterBg = take.isMasterBackground || idx === 0;

      lines.push(`  // --- Toma ${idx + 1}: ${take.takeId} (Zona: ${take.subjectZone}) ---`);
      lines.push(`  var ft_${idx} = importTakeFile('${normPath}');`);
      lines.push(`  if (ft_${idx}) {`);
      lines.push(`    var lyr_${idx} = cloneComp.layers.add(ft_${idx});`);
      lines.push(`    lyr_${idx}.name = '[CLONE TAKE ${idx + 1}] ${take.subjectZone}${isMasterBg ? " (MASTER BG)" : ""}';`);
      lines.push(`    lyr_${idx}.startTime = 0.0;`);
      lines.push(`    lyr_${idx}.inPoint = ${take.inPointSeconds.toFixed(3)};`);
      lines.push(`    lyr_${idx}.outPoint = ${(take.inPointSeconds + take.durationSeconds).toFixed(3)};`);
      lines.push(`    lyr_${idx}.motionBlur = true;`);
      lines.push(`    lyr_${idx}.property('Transform').property('Position').setValue([${compWidth / 2}, ${compHeight / 2}]);`);
      lines.push(`    var sc_${idx} = Math.max((${compWidth} / ft_${idx}.width), (${compHeight} / ft_${idx}.height)) * 100.0;`);
      lines.push(`    lyr_${idx}.property('Transform').property('Scale').setValue([sc_${idx}, sc_${idx}]);`);

      // Control de audio para evitar multiplicar ruido de sala
      if (audioMode === "ACTIVE_SPEAKER" && !isMasterBg) {
        lines.push(`    lyr_${idx}.audioEnabled = false; // Desduplicación de ruido de fondo`);
      }

      // Máscara dividida (Split Matte) excepto si es la capa base de fondo completo
      if (!isMasterBg) {
        lines.push(`    // Máscara de división espacial para aislar al clon`);
        lines.push(`    var mask_${idx} = lyr_${idx}.property('Masks').addProperty('Mask');`);
        lines.push(`    var shp_${idx} = mask_${idx}.property('maskShape').value;`);
        lines.push(
          `    shp_${idx}.vertices = [[${bounds.xMin}, 0], [${bounds.xMax}, 0], [${bounds.xMax}, ${compHeight}], [${bounds.xMin}, ${compHeight}]];`
        );
        lines.push(`    shp_${idx}.closed = true;`);
        lines.push(`    mask_${idx}.property('maskShape').setValue(shp_${idx});`);
        lines.push(`    mask_${idx}.property('maskFeather').setValue([${edgeFeatherPx}, 0]); // Suavizado horizontal continuo`);
      }

      lines.push(`  }`);
      lines.push("");
    });

    lines.push("  app.endUndoGroup();");
    lines.push("  alert('¡Composición de Clones Multi-Toma generada con éxito!');");
    lines.push("} catch(e) {");
    lines.push("  app.endUndoGroup();");
    lines.push("  alert('Error al generar Clones: ' + e.toString());");
    lines.push("}");

    return lines;
  }
}
