import {
  VisualizationDataset,
  VisualizationRequest,
  VisualizationIR,
} from "./types.js";
import { validateVisualizationDataset } from "./validation.js";
import { assertVisualizationSafeZone } from "./geometry.js";
import { validateAnimationMonotonicity } from "./animation.js";
import { computeVisualizationChecksum } from "./checksum.js";
import { compileAnimatedBarChart } from "./animated-bar-chart-compiler.js";
import { compileTrendLineGraph } from "./trend-line-graph-compiler.js";
import { generateBigStatCard } from "./big-stat-card-generator.js";
import { compileChronologyTimeline } from "./chronology-timeline-generator.js";
import { DataVisualizationValidationError } from "./errors.js";

/**
 * REQ-025 §54: Facade central del Data Visualization Engine.
 */
export class DataVisualizationEngine {
  public compile(
    dataset: VisualizationDataset,
    request: VisualizationRequest
  ): VisualizationIR {
    // 1. Validar dataset si es requerido por el tipo de visualización
    if (request.type !== "BIG_STAT") {
      const validation = validateVisualizationDataset(dataset);
      if (!validation.valid) {
        const firstError = validation.issues.find((i) => i.severity === "ERROR");
        throw new DataVisualizationValidationError(
          firstError ? `[${firstError.code}] ${firstError.message}` : "Dataset inválido"
        );
      }
    }

    let ir: VisualizationIR;

    // 2. Compilar según el tipo solicitado
    switch (request.type) {
      case "BAR_CHART": {
        ir = compileAnimatedBarChart(dataset, request.config, request.context);
        break;
      }
      case "TREND_LINE": {
        ir = compileTrendLineGraph(dataset, request.config, request.context);
        break;
      }
      case "BIG_STAT": {
        ir = generateBigStatCard(request.config, request.context);
        break;
      }
      case "CHRONOLOGY_TIMELINE": {
        ir = compileChronologyTimeline(dataset, request.config, request.context);
        break;
      }
      default: {
        throw new DataVisualizationValidationError(
          `Tipo de visualización '${(request as any).type}' no soportado.`
        );
      }
    }

    // 3. Validar geometría respecto a la Safe Zone
    try {
      assertVisualizationSafeZone(ir);
    } catch (err: any) {
      // Registrar en diagnostics o rethrow si es crítico
      if (!ir.warnings) ir.warnings = [];
      ir.warnings.push(err.message);
    }

    // 4. Validar monotonicidad de las animaciones
    for (const anim of ir.animations) {
      if (!validateAnimationMonotonicity(anim)) {
        throw new DataVisualizationValidationError(
          `Animación no monotónica detectada en elemento '${anim.elementId}'.`
        );
      }
    }

    // 5. Sellar criptográficamente mediante SHA-256 canónico
    ir.checksumSha256 = computeVisualizationChecksum(ir);

    return ir;
  }
}
