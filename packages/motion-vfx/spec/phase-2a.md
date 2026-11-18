# Especificación Técnica: Fase 2A — Transform System + Asset System

**Documento:** `spec/phase-2a.md`  
**Estado:** VIGENTE / CONGELADO  
**Versión de Arquitectura:** `0.2.0-2A`

---

## 0. Propósito y Alcance de Fase 2A

La **Fase 2A** construye la infraestructura matemática, espacial y de recursos audiovisuales que servirá de cimiento para el Modelo de Elementos (Fase 2B) y las Primitivas de Animación (Fase 3).

```
                    FASE 2A
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
   TRANSFORM SYSTEM           ASSET SYSTEM
          │                         │
 position / scale /           image / video /
 rotation / opacity           audio references
 anchor / hierarchy           metadata / registry
          │                         │
          └────────────┬────────────┘
                       ▼
             Element Model (Fase 2B)
```

---

## 1. Reglas Arquitectónicas Obligatorias

1. **Regla 1 — El Core no renderiza:** Cero dependencias de Canvas, WebGL, WebGPU, Skia o FFmpeg.
2. **Regla 2 — El Core no carga archivos:** Un asset es una referencia abstracta y metadatos estructurados, nunca un buffer ni archivo físico en memoria.
3. **Regla 3 — Transform independiente del renderer:** El sistema calcula matrices afines $3 \times 3$ puras y opacidades que cualquier renderer posterior consumirá.
4. **Regla 4 — Los transforms son evaluables en el tiempo:** Todas las propiedades espaciales y de opacidad son `Property<T>` con soporte completo de keyframes y easings deterministas.
5. **Regla 5 — `evaluate()` es una función pura:** No muta el estado interno ni expone referencias mutables.
6. **Regla 6 — Detección estricta de ciclos:** La jerarquía espacial prohíbe ciclos de emparentamiento ($A \to B \to A$) mediante validación de grafos acíclicos directos.

---

## 2. Sistema de Coordenadas y Convención Matemática

### 2.1. Coordenadas 2D
- **Origen:** $(0, 0)$ en la esquina superior izquierda (top-left).
- **Ejes:** $+X$ hacia la derecha, $+Y$ hacia abajo.

### 2.2. Propiedades de Transform
- `position`: `Property<Vector2>` (en píxeles, default $(0, 0)$).
- `scale`: `Property<Vector2>` (multiplicativa, default $(1, 1)$).
- `rotation`: `Property<number>` (grados sexagesimales $\theta^\circ$, sentido horario, default $0$).
- `opacity`: `Property<number>` (escalar $[0.0, 1.0]$, default $1$).
- `anchorPoint`: `Property<Vector2>` (normalizado $[0.0, 1.0]$, default $(0.5, 0.5)$).

### 2.3. Fórmula de Composición Matricial (Local Matrix)
Dado un elemento con dimensiones de caja $\text{bounds} = (w, h)$ y punto de anclaje normalizado $(a_x, a_y)$:
$$\text{offset}_{\text{anchor}} = (a_x \cdot w, a_y \cdot h)$$
$$M_{\text{local}} = T(\text{position}) \cdot T(\text{offset}_{\text{anchor}}) \cdot R(\text{rotation}) \cdot S(\text{scale}) \cdot T(-\text{offset}_{\text{anchor}})$$

---

## 3. Jerarquía y Resolución Espacial (`TransformResolver`)

Para cualquier nodo dentro de un árbol de emparentamiento:
$$M_{\text{world}} = M_{\text{parent\_world}} \times M_{\text{local}}$$
$$\text{Opacity}_{\text{world}} = \text{Opacity}_{\text{parent\_world}} \times \text{Opacity}_{\text{local}}$$

---

## 4. Sistema de Recursos (`AssetSystem`)

### 4.1. Estructura de `Asset`
```typescript
interface Asset {
  id: string;
  type: "image" | "video" | "audio";
  source: {
    path: string;
    [key: string]: unknown;
  };
  metadata?: ImageMetadata | VideoMetadata | AudioMetadata;
}
```

### 4.2. Catálogo `AssetRegistry`
- `add(asset: Asset): void` (Rechaza IDs duplicados o datos incompletos).
- `get(id: string): Asset | undefined`
- `require(id: string): Asset` (Lanza error si el ID no existe).
- `has(id: string): boolean`
- `remove(id: string): boolean`
- `list(): Asset[]`
- `clear(): void`
