# Especificación Técnica: Fase 5G — Masks, Rotoscoping & Tracking

**Documento:** `spec/phase-5g-masks-tracking.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulos:** `src/masks/`, `src/tracking/`

---

## 0. Propósito y Separación Arquitectónica

La **Fase 5G** construye el sistema de máscaras vectoriales, mattes de recorte, rotoscopia animada, seguimiento de movimiento (*tracking*) y binding de propiedades a elementos gráficos:

```
Video / Layer
  ├── MaskStack (Rectangle, Ellipse, Bézier)
  │     └── MatteGenerator (SDF, Feather, Expansion, Boolean Ops)
  │           └── Alpha Matte / Track Matte / Masked Effect
  │
  └── Tracker (Motion Tracking Data)
        └── TrackingSmoothing (Moving-Average, Exponential)
              └── PropertyBinding (Vinculación a Texto, Stickers, Cámaras)
```

---

## 1. Modelo de Datos y Estructuras

### 1.1. Máscaras y Geometría Bézier (`Mask`, `MaskPath`)
```typescript
interface MaskPoint {
  position: { x: number; y: number };
  inTangent?: { x: number; y: number };
  outTangent?: { x: number; y: number };
}

interface MaskPath {
  closed: boolean;
  points: MaskPoint[];
}

interface Mask {
  id: string;
  type: "rectangle" | "ellipse" | "bezier";
  path: MaskPath;
  mode: "add" | "subtract" | "intersect" | "difference";
  feather: number;    // Radio de difuminado en px
  expansion: number;  // Expansión/contracción en px
  opacity: number;    // [0, 1]
  inverted?: boolean;
}
```

### 1.2. Generación de Mattes y Operaciones Booleanas (`Matte`)
- **`Matte`:** Estructura pura rasterizada de canal alfa (`width`, `height`, `alpha: Float32Array`).
- **SDF (Signed Distance Function):** Cálculo exacto de distancia al contorno de la máscara para aplicar `feather` continuo y `expansion`.
- **Modos de Fusión (`MaskMode`):**
  - `add`: $\alpha_{out} = \alpha_A + \alpha_B \cdot (1 - \alpha_A)$
  - `subtract`: $\alpha_{out} = \alpha_A \cdot (1 - \alpha_B)$
  - `intersect`: $\alpha_{out} = \alpha_A \cdot \alpha_B$
  - `difference`: $\alpha_{out} = |\alpha_A - \alpha_B|$

### 1.3. Rotoscopia Animada (`RotoMask`, `RotoFrame`)
- Interpolación determinista punto a punto entre keyframes de caminos Bézier.

### 1.4. Tracking y Suavizado (`TrackingData`, `TrackingSmoothing`)
- Muestras de transformación espacial (`position`, `scale`, `rotation`, `confidence`).
- Métodos de filtrado de ruido (*jitter reduction*): `moving-average` y `exponential`.

### 1.5. Vinculación de Propiedades (`PropertyBinding`)
- Conexión desacoplada entre datos de tracking y cualquier elemento gráfico (ej. hacer que un título siga la posición $(x, y)$ de una persona con un offset $(0, -150)$).
