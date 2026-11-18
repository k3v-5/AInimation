# 📜 ESPECIFICACIÓN TÉCNICA: FASE 22
## Analog Film Emulation, 16mm/35mm Grain, Halation & Auteur Color Grading Engine

**Documento:** `spec/phase-22-analog-film-texture-color-grading.md`  
**Estado:** `FORMAL / NORMATIVO v1.0.0`  
**Módulo:** `src/film/`  
**Baseline:** `v4.4.0 (1,459 tests GREEN)`  
**Invariantes:** Conservación Energética • Distribución de Grano por Luminancia • Cero Clipping Extremo • Tolerancia Numérica $\epsilon \le 10^{-10}$  

---

## 1. Declaración de Misión y Alcance

La **Fase 22** (Fase 3 de 5 del Programa de Videoclips de Vanguardia) dota al motor del acabado de textura analógica y la graduación de color de autor característica de las producciones cinematográficas de **Tyler, The Creator**, **Kendrick Lamar** y **Ralphie Choo**:

1. **Simulador de Grano Fílmico Procedural (16mm & 35mm):**
   - Distribución física de haluros de plata dependiente de la luminancia local $Y$:
     $$\sigma_{\text{grain}}(Y) = \sigma_{\text{base}} \cdot 4 \cdot Y \cdot (1 - Y)$$
     La densidad de grano es máxima en tonos medios ($Y \approx 0.5$) y decrece naturalmente en sombras profundas y altas luces quemadas.
   - Distinción entre emulsión **16mm** (grano grueso y áspero) y **35mm** (grano fino de alta resolución).

2. **Film Halation Rojo (Dispersión Óptica de Altas Luces):**
   - Emulación física de la capa *antihalation backing* de las películas analógicas Kodak Vision3.
   - Aislamiento de altas luces ($Y > 0.80$), dispersión gaussiana roja ($\lambda_{\text{red}} \approx 650\text{ nm}$) y mezcla aditiva/trama (`Screen`) sobre bordes de alto contraste.

3. **Fluctuación de Obturación (Shutter Flicker) & Gate Weave:**
   - Variación orgánica determinista de exposición fotograma a fotograma ($\Delta \text{EV} \in [-0.05, +0.05]$) simulando la mecánica de obturador rotativo.
   - Micro-desplazamiento de arrastre (*Gate Weave*): $\Delta x, \Delta y \in [-1.2\text{px}, +1.2\text{px}]$ simulando el paso del celuloide por la ventanilla de cámara.

4. **Perfiles de Color de Autor (Auteur Color Bibles):**
   - **`TYLER_PASTEL_70S`:** Sombras levantadas con tinte turquesa/verde menta, amarillos mostaza, tonos sepia cálidos y compresión de altas luces.
   - **`KENDRICK_BLEACH_BYPASS_BW`:** Retención de plata (*Bleach Bypass*), contraste ultra-alto, negros puros aplastados y tonos de piel metálicos dramáticos.
   - **`RALPHIE_MINIDV_ACID`:** Estética híbrida analógico-digital Y2K, saturación hiper-realista y levantamiento azulado de pedestal.

---

## 2. Formulación Matemática

### 2.1. Curva de Densidad de Grano por Luminancia
Dado un pixel con luminancia $Y \in [0.0, 1.0]$:
$$G(Y) = \sigma_0 \cdot \left[ \sin(\pi \cdot Y) \right]^\gamma, \quad \gamma \in [1.2, 1.8]$$
Esto replica la respuesta estocástica real de los haluros de plata de las emulsiones fotográficas.

### 2.2. Aislamiento y Dispersión de Halation
1. **Máscara de Altas Luces:**
   $$M_{\text{hl}}(x, y) = \max\left(0, \frac{Y(x, y) - Y_{\text{thresh}}}{1 - Y_{\text{thresh}}}\right)$$
2. **Dispersión Gaussiana:**
   $$H_{\text{red}}(x, y) = \left( M_{\text{hl}} * K_{\sigma_{\text{halo}}} \right)(x, y) \cdot [1.0, 0.10, 0.05]$$
3. **Composición Final:**
   $$C_{\text{final}} = 1 - (1 - C_{\text{in}}) \cdot (1 - \alpha_{\text{halo}} \cdot H_{\text{red}})$$

---

## 3. Contratos y Esquemas Formales (TypeScript & Zod)

```typescript
export interface FilmGrainSpec {
  id: string;
  gauge: "16MM" | "35MM";
  intensity: number; // 0.0 a 1.0 (default: 0.35)
  luminanceCoupling: boolean; // true modula el grano según tonos medios
}

export interface FilmHalationSpec {
  id: string;
  threshold: number; // 0.70 a 0.95 (default: 0.82)
  radiusPx: number;  // 10 a 45 px (default: 24)
  intensity: number; // 0.0 a 1.0 (default: 0.65)
  tintHex: string;   // default: "#FF1A1A" (Rojo Halation)
}

export interface ShutterFlickerSpec {
  id: string;
  frequencyHz: number; // 12 a 24 Hz
  amplitudeEv: number; // 0.02 a 0.08 EV
  gateWeavePx: number; // 0.5 a 2.5 px
}

export interface AuteurColorGradingSpec {
  id: string;
  profile: "TYLER_PASTEL_70S" | "KENDRICK_BLEACH_BYPASS_BW" | "RALPHIE_MINIDV_ACID" | "CUSTOM";
  saturation: number;  // 0.0 a 2.0
  contrast: number;    // 0.5 a 2.0
  liftPedestal: number;// 0.0 a 0.15
  shadowTintRgb?: [number, number, number];
  highlightTintRgb?: [number, number, number];
}
```

---

## 4. Invariantes de Calidad

1. **Acotamiento de Luminancia:** Ninguna transformación de color ni adición de grano puede inducir valores de canal fuera de $[0.0, 1.0]$ o provocar NaN/Infinity.
2. **Monotonía de Halation:** La intensidad de Halation es monótona no decreciente respecto a la luminancia ($Y_1 \le Y_2 \implies H(Y_1) \le H(Y_2)$).
3. **Determinismo:** El ruido y flicker con semilla determinista genera exactamente el mismo hash SHA-256 en ejecuciones idénticas.
