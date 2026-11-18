# Especificación Técnica: Fase 4C — Effects & Visual Modifiers

**Documento:** `spec/phase-4c-effects-modifiers.md`  
**Estado:** VIGENTE / CONGELADO  
**Módulos:** `src/effects/`

---

## 0. Propósito y Principio Arquitectónico

La **Fase 4C** introduce el sistema de modificadores visuales y efectos que dotan al motor del acabado estético ("look pro" / "cinematic"):

### Invariante Fundamental: Efecto $\neq$ Animación
Un efecto es un **Modificador de Renderizado** que reside en la pila de efectos del elemento (`EffectStack`). Cada efecto expone parámetros basados en `Property<T>`, lo que permite que el `AnimationEngine` los anime de forma completamente desacoplada e interoperable:

```
Element ("HeroTitle")
   │
   ├── Transform (position, scale, rotation, opacity)
   │
   └── EffectStack
        ├── GaussianBlur (radius: Property<number>) ────────┐
        └── Glow (intensity: Property<number>, color: Color) ──┴──> Modificadores evaluados
```

---

## 1. Catálogo de Efectos Estándar

### 1.1. Blur & Enfoque
- **`GaussianBlur`**: `radius: Property<number>` (desenfoque gaussiano isotrópico).
- **`DirectionalBlur`**: `length: Property<number>`, `angle: Property<number>`.
- **`MotionBlur`**: `samples: number`, `shutterAngle: number` (calculado a partir del vector velocidad transform).

### 1.2. Glow & Sombra
- **`DropShadow`**: `offset: Property<Vector2>`, `blur: Property<number>`, `color: Color`, `opacity: Property<number>`.
- **`Glow`**: `radius: Property<number>`, `intensity: Property<number>`, `color: Color`, `threshold: Property<number>`.

### 1.3. Ajustes de Color (Color Grading)
- **`ColorAdjustments`**: `brightness: Property<number>`, `contrast: Property<number>`, `saturation: Property<number>`, `hue: Property<number>`, `tint: Color`.

### 1.4. Estilización y Distorsión
- **`ChromaticAberration`**: `offset: Property<number>`, `angle: Property<number>`.
- **`Vignette`**: `amount: Property<number>`, `radius: Property<number>`, `softness: Property<number>`.
- **`NoiseGrain`**: `amount: Property<number>`, `monochrome: boolean`, `seed: number`.

---

## 2. Direccionamiento Canónico de Propiedades de Efectos

El sistema de targets de animación puede direccionar propiedades de efectos usando la convención estándar:
`${elementId}:effect:${effectId}.${propertyName}`

Por ejemplo:
- `title:effect:blur.radius`
- `logo:effect:glow.intensity`
- `background:effect:vignette.amount`

---

## 3. Serialización y Evaluación

Cada efecto implementa `evaluate(time)` retornando un descriptor inmutable de estado (`EvaluatedEffect`), listo para el pipeline de renderizado y exportación a After Effects JSX / shaders.
