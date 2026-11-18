import {
  BlackoutVacuumSpec,
  BlackoutVacuumSpecInput,
  BlackoutVacuumSpecSchema,
} from "./rhythm-types.js";
import { MusicalGrid } from "./musical-grid.js";

/**
 * Motor de vacío visual y corte a negro previo al drop (Blackout Drop & Audio Vacuum).
 */
export class BlackoutVacuumEngine {
  /**
   * Calcula la ventana de vacío temporal cuantizada a la rejilla de fotogramas.
   */
  public static calculateVacuumWindow(
    specInput: BlackoutVacuumSpecInput,
    fps: number
  ): {
    vacuumStartSeconds: number;
    dropTimeSeconds: number;
    vacuumDurationSeconds: number;
    impactFlashEndSeconds?: number;
  } {
    const spec = BlackoutVacuumSpecSchema.parse(specInput);
    const dropTimeSnapped = MusicalGrid.snapToFrame(spec.dropTimeSeconds, fps);
    const vacuumDurationSnapped = MusicalGrid.snapToFrame(spec.vacuumDurationSeconds, fps);
    const vacuumStartSnapped = Math.max(0.0, MusicalGrid.snapToFrame(dropTimeSnapped - vacuumDurationSnapped, fps));

    const result: {
      vacuumStartSeconds: number;
      dropTimeSeconds: number;
      vacuumDurationSeconds: number;
      impactFlashEndSeconds?: number;
    } = {
      vacuumStartSeconds: vacuumStartSnapped,
      dropTimeSeconds: dropTimeSnapped,
      vacuumDurationSeconds: Number((dropTimeSnapped - vacuumStartSnapped).toFixed(6)),
    };

    if (spec.impactFlashFrame) {
      const frameSec = 1.0 / fps;
      result.impactFlashEndSeconds = MusicalGrid.snapToFrame(dropTimeSnapped + frameSec, fps);
    }

    return result;
  }

  /**
   * Genera las sentencias ExtendScript para inyectar el apagón y flash de impacto en After Effects.
   */
  public static exportToExtendScript(
    specInput: BlackoutVacuumSpecInput,
    fps: number,
    options: { compVarName?: string } = {}
  ): string[] {
    const spec = BlackoutVacuumSpecSchema.parse(specInput);
    const compVar = options.compVarName ?? "comp";
    const window = this.calculateVacuumWindow(spec, fps);
    const lines: string[] = [];

    lines.push(`  // === BLACKOUT VACUUM & IMPACT DROP: ${spec.id} ===`);
    lines.push(`  try {`);
    lines.push(`    // 1. Capa de Vacío Negro Absoluto`);
    lines.push(
      `    var blackLyr = ${compVar}.layers.addSolid([0.0, 0.0, 0.0], "[BLACKOUT VACUUM] ${spec.id}", ${compVar}.width, ${compVar}.height, 1.0);`
    );
    lines.push(`    blackLyr.startTime = 0.0;`);
    lines.push(`    blackLyr.inPoint = ${window.vacuumStartSeconds.toFixed(4)};`);
    lines.push(`    blackLyr.outPoint = ${window.dropTimeSeconds.toFixed(4)};`);

    // 2. Destello de 1 frame en el impacto
    if (spec.impactFlashFrame && window.impactFlashEndSeconds !== undefined) {
      lines.push(`    // 2. Destello de 1 frame en el Beat Drop exacto`);
      lines.push(
        `    var flashLyr = ${compVar}.layers.addSolid([1.0, 1.0, 1.0], "[IMPACT FLASH] ${spec.id}", ${compVar}.width, ${compVar}.height, 1.0);`
      );
      lines.push(`    flashLyr.blendingMode = BlendingMode.ADD;`);
      lines.push(`    flashLyr.startTime = 0.0;`);
      lines.push(`    flashLyr.inPoint = ${window.dropTimeSeconds.toFixed(4)};`);
      lines.push(`    flashLyr.outPoint = ${window.impactFlashEndSeconds.toFixed(4)};`);
    }

    lines.push(`  } catch(e) {`);
    lines.push(`    alert('Error in BlackoutVacuumEngine: ' + e.toString());`);
    lines.push(`  }`);

    return lines;
  }
}
