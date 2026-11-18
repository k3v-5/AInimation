import { Composition } from "../../core/composition.js";
import { DeterminismError } from "../../errors/runtime-errors.js";
import { ProjectSerializer } from "../persistence/ProjectSerializer.js";

/**
 * Validador de determinismo de evaluación temporal (Fase 18).
 */
export class DeterminismValidator {
  /**
   * Ejecuta múltiples evaluaciones sobre una composición en puntos temporales clave y comprueba repetibilidad estricta.
   */
  public static verifyDeterminism(comp: Composition, testTimes: number[] = [0, 0.5, 1.0, 2.5]): { verified: boolean; hash: string } {
    const hashes: string[] = [];

    for (const t of testTimes) {
      const state1 = comp.evaluate(t);
      const state2 = comp.evaluate(t);

      const hash1 = ProjectSerializer.hashProject(state1);
      const hash2 = ProjectSerializer.hashProject(state2);

      if (hash1 !== hash2) {
        throw new DeterminismError(
          `Non-deterministic evaluation detected for composition '${comp.name}' at t=${t}s: hash1='${hash1}' !== hash2='${hash2}'`
        );
      }

      hashes.push(`${t}:${hash1}`);
    }

    const overallHash = ProjectSerializer.hashProject(hashes);
    return { verified: true, hash: overallHash };
  }
}
