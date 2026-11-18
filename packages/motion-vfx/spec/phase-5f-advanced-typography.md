# Especificación Técnica: Fase 5F — Advanced Text & Typography

**Documento:** `spec/phase-5f-advanced-typography.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulos:** `src/typography/`

---

## 0. Propósito y Separación Arquitectónica

La **Fase 5F** construye el motor tipográfico vectorial avanzado y kinetic typography:

```
Transcript / User Text
        ↓
   TextDocument & Spans (Rich Text)
        ↓
   FontRegistry & FallbackResolver
        ↓
   TextShaper (Unicode Graphemes, Ligatures & Clusters)
        ↓
   TextLayoutEngine (Wrapping, Baselines, Layout/Visual Bounds)
        ↓
   PaintStack (Gradient Fill, Multi-layer Stroke, Background, Shadow)
        ↓
   GlyphTransform & Stagger (Kinetic per-glyph motion)
        ↓
   Renderer / Composition
```

---

## 1. Modelo de Datos y Estructuras

### 1.1. `TextDocument` & `TextSpan` (Rich Text)
```typescript
interface TextSpan {
  start: number; // Índice de carácter inicial
  end: number;   // Índice de carácter final [start, end)
  style?: Partial<TextStyle>;
  paint?: Partial<TextPaint>;
}

interface TextDocument {
  id: string;
  content: string;
  defaultStyle: TextStyle;
  defaultPaint: TextPaint;
  spans: TextSpan[];
}
```

### 1.2. `FontRegistry`, `FontResource` & `FontFallback`
- **`FontMetrics`:** `{ ascent, descent, lineGap, unitsPerEm }`.
- **`FontResolver`:** Resuelve la fuente solicitada y, si no se encuentra en el registro, delega al `fallbackFont` ("Inter" / "Arial") haciendo matching por `fontWeight` más cercano.

### 1.3. `TextShaper` & `GlyphPosition`
- Transforma caracteres y secuencias Unicode (incluyendo emojis y marcas combinadas) en glifos posicionados con `advanceX`, `advanceY` y `cluster`.

### 1.4. `TextPaint` y `PaintStack`
- Soporte para relleno sólido, gradiente lineal / radial (`LinearGradient`, `RadialGradient`), trazo multi-capa (*outer stroke, inner stroke*), sombras proyectadas y cajas de fondo con `padding` y `cornerRadius`.

### 1.5. `GlyphTransform` y `StaggerFunction`
- Modificadores por glifo (`position`, `rotation`, `scale`, `opacity`) con modos de stagger deterministas (`forward`, `reverse`, `center`, `random` con semilla PRNG).

---

## 2. Invariantes de Medición y Límites Visuales

1. **`layoutBounds` $\neq$ `visualBounds`:**
   - **`layoutBounds`:** Rectángulo espacial de maquetación tipográfica (ancho y alto del texto).
   - **`visualBounds`:** Rectángulo que incluye el grosor de trazo exterior (`stroke.width`), desenfoque de sombra (`shadow.blur`) y paddings de fondo.
2. **Determinismo en Stagger Aleatorio:**
   - El modo `random` de stagger se calcula mediante un generador pseudo-aleatorio lineal congruente (LCG) parametrizado por `seed`.
