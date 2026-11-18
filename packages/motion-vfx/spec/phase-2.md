# Especificación Técnica: Fase 2 — Element Model

**Documento:** `spec/phase-2.md`  
**Estado:** VIGENTE / CONGELADO  
**Versión de Esquema:** `0.2.0`

---

## 1. Objetivo de la Fase

Construir la capa de modelado y descripción semántica de contenido audiovisual (`Text`, `Image`, `Video`, `Shape`, `Audio`, `Group`) sobre el Core Temporal de la Fase 1.

```
                 CORE (Fase 1)
                      │
        ┌─────────────┴─────────────┐
        │                           │
     Timeline                   Properties
        │                           │
        └─────────────┬─────────────┘
                      │
                      ▼
             ELEMENT MODEL (Fase 2)
                      │
       ┌──────────────┼──────────────┐
       │              │              │
      Text          Image          Video
       │              │              │
       ├──────────────┼──────────────┤
       │              │              │
     Shape          Audio          Group
```

---

## 2. Límites de Alcance Estrictos

Esta fase **NO debe producir ni contener**:
- ❌ Renderizado de píxeles (Canvas, WebGL, Skia, FFmpeg)
- ❌ Decodificación de audio o video (codecs, WebAudio, buffers de audio)
- ❌ Carga física de archivos del disco o red (las imágenes y videos se manejan como `AssetReference` abstractas)
- ❌ Carga ni rasterización de fuentes tipográficas
- ❌ Shaders, sombras, blur, glow ni efectos de post-procesado
- ❌ Máscaras, track mattes ni modos de fusión avanzados (blending)
- ❌ Servidor MCP, paneles UI ni integración con After Effects / Blender
- ❌ Expresiones de scripting ni IA generativa

El motor calcula **únicamente el estado lógico, espacial y temporal** de cada elemento.

---

## 3. Principios y Reglas Arquitectónicas

### Regla 1 — Evaluación Pura sin Efectos Secundarios
`element.evaluate(time)` calcula y devuelve el estado formal del elemento en ese instante. **Nunca** abre archivos, decodifica imágenes, dibuja en un canvas ni llama a APIs del sistema operativo.

### Regla 2 — Jerarquía Unificada de Elementos
Toda entidad visual o de audio hereda de `BaseElement`:
```
BaseElement (id, name, startTime, endTime, enabled)
├── VisualElement (transform: Transform)
│   ├── TextElement
│   ├── ImageElement
│   ├── VideoElement
│   ├── ShapeElement
│   └── GroupElement (children: BaseElement[])
└── AudioElement (source: AssetReference, volume, playbackRate)
```

### Regla 3 — Sistema de Transformaciones y Anchor Point Normalizado
Todo `VisualElement` posee un `Transform`:
- `position`: `Property<Vector2>` (en píxeles de la composición)
- `scale`: `Property<Vector2>` (multiplicativa, base 1.0 = 100%)
- `rotation`: `Property<number>` (en **grados**, clockwise)
- `opacity`: `Property<number>` (normalizada en $[0, 1]$)
- `anchorPoint`: `Property<Vector2>` (normalizado $[0, 1]$, donde $(0.5, 0.5)$ es el centro del elemento)

### Regla 4 — Jerarquía Espacial (Local-to-World Transform)
Un `GroupElement` propaga su matriz afín $3 \times 3$ y su opacidad acumulada a sus hijos:
$$M_{\text{world}} = M_{\text{parent\_world}} \times M_{\text{local}}$$
$$\text{Opacity}_{\text{world}} = \text{Opacity}_{\text{parent\_world}} \times \text{Opacity}_{\text{local}}$$

### Regla 5 — Desacoplamiento de Recursos (`AssetRegistry`)
Los elementos de medios (`ImageElement`, `VideoElement`, `AudioElement`) referencian activos mediante identificadores en un `AssetRegistry`:
```typescript
interface AssetReference {
  id: string;
  type: "image" | "video" | "audio";
  path?: string;
  metadata?: Record<string, unknown>;
}
```

### Regla 6 — Mapeo Temporal de Video (`Source Time` vs `Composition Time`)
Para un `VideoElement` con `startTime`, `sourceStartTime`, `playbackRate` y `loop`:
$$t_{\text{elapsed}} = (t_{\text{comp}} - \text{startTime}) \times \text{playbackRate}$$
$$t_{\text{source}} = \text{sourceStartTime} + t_{\text{elapsed}}$$
Si `loop === true` y existe `sourceDuration`:
$$t_{\text{source}} = \text{sourceStartTime} + (t_{\text{elapsed}} \pmod{\text{sourceDuration}})$$

---

## 4. Criterios de Aceptación

1. **Subfase 2A:** Módulo de matrices 2D, clase `Transform` y `AssetRegistry` implementados y probados.
2. **Subfase 2B:** Clases `BaseElement`, `VisualElement`, `TextElement`, `ImageElement`, `VideoElement`, `AudioElement`, `ShapeElement` y `GroupElement` operativas con soporte de `Property<T>`.
3. **Subfase 2C:** `ElementFactory.fromJSON()`, esquema de serialización `v0.2.0` y retrocompatibilidad con proyectos `v0.1.0`.
4. **Verificación:** Cobertura exhaustiva de tests unitarios, tests de jerarquía matricial 2D, tests de video timeline y 0 regresiones en las suites de Fase 1 y 1.5.
