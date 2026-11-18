import { getEasing } from "../animation/easing.js";
import { cloneValue, interpolate } from "../animation/interpolation.js";
import { validateKeyframeValue, validateTime } from "../validation/validators.js";
import { Keyframe } from "./keyframe.js";
import { EasingName, SpatialInterpolationType, SpatialTangent, Time } from "./types.js";

/**
 * Propiedad animable fundamental del Core.
 * Mantiene un valor base estático y una lista de keyframes ordenados.
 */
export class Property<T> {
  private baseValue: T;
  private keyframes: Keyframe<T>[] = [];

  constructor(initialValue: T) {
    validateKeyframeValue(initialValue);
    this.baseValue = cloneValue(initialValue);
  }

  /**
   * Obtiene una copia del valor base estático.
   */
  public getValue(): T {
    return cloneValue(this.baseValue);
  }

  /**
   * Actualiza el valor base estático.
   */
  public setValue(value: T): void {
    validateKeyframeValue(value);
    this.baseValue = cloneValue(value);
  }

  /**
   * Añade o reemplaza un keyframe en el timestamp indicado.
   * Mantiene el array de keyframes ordenado cronológicamente.
   */
  public addKeyframe(
    timeOrKeyframe: Time | Keyframe<T>,
    value?: T,
    easing?: EasingName,
    options?: {
      spatialIn?: SpatialTangent;
      spatialOut?: SpatialTangent;
      spatialInterpolation?: SpatialInterpolationType;
    }
  ): void {
    let newKeyframe: Keyframe<T>;

    if (typeof timeOrKeyframe === "object" && timeOrKeyframe !== null && "time" in timeOrKeyframe) {
      const validTime = validateTime(timeOrKeyframe.time);
      validateKeyframeValue(timeOrKeyframe.value);
      newKeyframe = {
        time: validTime,
        value: cloneValue(timeOrKeyframe.value),
        easing: timeOrKeyframe.easing,
        spatialIn: timeOrKeyframe.spatialIn ? cloneValue(timeOrKeyframe.spatialIn) : undefined,
        spatialOut: timeOrKeyframe.spatialOut ? cloneValue(timeOrKeyframe.spatialOut) : undefined,
        spatialInterpolation: timeOrKeyframe.spatialInterpolation,
      };
    } else {
      const validTime = validateTime(timeOrKeyframe);
      validateKeyframeValue(value);
      newKeyframe = {
        time: validTime,
        value: cloneValue(value as T),
        easing,
        spatialIn: options?.spatialIn ? cloneValue(options.spatialIn) : undefined,
        spatialOut: options?.spatialOut ? cloneValue(options.spatialOut) : undefined,
        spatialInterpolation: options?.spatialInterpolation,
      };
    }

    // Buscar si ya existe un keyframe en ese timestamp
    const existingIndex = this.keyframes.findIndex((k) => k.time === newKeyframe.time);
    if (existingIndex !== -1) {
      // Reemplazo del existente
      this.keyframes[existingIndex] = newKeyframe;
    } else {
      // Inserción ordenada
      const insertIndex = this.keyframes.findIndex((k) => k.time > newKeyframe.time);
      if (insertIndex === -1) {
        this.keyframes.push(newKeyframe);
      } else {
        this.keyframes.splice(insertIndex, 0, newKeyframe);
      }
    }
  }

  /**
   * Elimina el keyframe en el timestamp indicado si existe.
   * Retorna true si fue eliminado, false si no se encontró.
   */
  public removeKeyframe(time: Time): boolean {
    const validTime = validateTime(time);
    const index = this.keyframes.findIndex((k) => k.time === validTime);
    if (index !== -1) {
      this.keyframes.splice(index, 1);
      return true;
    }
    return false;
  }

  /**
   * Elimina todos los keyframes registrados.
   */
  public clearKeyframes(): void {
    this.keyframes = [];
  }

  /**
   * Retorna una copia profunda e inmutable de los keyframes ordenados.
   */
  public getKeyframes(): Keyframe<T>[] {
    return this.keyframes.map((k) => ({
      time: k.time,
      value: cloneValue(k.value),
      ...(k.easing ? { easing: k.easing } : {}),
      ...(k.spatialIn ? { spatialIn: cloneValue(k.spatialIn) } : {}),
      ...(k.spatialOut ? { spatialOut: cloneValue(k.spatialOut) } : {}),
      ...(k.spatialInterpolation ? { spatialInterpolation: k.spatialInterpolation } : {}),
    }));
  }

  /**
   * Evalúa la propiedad en el instante `time` de forma pura y determinista.
   */
  public evaluate(time: Time): T {
    const validTime = validateTime(time);

    // 1. Sin animación: devolver valor base
    if (this.keyframes.length === 0) {
      return cloneValue(this.baseValue);
    }

    // 2. Un único keyframe: hold constante
    if (this.keyframes.length === 1) {
      return cloneValue(this.keyframes[0].value);
    }

    // 3. Antes del primer keyframe: hold del primer valor
    if (validTime <= this.keyframes[0].time) {
      return cloneValue(this.keyframes[0].value);
    }

    // 4. Después del último keyframe: hold del último valor
    const lastIndex = this.keyframes.length - 1;
    if (validTime >= this.keyframes[lastIndex].time) {
      return cloneValue(this.keyframes[lastIndex].value);
    }

    // 5. Búsqueda binaria del segmento [previous, next]
    let low = 0;
    let high = lastIndex;
    let prevIndex = 0;

    while (low <= high) {
      const mid = Math.floor((low + high) / 2);
      if (this.keyframes[mid].time <= validTime) {
        prevIndex = mid;
        low = mid + 1;
      } else {
        high = mid - 1;
      }
    }

    const prevKeyframe = this.keyframes[prevIndex];
    const nextKeyframe = this.keyframes[prevIndex + 1];

    // Si coincide exactamente con el timestamp del keyframe previo
    if (validTime === prevKeyframe.time) {
      return cloneValue(prevKeyframe.value);
    }

    // 6. Cálculo de progreso en el segmento
    const segmentDuration = nextKeyframe.time - prevKeyframe.time;
    if (segmentDuration <= 0) {
      return cloneValue(prevKeyframe.value);
    }

    const rawProgress = (validTime - prevKeyframe.time) / segmentDuration;

    // 7. Aplicar la función de easing del keyframe inicial del segmento
    const easingFn = getEasing(prevKeyframe.easing);
    const easedProgress = easingFn(rawProgress);

    // 8. Interpolar y retornar
    return interpolate(prevKeyframe.value, nextKeyframe.value, easedProgress);
  }
}
