import { SerializationError } from "../../../errors/index.js";
import { DSLDocument, DSLNode } from "../types/index.js";

/**
 * Parser para el DSL de animación (Fase 3E).
 * Normaliza y resuelve variables declaradas ($varName).
 */
export class DSLParser {
  /**
   * Parsea un string JSON o un objeto literal a una estructura DSLDocument tipada con variables resueltas.
   */
  public static parse(input: string | Record<string, unknown>): DSLDocument {
    let raw: Record<string, unknown>;

    if (typeof input === "string") {
      try {
        raw = JSON.parse(input);
      } catch (err: any) {
        throw new SerializationError(`Invalid JSON in DSL input: ${err.message}`);
      }
    } else if (typeof input === "object" && input !== null) {
      raw = input;
    } else {
      throw new SerializationError("DSL input must be a JSON string or an object.");
    }

    const version = raw.version ?? 1;
    if (version !== 1) {
      throw new SerializationError(`Unsupported DSL version '${version}'. Only version 1 is supported.`);
    }

    const variables: Record<string, number | string> = {};
    if (raw.variables && typeof raw.variables === "object") {
      for (const [k, v] of Object.entries(raw.variables as Record<string, unknown>)) {
        if (typeof v === "number" || typeof v === "string") {
          variables[k] = v;
        }
      }
    }

    const rawAnimations = Array.isArray(raw.animations) ? raw.animations : [];
    const resolvedAnimations = rawAnimations.map((node) => this.resolveVariablesInNode(node, variables));

    return {
      version: 1,
      variables,
      animations: resolvedAnimations,
    };
  }

  private static resolveValue(val: unknown, vars: Record<string, number | string>): unknown {
    if (typeof val === "string" && val.startsWith("$")) {
      const varName = val.slice(1);
      if (varName in vars) {
        return vars[varName];
      }
      // Si la variable no está definida, dejamos el valor string para que el validador lance UNDEFINED_VARIABLE con ruta exacta
      return val;
    }

    if (val && typeof val === "object" && !Array.isArray(val)) {
      const copy: Record<string, unknown> = {};
      for (const [k, v] of Object.entries(val as Record<string, unknown>)) {
        copy[k] = this.resolveValue(v, vars);
      }
      return copy;
    }

    if (Array.isArray(val)) {
      return val.map((item) => this.resolveValue(item, vars));
    }

    return val;
  }

  private static resolveVariablesInNode(node: any, vars: Record<string, number | string>): DSLNode {
    if (!node || typeof node !== "object") {
      return node;
    }

    const resolved: any = {};
    for (const [k, v] of Object.entries(node)) {
      if (k === "children" && Array.isArray(v)) {
        resolved.children = v.map((child) => this.resolveVariablesInNode(child, vars));
      } else {
        resolved[k] = this.resolveValue(v, vars);
      }
    }

    return resolved as DSLNode;
  }
}
