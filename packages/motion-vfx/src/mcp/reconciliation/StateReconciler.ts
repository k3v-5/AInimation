export interface ExpectedLayerState {
  id: string;
  name: string;
  inPoint: number;
  outPoint: number;
  position: [number, number];
  scale?: [number, number];
  rotation?: number;
}

export interface ActualLayerState {
  index: number;
  name: string;
  inPoint: number;
  outPoint: number;
  position?: [number, number];
  scale?: [number, number];
  rotation?: number;
}

export interface ReconciliationReport {
  isEquivalent: boolean;
  status: "pass" | "warning" | "mismatch";
  discrepancies: string[];
  maxSpatialDeltaPx: number;
  evaluatedLayersCount: number;
}

/**
 * Motor de Reconciliación de Estado (Expected IR vs Actual AE Runtime) (REQ-021).
 * Compara las cotas proyectadas en la IR contra las cotas reales reportadas por After Effects.
 */
export class StateReconciler {
  public static readonly POS_TOLERANCE_PX = 0.05;
  public static readonly TIME_TOLERANCE_SEC = 0.04; // 1 fotograma a 25fps

  /**
   * Reconcilia el estado esperado contra el estado real.
   */
  public static reconcile(
    expected: ExpectedLayerState[],
    actual: ActualLayerState[]
  ): ReconciliationReport {
    const discrepancies: string[] = [];
    let maxDelta = 0.0;

    for (const exp of expected) {
      const act = actual.find((a) => a.name === exp.name);
      if (!act) {
        discrepancies.push(`Missing layer in AE: expected '${exp.name}' (ID: ${exp.id})`);
        continue;
      }

      // 1. Verificación temporal (InPoint / OutPoint)
      const inDelta = Math.abs(exp.inPoint - act.inPoint);
      const outDelta = Math.abs(exp.outPoint - act.outPoint);
      if (inDelta > this.TIME_TOLERANCE_SEC || outDelta > this.TIME_TOLERANCE_SEC) {
        discrepancies.push(
          `Timing mismatch on '${exp.name}': inDelta=${inDelta.toFixed(3)}s, outDelta=${outDelta.toFixed(3)}s`
        );
      }

      // 2. Verificación espacial (Posición X, Y) si está disponible
      if (act.position) {
        const dx = Math.abs(exp.position[0] - act.position[0]);
        const dy = Math.abs(exp.position[1] - act.position[1]);
        const spatialDelta = Math.sqrt(dx * dx + dy * dy);
        if (spatialDelta > maxDelta) maxDelta = spatialDelta;

        if (spatialDelta > this.POS_TOLERANCE_PX) {
          discrepancies.push(
            `Spatial mismatch on '${exp.name}': expected [${exp.position}], got [${act.position}] (delta=${spatialDelta.toFixed(3)}px)`
          );
        }
      }
    }

    const isEquivalent = discrepancies.length === 0;
    const status: ReconciliationReport["status"] = isEquivalent
      ? "pass"
      : maxDelta <= 1.0
      ? "warning"
      : "mismatch";

    return {
      isEquivalent,
      status,
      discrepancies,
      maxSpatialDeltaPx: Number(maxDelta.toFixed(4)),
      evaluatedLayersCount: expected.length,
    };
  }
}
