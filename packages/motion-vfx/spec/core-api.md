# Especificación de API: Fase 1 — Core API Reference

**Documento:** `spec/core-api.md`  
**Estado:** VIGENTE / CONGELADO  
**Versión:** `0.1.0`

---

## 1. Tipos Fundamentales (`src/core/types.ts`)

```typescript
/** Tiempo continuo en segundos (>= 0). No NaN, no Infinity. */
export type Time = number;

/** Vector matemático bidimensional */
export interface Vector2 {
  x: number;
  y: number;
}

/** Vector matemático tridimensional */
export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

/** Color normalizado en rango 0.0 a 1.0 */
export interface Color {
  r: number;
  g: number;
  b: number;
  a: number;
}

/** Nombres de funciones de Easing estándar de Fase 1 */
export type EasingName = "linear" | "easeIn" | "easeOut" | "easeInOut";

/** Firma de función de Easing pura */
export type EasingFunction = (progress: number) => number;

/** Tangentes espaciales para curvas de movimiento 2D/3D */
export interface SpatialTangent2D {
  x: number;
  y: number;
}
export interface SpatialTangent3D {
  x: number;
  y: number;
  z: number;
}
export type SpatialTangent = SpatialTangent2D | SpatialTangent3D;
export type SpatialInterpolationType = "linear" | "bezier" | "hold";
```

---

## 2. Keyframe (`src/core/keyframe.ts`)

```typescript
export interface Keyframe<T> {
  readonly time: Time;
  readonly value: T;
  readonly easing?: EasingName;
  readonly spatialIn?: SpatialTangent;
  readonly spatialOut?: SpatialTangent;
  readonly spatialInterpolation?: SpatialInterpolationType;
}
```

- **Invariante:** `time >= 0`. `value` no puede ser `null` ni `undefined`.
- **Segmentación:** El `easing` especificado en $K_i$ gobierna la transición hacia $K_{i+1}$. Si se omite, se asume `"linear"`.
- **Extensibilidad Espacial:** Campos opcionales para almacenar tangentes de Bezier espacial sin afectar el cálculo temporal de Fase 1.

---

## 3. Animación e Interpolación (`src/animation/`)

### 3.1. Easing (`src/animation/easing.ts`)

Funciones cúbicas puras:
- **`linear(t)`**: $t$
- **`easeIn(t)`**: $t^3$
- **`easeOut(t)`**: $1 - (1 - t)^3$
- **`easeInOut(t)`**:
  $$\text{easeInOut}(t) = \begin{cases} 4t^3 & \text{si } t < 0.5 \\ 1 - \frac{(-2t + 2)^3}{2} & \text{si } t \ge 0.5 \end{cases}$$

Función auxiliar:
```typescript
export function getEasing(name?: EasingName): EasingFunction;
```

### 3.2. Interpolation (`src/animation/interpolation.ts`)

```typescript
export function clamp01(value: number): number;

export function interpolate<T>(from: T, to: T, progress: number): T;
```

- Aplica `progress = clamp01(progress)`.
- Soporta:
  - `number`: $\text{from} + (\text{to} - \text{from}) \cdot \text{progress}$
  - `Vector2`: $\{ x: \text{interp}(x), y: \text{interp}(y) \}$
  - `Vector3`: $\{ x: \text{interp}(x), y: \text{interp}(y), z: \text{interp}(z) \}$
- Lanza `ValidationError` si `from` y `to` no son de tipos compatibles o soportados.

---

## 4. Property<T> (`src/core/property.ts`)

```typescript
export class Property<T> {
  constructor(initialValue: T);

  /** Obtiene una copia del valor base estático */
  getValue(): T;

  /** Modifica el valor base estático */
  setValue(value: T): void;

  /** 
   * Añade un keyframe. Si ya existe un keyframe en `time`, lo reemplaza.
   * Mantiene la lista de keyframes ordenada ascendentemente por tiempo.
   */
  addKeyframe(time: Time, value: T, easing?: EasingName): void;

  /** Elimina el keyframe en el timestamp indicado */
  removeKeyframe(time: Time): boolean;

  /** Elimina todos los keyframes */
  clearKeyframes(): void;

  /** Obtiene una copia inmutable del array de keyframes ordenados */
  getKeyframes(): Keyframe<T>[];

  /** Evalúa el valor de la propiedad en el instante `time` */
  evaluate(time: Time): T;
}
```

