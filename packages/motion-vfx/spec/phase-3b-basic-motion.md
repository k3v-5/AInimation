# Especificación Técnica: Fase 3B — Basic Motion Primitives

**Documento:** `spec/phase-3b-basic-motion.md`  
**Estado:** VIGENTE / CONGELADO  
**Módulos:** `src/animation/primitives/`

---

## 0. Propósito y Alcance

La **Fase 3B** construye las primitivas fundamentales de movimiento (`fadeIn`, `fadeOut`, `slideIn`, `slideOut`, `scaleIn`, `scaleOut`, `rotateIn`, `rotateOut`) sobre la arquitectura `AnimationNode` de Fase 3A.

```
                  AnimationNode (Fase 3A)
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          FadeIn/Out    SlideIn/Out   ScaleIn/Out
                            │
                        RotateIn/Out
```

---

## 1. Reglas e Invariantes Arquitectónicos

1. **Constructores de Animaciones Puras (No Renderers ni Mutaciones Inmediatas):**
   Llamar a `slideIn(element)` o `fadeIn(element)` **NO muta** de forma destructiva las propiedades del elemento; construye y retorna una instancia de `BasicAnimation` configurada con el destino `{ elementId: element.id, propertyPath }`.
2. **Relatividad al Estado Base del Elemento:**
   - Si el elemento tiene `position = (500, 500)` y se aplica `slideIn(element, { direction: "left", distance: 200 })`, la animación calcula:
     $$\text{from} = (300, 500), \quad \text{to} = (500, 500)$$
3. **Centralización de Defaults:**
   Todos los valores por defecto residen en un único módulo (`defaults.ts`).
4. **Componibilidad Directa en Árboles:**
   Cualquier primitiva puede combinarse inmediatamente con `parallel(...)` y `sequence(...)`.
5. **Reversibilidad y Reutilización:**
   `fadeIn`/`fadeOut`, `slideIn`/`slideOut`, etc., comparten la función constructora genérica `animateProperty<T>()`.

---

## 2. Definición Formal de Fórmulas de Desplazamiento (Slide)

Dado $P_{\text{base}} = (x_0, y_0)$ y distancia $d \ge 0$:

| Primitiva | Dirección | $P_{\text{from}}$ | $P_{\text{to}}$ |
|---|---|---|---|
| `slideIn` | `"left"` | $(x_0 - d, y_0)$ | $(x_0, y_0)$ |
| `slideIn` | `"right"` | $(x_0 + d, y_0)$ | $(x_0, y_0)$ |
| `slideIn` | `"up"` | $(x_0, y_0 - d)$ | $(x_0, y_0)$ |
| `slideIn` | `"down"` | $(x_0, y_0 + d)$ | $(x_0, y_0)$ |
| `slideOut` | `"left"` | $(x_0, y_0)$ | $(x_0 - d, y_0)$ |
| `slideOut` | `"right"` | $(x_0, y_0)$ | $(x_0 + d, y_0)$ |
| `slideOut` | `"up"` | $(x_0, y_0)$ | $(x_0, y_0 - d)$ |
| `slideOut` | `"down"` | $(x_0, y_0)$ | $(x_0, y_0 + d)$ |

---

## 3. Tipos e Interfaces

```typescript
export type SlideDirection = "left" | "right" | "up" | "down";

export interface MotionOptions {
  duration?: number;
  delay?: number;
  easing?: EasingName;
  priority?: number;
}

export interface SlideOptions extends MotionOptions {
  direction?: SlideDirection;
  distance?: number;
}

export interface ScaleOptions extends MotionOptions {
  from?: Vector2 | number;
  to?: Vector2 | number;
}

export interface RotateOptions extends MotionOptions {
  from?: number;
  to?: number;
}
```
