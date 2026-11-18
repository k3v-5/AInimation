# Especificación Técnica: Fase 5C — Scenes & Transitions

**Documento:** `spec/phase-5c-scenes-transitions.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulos:** `src/scenes/`, `src/transitions/`

---

## 0. Propósito y Principios Arquitectónicos

La **Fase 5C** formaliza el modelo de escenas compositivas y el motor de transiciones cinemáticas:

### Invariantes Fundamentales

1. **Scene $\neq$ Timeline:**
   - Una **`Scene`** es una unidad compositiva temporal modular (`Composition`) que posee duración, roles semánticos (`hook`, `intro`, `explanation`, `cta`) y marcadores internos.
   - La **`Timeline`** orquesta la secuencia global de escenas y sus regiones de solapamiento.

2. **Transición = Composición Temporal entre Dos RenderTargets:**
   - Una transición **no es un efecto especial aislado**, sino un modificador compositivo que toma dos estados evaluados (`RenderTarget A` de la escena saliente y `RenderTarget B` de la escena entrante) y calcula el estado resultante en una ventana temporal $[t_{\text{start}}, t_{\text{end}})$ con progreso $\tau \in [0, 1]$ modulado por una función de easing.
   - Las transiciones combinan de forma limpia `Opacity`, `Transform` (Scale, Translation), `Blur` y capas de color.

3. **Precomposiciones (`CompositionElement`):**
   - Permite anidar una composición/escena entera como un elemento dentro de otra composición, aplicando transformaciones, animaciones y pilas de efectos a nivel global de precomp.

---

## 1. Modelo de Escenas y Roles Semánticos

### 1.1. Metadatos y Roles Semánticos (`SemanticSceneRole`)
```typescript
type SemanticSceneRole =
  | "hook"
  | "intro"
  | "explanation"
  | "example"
  | "reaction"
  | "cta"
  | "outro"
  | "custom";
```

### 1.2. `Scene`
- `id`: Identificador único.
- `duration`: Duración local de la escena.
- `composition`: Instancia de `Composition` con sus elementos, capas y dimensiones.
- `metadata`: `{ name?: string; tags?: string[]; semanticRole?: SemanticSceneRole }`.
- `markers`: Marcadores temporales internos.

---

## 2. Catálogo de Transiciones y Registro (`TransitionRegistry`)

Cada transición implementa `TransitionDefinition`:
- `id`: Identificador (ej. `"crossfade"`, `"zoom"`, `"whip"`).
- `parameters`: Esquema de parámetros validados (`min`, `max`, `default`, `type`).
- `evaluate(context)`: Calcula el estado de mezcla en el progreso $\tau \in [0, 1]$.

### Catálogo Estándar Builtin
1. **`Cut`**: Corte instantáneo ($\tau < 1 \to A, \tau = 1 \to B$).
2. **`Crossfade` / `Fade`**: Interpolación lineal o eased de opacidades ($A: 1 \to 0$, $B: 0 \to 1$).
3. **`DipToColor`**: Fase 1 ($A \to \text{Color}$), Fase 2 ($\text{Color} \to B$).
4. **`Zoom`**: Escala dinámica de salida en $A$ ($1.0 \to 1.0 + \text{amount}$) y de entrada en $B$ ($1.0 - \text{amount} \to 1.0$) con pico de desenfoque intermedio.
5. **`Slide`**: Desplazamiento cartesiano en $X$ o $Y$ según dirección (`left`, `right`, `up`, `down`).
6. **`Whip` / `WhipPan`**: Desplazamiento rápido con desenfoque de movimiento angular direccional.
7. **`Blur`**: Descenso de nitidez en $A$ ($0 \to \text{blurMax}$) y recuperación en $B$ ($\text{blurMax} \to 0$).
8. **`Flash`**: Capa aditiva de destello blanco peaking en $\tau = 0.5$.

---

## 3. Pipeline de Renderizado y Evaluación de Transiciones

$$\tau = \text{getEasing}(\text{easing})\left(\frac{t_{\text{global}} - t_{\text{transStart}}}{t_{\text{transDuration}}}\right)$$

```
Scene A (Evaluate at t_localA) ──► Target A ──┐
                                             ├──► Transition(Target A, Target B, tau) ──► Final Output
Scene B (Evaluate at t_localB) ──► Target B ──┘
```
