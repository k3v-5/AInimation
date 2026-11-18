import { Composition } from "../../core/composition.js";
import { deserializeComposition as coreDeserializeComposition } from "../../serialization/deserializer.js";
import { ProjectEnvelope } from "./ProjectEnvelope.js";

/**
 * Deserializador determinista de Envelopes a objetos puros del Motion Engine (Fase 18).
 */
export class ProjectDeserializer {
  /**
   * Reconstruye una instancia de Composition a partir del envelope persistido.
   */
  public static deserializeComposition(envelope: ProjectEnvelope): Composition {
    const rawProject = envelope.project as any;
    const projectToDeserialize = rawProject.composition ? rawProject : { schemaVersion: "0.2.0", composition: rawProject };
    return coreDeserializeComposition(projectToDeserialize);
  }
}
