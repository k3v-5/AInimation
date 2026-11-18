import { Color, PropertyTypeName, Vector2, Vector3 } from "../core/types.js";
import { ValidationError } from "../errors/index.js";

/**
 * Limita un valor numérico estrictamente al rango [0, 1].
 */
export function clamp01(value: number): number {
  if (Number.isNaN(value)) {
    return 0;
  }
  if (value <= 0) {
    return 0;
  }
  if (value >= 1) {
    return 1;
  }
  return value;
}

/**
 * Crea una copia profunda e inmutable de un valor de propiedad.
 */
export function cloneValue<T>(value: T): T {
  if (value === null || typeof value !== "object") {
    return value;
  }
  if (Array.isArray(value)) {
    return value.map((item) => cloneValue(item)) as unknown as T;
  }
  const copy: Record<string, unknown> = {};
  for (const key of Object.keys(value as Record<string, unknown>)) {
    copy[key] = cloneValue((value as Record<string, unknown>)[key]);
  }
  return copy as T;
}

/**
 * Detecta el tipo de valor soportado en el Core.
 */
export function detectValueType(val: unknown): PropertyTypeName {
  if (typeof val === "number") {
    return "number";
  }
  if (typeof val === "string") {
    return "string";
  }
  if (typeof val === "boolean") {
    return "boolean";
  }
  if (val && typeof val === "object") {
    const obj = val as Record<string, unknown>;
    if (typeof obj.r === "number" && typeof obj.g === "number" && typeof obj.b === "number" && typeof obj.a === "number") {
      return "color";
    }
    if (typeof obj.x === "number" && typeof obj.y === "number" && typeof obj.z === "number") {
      return "vector3";
    }
    if (typeof obj.x === "number" && typeof obj.y === "number") {
      return "vector2";
    }
  }
  return "unknown";
}

/**
 * Interpola linealmente entre dos valores soportados aplicando un progreso [0, 1].
 */
export function interpolate<T>(from: T, to: T, rawProgress: number): T {
  const p = clamp01(rawProgress);

  if (p === 0) {
    return cloneValue(from);
  }
  if (p === 1) {
    return cloneValue(to);
  }

  // 1. Tipo número
  if (typeof from === "number" && typeof to === "number") {
    return (from + (to - from) * p) as unknown as T;
  }

  // 2. Objetos vectoriales y color
  if (from && to && typeof from === "object" && typeof to === "object") {
    const fromObj = from as Record<string, unknown>;
    const toObj = to as Record<string, unknown>;

    // Vector2
    if (
      typeof fromObj.x === "number" &&
      typeof fromObj.y === "number" &&
      typeof toObj.x === "number" &&
      typeof toObj.y === "number" &&
      !("z" in fromObj || "z" in toObj)
    ) {
      return {
        x: fromObj.x + (toObj.x - fromObj.x) * p,
        y: fromObj.y + (toObj.y - fromObj.y) * p,
      } as unknown as T;
    }

    // Vector3
    if (
      typeof fromObj.x === "number" &&
      typeof fromObj.y === "number" &&
      typeof fromObj.z === "number" &&
      typeof toObj.x === "number" &&
      typeof toObj.y === "number" &&
      typeof toObj.z === "number"
    ) {
      return {
        x: fromObj.x + (toObj.x - fromObj.x) * p,
        y: fromObj.y + (toObj.y - fromObj.y) * p,
        z: fromObj.z + (toObj.z - fromObj.z) * p,
      } as unknown as T;
    }

    // Color
    if (
      typeof fromObj.r === "number" &&
      typeof fromObj.g === "number" &&
      typeof fromObj.b === "number" &&
      typeof fromObj.a === "number" &&
      typeof toObj.r === "number" &&
      typeof toObj.g === "number" &&
      typeof toObj.b === "number" &&
      typeof toObj.a === "number"
    ) {
      return {
        r: fromObj.r + (toObj.r - fromObj.r) * p,
        g: fromObj.g + (toObj.g - fromObj.g) * p,
        b: fromObj.b + (toObj.b - fromObj.b) * p,
        a: fromObj.a + (toObj.a - fromObj.a) * p,
      } as unknown as T;
    }
  }

  // 3. Strings y Booleanos (Interpolación escalonada/discreta: hold hasta completar)
  if (typeof from === "string" && typeof to === "string") {
    return (p < 1 ? from : to) as unknown as T;
  }

  if (typeof from === "boolean" && typeof to === "boolean") {
    return (p < 1 ? from : to) as unknown as T;
  }

  throw new ValidationError(
    `Cannot interpolate incompatible or unsupported types: from=${JSON.stringify(from)}, to=${JSON.stringify(to)}`
  );
}

/**
 * Interpola linealmente sin acotar el progreso al rango [0, 1] (necesario para Overshoot, Spring, Elastic, etc.).
 */
export function interpolateUnclamped<T>(from: T, to: T, p: number): T {
  if (p === 0) {
    return cloneValue(from);
  }
  if (p === 1) {
    return cloneValue(to);
  }

  // 1. Tipo número
  if (typeof from === "number" && typeof to === "number") {
    return (from + (to - from) * p) as unknown as T;
  }

  // 2. Objetos vectoriales y color
  if (from && to && typeof from === "object" && typeof to === "object") {
    const fromObj = from as Record<string, unknown>;
    const toObj = to as Record<string, unknown>;

    // Vector2
    if (
      typeof fromObj.x === "number" &&
      typeof fromObj.y === "number" &&
      typeof toObj.x === "number" &&
      typeof toObj.y === "number" &&
      !("z" in fromObj || "z" in toObj)
    ) {
      return {
        x: fromObj.x + (toObj.x - fromObj.x) * p,
        y: fromObj.y + (toObj.y - fromObj.y) * p,
      } as unknown as T;
    }

    // Vector3
    if (
      typeof fromObj.x === "number" &&
      typeof fromObj.y === "number" &&
      typeof fromObj.z === "number" &&
      typeof toObj.x === "number" &&
      typeof toObj.y === "number" &&
      typeof toObj.z === "number"
    ) {
      return {
        x: fromObj.x + (toObj.x - fromObj.x) * p,
        y: fromObj.y + (toObj.y - fromObj.y) * p,
        z: fromObj.z + (toObj.z - fromObj.z) * p,
      } as unknown as T;
    }

    // Color (los canales de color se acotan a [0, 1] por seguridad visual)
    if (
      typeof fromObj.r === "number" &&
      typeof fromObj.g === "number" &&
      typeof fromObj.b === "number" &&
      typeof fromObj.a === "number" &&
      typeof toObj.r === "number" &&
      typeof toObj.g === "number" &&
      typeof toObj.b === "number" &&
      typeof toObj.a === "number"
    ) {
      return {
        r: clamp01(fromObj.r + (toObj.r - fromObj.r) * p),
        g: clamp01(fromObj.g + (toObj.g - fromObj.g) * p),
        b: clamp01(fromObj.b + (toObj.b - fromObj.b) * p),
        a: clamp01(fromObj.a + (toObj.a - fromObj.a) * p),
      } as unknown as T;
    }
  }

  // 3. Strings y Booleanos (Interpolación escalonada/discreta: hold hasta completar)
  if (typeof from === "string" && typeof to === "string") {
    return (p < 1 ? from : to) as unknown as T;
  }

  if (typeof from === "boolean" && typeof to === "boolean") {
    return (p < 1 ? from : to) as unknown as T;
  }

  throw new ValidationError(
    `Cannot interpolate incompatible or unsupported types: from=${JSON.stringify(from)}, to=${JSON.stringify(to)}`
  );
}
