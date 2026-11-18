# Especificación Técnica: Fase 24 — Avant-Garde Brutalist Kinetic Typography, Liquid Chrome & Perspective Anchored Text

**Versión:** 1.0.0  
**Fecha:** 2026-09-05  
**Módulo:** `src/kinetic-typography/`  
**Objetivo:** Implementar la quinta y última fase del Programa de Producción de Videoclips de Alto Calibre para After Effects, introduciendo tipografía cinética brutalista editorial (estilo Tyler, The Creator y TIME Magazine), efecto de cromo líquido metálico reflectante (estilo Ralphie Choo y Y2K revival) y anclaje espacial en perspectiva 3D (estilo Dave Free / Kendrick Lamar).

---

## 1. Fundamentos Estéticos y Arquitectura Matemática

### 1.1 Estilo Brutalista Editorial (TIME & Tyler Poster Style)
En cumplimiento estricto de [`docs/USER_DESIGN_PREFERENCES.md`](file:///F:/Dev/after-effects-mcp/docs/USER_DESIGN_PREFERENCES.md):
- **Tipografía:** Sans-serif condensada ultra-bold (`Impact`, `Arial Black`, `Anton`).
- **Deformación Vertical (Anamorphic Stretch):** Estiramiento vertical forzado al $120\% - 150\%$ en la escala Y del texto ($S_y \in [1.20, 1.50] \cdot S_x$).
- **Interletraje Negativo:** *Tracking* agresivo entre $-50$ y $-120$ para emular póster editorial de impacto visual masivo.
- **Centrado Riguroso:** `ParagraphJustification.CENTER_JUSTIFY` y punto de anclaje centrado geométricamente en la caja delimitadora:
  $$\mathbf{A} = \left[ b_{\text{left}} + \frac{b_{\text{width}}}{2}, \; b_{\text{top}} + \frac{b_{\text{height}}}{2} \right]$$
- **Paleta Cromática de Alto Contraste:** Rojo carmesí `#FF1424` (`[1.0, 0.078, 0.141]`), blanco puro `#FFFFFF` y negro profundo `#0B0B0C`.

### 1.2 Emulación de Cromo Líquido (Liquid Chrome Shader)
Para lograr el acabado metálico hiper-reflectante y viscoso sin depender de motores 3D externos:
1. **Bisel y Relieve Alfa:** `ADBE Bevel Alpha` con ángulo de luz de $45^\circ$, grosor de $4.0\text{px}$ e intensidad especular.
2. **Deformación Ondulatoria Turbulenta:** `ADBE Turbulent Displace` con tamaño pequeño ($15 - 25\text{px}$) y cantidad sutil ($8 - 18\text{px}$) con evolución animada:
   $$\text{Evolution} = \omega_{\text{ev}} \cdot t$$
3. **Inflexión Curva Especular:** Curva en S hiperbólica que refleja tonos metálicos altos y sombras de mercurio.
4. **Tinte Cromado:** Mapeo de tonos con tintes platino, cromo ácido o cromo dorado.

### 1.3 Anclaje Espacial en Perspectiva 3D (Scene Geometry Anchoring)
- Activación de capa 3D (`threeDLayer = true`).
- Proyección en perspectiva euclidiana tridimensional con rotación compuesta $[\theta_x, \theta_y, \theta_z]$ y traslación espacial $[X, Y, Z]$.
- Orientación alineada a puntos de fuga arquitectónicos o planos de suelo.

### 1.4 Slam Rítmico y Rebote Armónico Subamortiguado
Impacto percusivo en bombos o golpes de caja (*word slams*):
$$S(t) = S_{\text{target}} + (S_{\text{initial}} - S_{\text{target}}) \cdot e^{-\zeta \omega_n t} \cos(\omega_d t)$$
donde:
- $S_{\text{initial}} \approx 250\%$, $S_{\text{target}} = 100\%$
- Factor de amortiguamiento $\zeta \in [0.45, 0.65]$ (subamortiguado elástico)
- Frecuencia amortiguada $\omega_d = \omega_n \sqrt{1 - \zeta^2}$

---

## 2. Definición de Tipos e Interfaces (`src/kinetic-typography/kinetic-typography-types.ts`)

```typescript
export interface BrutalistTypeSpec {
  id: string;
  text: string;
  fontFamily: string; // "Impact", "Arial-Black", "Anton"
  fontSizePx: number; // ej. 180 - 320
  verticalStretchPercent: number; // 120% - 150%
  tracking: number; // -100 a -30
  colorHex: string; // "#FF1424" o "#FFFFFF"
  allCaps: boolean;
  boxPaddingPercent?: number;
}

export interface LiquidChromeSpec {
  id: string;
  bevelDepthPx: number; // 2.0 a 8.0
  turbulentAmount: number; // 5.0 a 25.0
  turbulentSize: number; // 10.0 a 40.0
  evolutionSpeed: number; // Ciclos/segundo
  chromePalette: "PLATINUM" | "ACID_EMERALD" | "MOLTEN_GOLD" | "CUSTOM";
  tintRgb?: [number, number, number];
}

export interface PerspectiveAnchorSpec {
  id: string;
  position3D: [number, number, number]; // [X, Y, Z]
  rotation3D: [number, number, number]; // [RotX, RotY, RotZ] en grados
  vanishingPointAlign: "CENTER" | "FLOOR_RECEDING" | "WALL_LEFT" | "WALL_RIGHT";
}

export interface WordSlamSpec {
  id: string;
  triggerTimeSeconds: number;
  durationSeconds: number; // 0.25s a 0.45s
  initialScalePercent: number; // 220% - 300%
  dampingRatio: number; // 0.55
  naturalFrequency: number; // 24.0
}

export interface KineticTypographyPlan {
  id: string;
  brutalist: BrutalistTypeSpec;
  chrome?: LiquidChromeSpec;
  perspective?: PerspectiveAnchorSpec;
  slam?: WordSlamSpec;
  extendScriptLines: string[];
  checksumSha256: string;
}
```

---

## 3. Invariantes y Certificación

1. **`comp.motionBlur = true` Obligatorio:** Toda capa de texto cinético debe tener `motionBlur = true`.
2. **Centrado Geométrico Infalible:** Todo texto con ajuste centrado debe recalcular su `Anchor Point` a partir de `sourceRectAtTime`.
3. **Determinismo SHA-256:** Garantía de idempotencia en toda compilación.
