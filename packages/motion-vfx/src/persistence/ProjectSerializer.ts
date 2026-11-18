import * as crypto from "node:crypto";
import { Composition } from "../core/composition.js";
import { SerializationError } from "../errors/index.js";
import { serializeComposition } from "../serialization/serializer.js";

/**
 * Serializador determinista canónico y generador de hashes criptográficos SHA-256 (Fase 18).
 */
export class ProjectSerializer {
  /**
   * Serializa cualquier valor a JSON canónico determinista.
   */
  public static canonicalize(value: unknown): string {
    return this.stringifyValue(value);
  }

  /**
   * Alias de canonicalize para conveniencia.
   */
  public static canonicalStringify(value: unknown): string {
    return this.canonicalize(value);
  }

  /**
   * Calcula el hash SHA-256 de la representación canónica de un valor.
   */
  public static hashCanonical(value: unknown): string {
    const canonical = this.canonicalize(value);
    return crypto.createHash("sha256").update(canonical, "utf8").digest("hex");
  }

  /**
   * Serializa una composición completa a su representación canónica como JSON plano.
   */
  public static serialize(comp: Composition): Record<string, unknown> {
    const raw = serializeComposition(comp);
    return JSON.parse(this.canonicalize(raw));
  }

  private static stringifyValue(val: unknown): string {
    if (val === null) return "null";
    if (typeof val === "boolean") return val ? "true" : "false";

    if (typeof val === "number") {
      if (!Number.isFinite(val)) {
        throw new SerializationError(`Non-finite number encountered during canonicalization: ${val}`);
      }
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
