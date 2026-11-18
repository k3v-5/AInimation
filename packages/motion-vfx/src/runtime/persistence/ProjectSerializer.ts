import * as crypto from "node:crypto";
import { Composition } from "../../core/composition.js";
import { SerializationError } from "../../errors/index.js";
import { serializeComposition as coreSerializeComposition } from "../../serialization/serializer.js";

/**
 * Serializador canónico y generador de hash determinista libre de contaminación temporal (Fase 18).
 */
export class ProjectSerializer {
  /**
   * Serializa un objeto o valor a formato JSON canónico determinista.
   * Reglas:
   * 1. Claves de objetos ordenadas lexicográficamente.
   * 2. Arrays preservan su orden original exacto.
   * 3. Normalización de -0 a 0.
   * 4. Validación de números finitos (rechaza NaN e Infinity).
   * 5. Saltos de línea consistentes \n y sin espacios redundantes.
   */
  public static canonicalize(value: unknown): string {
    return this.stringifyValue(value);
  }

  /**
   * Calcula el hash criptográfico SHA-256 de la representación canónica de un proyecto.
   */
  public static hashProject(project: unknown): string {
    const canonical = this.canonicalize(project);
    return crypto.createHash("sha256").update(canonical, "utf8").digest("hex");
  }

  /**
   * Serializa una instancia de Composition a su representación serializada canónica.
   */
  public static serializeComposition(comp: Composition): Record<string, unknown> {
    const raw = coreSerializeComposition(comp);
    return JSON.parse(this.canonicalize(raw));
  }

  private static stringifyValue(val: unknown): string {
    if (val === null) return "null";
    if (typeof val === "boolean") return val ? "true" : "false";

    if (typeof val === "number") {
      if (!Number.isFinite(val)) {
        throw new SerializationError(`Non-finite number encountered during canonicalization: ${val}`);
      }
      // Normalizar -0 a 0
      if (Object.is(val, -0)) {
        return "0";
      }
      return val.toString();
    }

    if (typeof val === "string") {
      return JSON.stringify(val);
    }

    if (Array.isArray(val)) {
      const items = val.map((item) => this.stringifyValue(item));
      return `[${items.join(",")}]`;
    }

    if (typeof val === "object") {
      const obj = val as Record<string, unknown>;
      const keys = Object.keys(obj).sort();
      const entries: string[] = [];

      for (const key of keys) {
        const itemVal = obj[key];
        if (itemVal !== undefined && typeof itemVal !== "function" && typeof itemVal !== "symbol") {
          entries.push(`${JSON.stringify(key)}:${this.stringifyValue(itemVal)}`);
        }
      }

      return `{${entries.join(",")}}`;
    }

    throw new SerializationError(`Unsupported type encountered during canonicalization: ${typeof val}`);
  }
}
