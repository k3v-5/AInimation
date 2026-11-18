import { Composition } from "../../core/composition.js";
import { AspectRatio } from "../core/AspectRatio.js";
import { ThumbnailCandidate } from "../core/DeliveryPackage.js";
import { ThumbnailScorer } from "./ThumbnailScorer.js";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";

export class ThumbnailSelector {
  /**
   * Extrae determinísticamente los mejores N fotogramas candidatos para miniaturas.
   */
  public static selectThumbnails(
    comp: Composition,
    aspectRatio: AspectRatio = "9:16",
    count = 3
  ): ThumbnailCandidate[] {
    const duration = comp.duration;
    const candidates: ThumbnailCandidate[] = [];

    // Muestrear a lo largo de la línea de tiempo (mínimo 10 muestras espaciadas)
    const samples = Math.max(10, Math.floor(duration * 2));
    const step = duration / samples;

    for (let i = 1; i < samples; i++) {
      const t = Math.round(i * step * 100) / 100;
      const score = ThumbnailScorer.scoreFrame(comp, t);

      const artifactHash = ProjectSerializer.hashCanonical({
        compositionId: comp.id,
        timeSeconds: t,
        aspectRatio,
        score,
      });

      candidates.push({
        timeSeconds: t,
        aspectRatio,
        score,
        artifactHash,
        description: `High-impact candidate at ${t.toFixed(2)}s (Score: ${score})`,
      });
    }

    // Ordenar por score descendente, desempate por timeSeconds ascendente
    candidates.sort((a, b) => b.score - a.score || a.timeSeconds - b.timeSeconds);

    return candidates.slice(0, count);
  }
}
