# Especificación Técnica: Fase 3A — Animation Architecture

**Documento:** `spec/phase-3a-animation-architecture.md`  
**Estado:** VIGENTE / CONGELADO  
**Módulos:** `src/animation/`

---

## 0. Propósito y Alcance

La **Fase 3A** construye el motor de animación modular y componible del Motion Graphics Engine.

Una animación es una abstracción pura de transformación temporal desacoplada del renderizado que produce valores evaluados para propiedades espaciales, temporales y visuales:

```
AnimationNode (Composite Pattern)
│
├── BasicAnimation<T>     (Unidad atómica: from -> to con easing y delay)
├── ParallelAnimation     (Ejecución concurrente: duration = max(delay_i + dur_i))
└── SequenceAnimation     (Ejecución secuencial: duration = sum(delay_i + dur_i))
```

---

## 1. Principios Arquitectónicos e Invariantes

1. **Desacoplamiento Absoluto del Renderizado:**
   Una animación produce `AnimationResult` (valores numéricos, vectores, colores), jamás dibuja píxeles ni interactúa con APIs gráficas.
2. **Cadena Temporal Estricta:**
   $$\text{Composition Time} \longrightarrow \text{Element Local Time} \longrightarrow \text{Animation Time} \longrightarrow \text{Progress } [0, 1] \longrightarrow \text{Easing} \longrightarrow \text{Valor Interpolado}$$
3. **Inmutabilidad y Pureza:**
   `animation.evaluate(time)` no muta las propiedades del elemento ni el árbol de animación; es una función pura e idempotente.
4. **Composición de Árboles (Composite Pattern):**
   Las animaciones pueden anidarse arbitrariamente (`Parallel` dentro de `Sequence`, `Sequence` dentro de `Parallel`).
5. **Direccionamiento Canónico de Propiedades (`AnimationTarget`):**
   Toda pista de animación referencia un destino estable `{ elementId: string, propertyPath: string }` serializable en JSON (ej. `title::transform.position`).
6. **Resolución de Conflictos y Prioridad:**
   Si múltiples nodos escriben al mismo destino en el mismo instante, la resolución respeta `priority` (mayor prioridad sobreescribe) o el orden de declaración.

---

## 2. Tipos e Interfaces Fundamentales

```typescript
export type AnimationLifecycleState = "before" | "active" | "after";

export interface AnimationTarget {
  elementId: string;
  propertyPath: string; // ej. "transform.position", "transform.opacity", "volume"
}

export interface AnimationTrack<T = unknown> {
  target: AnimationTarget;
  from: T;
  to: T;
  easing?: EasingName;
}

export interface AnimationResult {
  has(target: AnimationTarget): boolean;
  get<T = unknown>(target: AnimationTarget): T | undefined;
  getAll(): Map<string, unknown>;
}
```

---

## 3. Modelo de Nodos de Animación

### 3.1. `AnimationNode` (Base Abstracta)
- `id: string`
- `delay: number` ($\ge 0$)
- `duration: number` ($> 0$)
- `totalDuration: number` (calculado según el tipo de nodo)
- `priority: number` (default 0)
- `getState(time: number): AnimationLifecycleState`
- `evaluate(time: number): AnimationResult`

### 3.2. `BasicAnimation<T>`
- Ejecuta una o más `AnimationTrack<T>` entre `from` y `to`.
- Progreso normalizado:
  $$p_{\text{norm}} = \text{clamp01}\left(\frac{t - \text{delay}}{\text{duration}}\right)$$
  $$p_{\text{eased}} = \text{evaluateEasing}(\text{easing}, p_{\text{norm}})$$
  $$\text{value} = \text{interpolate}(from, to, p_{\text{eased}})$$

### 3.3. `ParallelAnimation`
- Ejecuta múltiples `AnimationNode` concurrentemente.
- $\text{duration} = \max_{i}(\text{node}_i.\text{delay} + \text{node}_i.\text{duration})$.
- Fusiona los `AnimationResult` de todos sus hijos.

### 3.4. `SequenceAnimation`
- Ejecuta múltiples `AnimationNode` uno tras otro.
- $\text{duration} = \sum_{i}(\text{node}_i.\text{delay} + \text{node}_i.\text{duration})$.
- Rutea $t$ al nodo activo y mantiene el estado final de los nodos anteriores (`after`).