### Lógica de `evaluate(time: Time)`:
1. Validar `time >= 0`.
2. Si `keyframes.length === 0`: devolver copia de `baseValue`.
3. Si `keyframes.length === 1`: devolver copia de `keyframes[0].value`.
4. Si `time <= keyframes[0].time`: devolver copia de `keyframes[0].value` (hold inicial).
5. Si `time >= keyframes[last].time`: devolver copia de `keyframes[last].value` (hold final).
6. Localizar $K_i, K_{i+1}$ tal que $K_i.\text{time} \le \text{time} < K_{i+1}.\text{time}$.
7. $\text{rawProgress} = \frac{\text{time} - K_i.\text{time}}{K_{i+1}.\text{time} - K_i.\text{time}}$.
8. $\text{easedProgress} = \text{getEasing}(K_i.\text{easing})(\text{rawProgress})$.
9. Devolver $\text{interpolate}(K_i.\text{value}, K_{i+1}.\text{value}, \text{easedProgress})$.

---

## 5. Layer (`src/core/layer.ts`)

```typescript
export interface LayerOptions {
  id: string;
  name?: string;
  startTime?: Time;
  endTime?: Time;
}

export interface LayerSnapshot {
  id: string;
  name: string;
  active: boolean;
  properties?: Record<string, unknown>;
}

export class Layer {
  readonly id: string;
  name: string;
  startTime: Time;
  endTime: Time;

  constructor(options: LayerOptions);

  /** Obtiene o registra una propiedad en el Layer */
  property(name: string): Property<unknown>;
  property<T>(name: string, initialValue?: T): Property<T>;

  /** Comprueba si el layer está activo en el tiempo indicado: startTime <= time < endTime */
  isActive(time: Time): boolean;

  /** Evalúa el estado del layer en `time` y retorna un snapshot inmutable */
  evaluate(time: Time): LayerSnapshot;
}
```

### Propiedades por defecto de un Layer:
- `"position"`: `Property<Vector2>({ x: 0, y: 0 })`
- `"scale"`: `Property<Vector2>({ x: 1, y: 1 })`
- `"rotation"`: `Property<number>(0)`
- `"opacity"`: `Property<number>(1)`

---

## 6. Composition (`src/core/composition.ts`)

```typescript
export interface CompositionOptions {
  id?: string;
  name?: string;
  width: number;
  height: number;
  fps: number;
  duration: Time;
}

export interface CompositionSnapshot {
  time: Time;
  duration: Time;
  width: number;
  height: number;
  fps: number;
  layers: LayerSnapshot[];
}

export class Composition {
  readonly id: string;
  name: string;
  readonly width: number;
  readonly height: number;
  readonly fps: number;
  readonly duration: Time;

  constructor(options: CompositionOptions);

  addLayer(layer: Layer): void;
  removeLayer(id: string): boolean;
  getLayer(id: string): Layer | undefined;
  getLayers(): Layer[];
  moveLayer(id: string, newIndex: number): void;

  /** Evalúa la composición completa en `time` y retorna un snapshot inmutable */
  evaluate(time: Time): CompositionSnapshot;
}
```

---

## 7. Timeline (`src/core/timeline.ts`)

```typescript
export class Timeline {
  readonly fps: number;
  readonly duration: Time;

  constructor(fps: number, duration: Time);

  frameToTime(frame: number): Time;
  timeToFrame(time: Time): number;
  totalFrames(): number;
}
```

---

## 8. Jerarquía de Errores (`src/errors/`)

- `MotionEngineError`: Error base de todo el motor.
- `ValidationError`: Fallo de validación en datos, dimensiones, o tipos.
- `InvalidTimeError`: Timestamp inválido (`NaN`, negativo o infinito).
- `InvalidKeyframeError`: Keyframe malformado o valor incompatible.
- `DuplicateLayerError`: Intento de registrar dos capas con el mismo `id`.
- `LayerNotFoundError`: Búsqueda de una capa inexistente.
- `SerializationError`: Error de schema o formato durante JSON parse/serialize.
