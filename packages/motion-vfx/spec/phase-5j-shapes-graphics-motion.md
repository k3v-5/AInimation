# Especificación Técnica: Fase 5J — Shapes, Graphics & Procedural Motion

**Documento:** `spec/phase-5j-shapes-graphics-motion.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulo:** `src/graphics/`

---

## 0. Propósito y Separación Arquitectónica

La **Fase 5J** introduce el sistema de gráficos vectoriales 2D, componentes visuales semánticos y movimiento procedural para el motor de motion graphics y edición:

```
                  GRAPHIC DEFINITION (Semantic Component)
                                  │
       ┌──────────────────────────┼──────────────────────────┐
       ↓                          ↓                          ↓
    GEOMETRY                    STYLE                      LAYOUT
(Rect, Arrow, Ellipse)    (Fill, Stroke, Dash)     (Anchor, Stack, Safe Area)
       │                          │                          │
       └──────────────────────────┼──────────────────────────┘
                                  ↓
                          PROCEDURAL MOTION
                   (Trim Paths, Springs, Noise)
                                  ↓
                        LAYER & RENDER GRAPH
```

---

## 1. Geometrías y Modificadores de Trazo (`Geometry`, `Stroke`, `TrimPaths`)

### 1.1. Geometrías
- **`RectangleGeometry`:** `width`, `height`.
- **`RoundedRectangleGeometry`:** `width`, `height`, `radius` (con sujeción $r \le \min(w, h)/2$).
- **`EllipseGeometry`:** `rx`, `ry` o `width`, `height`.
- **`LineGeometry`:** `start: Vec2`, `end: Vec2`.
- **`ArrowGeometry`:** `start: Vec2`, `end: Vec2`, `headLength`, `headWidth`, `shaftWidth`.
- **`PolygonGeometry` & `PathGeometry`:** Polígonos y trazados Bézier continuos.

### 1.2. Modificadores de Trazo y Animación
- **`Stroke`:** `color`, `width`, `opacity`, `join` (`miter`, `round`, `bevel`), `cap` (`butt`, `round`, `square`), `dash` (`segments`, `offset`).
- **`TrimPaths`:** Recorte paramétrico de curvas $[start, end, offset]$ en el rango normalizado $[0, 1]$.

---

## 2. Sistema de Diseño y Disposición (`LayoutEngine`, `AnchorLayout`)

1. **Posicionamiento por Anclajes (`AnchorPosition`):**
   - 9 anclajes canónicos: `top-left`, `top-center`, `top-right`, `center-left`, `center`, `center-right`, `bottom-left`, `bottom-center`, `bottom-right`.
2. **Disposición en Pila (`StackLayout`):**
   - Direcciones `horizontal` y `vertical`, con espacio entre elementos (`gap`) y alineación (`start`, `center`, `end`).
3. **Zonas Seguras (*Safe Areas*):**
   - Márgenes de seguridad para interfaces móviles y plataformas 9:16 (TikTok, Instagram Reels, YouTube Shorts).

---

## 3. Componentes Gráficos Semánticos y Presets (`GraphicComponents`, `GraphicPresetRegistry`)

1. **Componentes:**
   - `Card`: Tarjeta con fondo redondeado, título, subtítulo e icono opcional.
   - `Callout`: Bocadillo de texto explicativo con flecha orientada hacia un sujeto o coordenadas.
   - `Badge`: Insignia o píldora de notificación / alerta.
   - `ProgressBar`: Barra de progreso con valor continuo $[min, max]$.
   - `Counter`: Contador numérico con formateo inteligente (`1K`, `1.2M`, `$1,000`, `85%`).
   - `Chart`: Gráficos sencillos de barras, líneas y sectores circulares.
2. **Presets Semánticos:** `youtube-callout`, `highlight-circle`, `modern-card`, `warning-badge`, `progress-bar`, `social-counter`.
