import { Composition } from "../core/composition.js";
import { deserializeComposition } from "../serialization/deserializer.js";

/**
 * Deserializador determinista de proyectos persistidos a instancias de Composition (Fase 18).
 */
export class ProjectDeserializer {
  public static deserialize(rawProject: unknown): Composition {
    const rawObj = rawProject as any;
    const projectToDeserialize = rawObj.composition
      ? rawObj
      : { schemaVersion: "0.2.0", composition: rawObj };

    return deserializeComposition(projectToDeserialize);
  }
}
