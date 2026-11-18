# 📜 ESPECIFICACIÓN TÉCNICA: FASE 20
## Extreme Optics, Fisheye, Crash/Snap Zooms & Dynamic Camera Movement Engine

**Documento:** `spec/phase-20-extreme-optics-camera-motion.md`  
**Estado:** `FORMAL / NORMATIVO v1.0.0`  
**Módulo:** `src/optics/`  
**Baseline:** `v4.2.0 (1,443 tests GREEN)`  
**Invariantes:** Inercia Física • Compensación de Escala Óptica • Cero Desfase Transiente • Tolerancia Numérica $\epsilon \le 10^{-10}$  

---

## 1. Declaración de Misión y Alcance

La **Fase 20** (Fase 1 de 5 del Programa de Videoclips de Vanguardia) dota al motor de las capacidades ópticas y de cámara que definen las producciones audiovisuales de alto calibre de artistas como **Tyler, The Creator**, **Kendrick Lamar (Dave Free / pgLang)** y **Ralphie Choo (Little Spain)**:

1. **Snap / Crash Zooms Rítmicos al Beat:**
   - Zooms hiper-rápidos ($100\% \to 180\% - 240\%$ en $0.10\text{s} - 0.25\text{s}$) sincronizados con impactos de batería (cajas, bombos o remates líricos).
   - Curva de rebote inercial con amortiguamiento físico subamortiguado (*underdamped harmonic oscillation*) para evitar frenados rígidos no naturales.

2. **Emulador de Ópticas Extremas & Ojo de Pez (Fisheye & Anamorphic Barrel):**
   - Deformación de barril de gran angular basada en el modelo matemático de Brown-Conrady ($r_d = r_u(1 + k_1 r_u^2)$).
   - Aberración cromática radial en los bordes del encuadre (dispersión espectral RGB con desfase de escala $\delta \in [0.5\%, 2.5\%]$).
   - Viñeta anamórfica de borde cóncavo.

3. **Dolly Zoom Virtual (Efecto Vértigo):**
   - Compensación automática entre la distancia de cámara virtual y el campo de visión focal ($FOV$), manteniendo constante el tamaño aparente del sujeto mientras el fondo se deforma o expande dramáticamente:
     $$h_{\text{subject}} = 2 \cdot d(t) \cdot \tan\left(\frac{\theta(t)}{2}\right) = \text{constante}$$

4. **Latigazos de Cámara (Whip Pans) de Transición:**
   - Movimientos angulares extremos en menos de 6 fotogramas con desenfoque direccional de movimiento forzado (`comp.motionBlur = true` y `ADBE Directional Blur`).

---

## 2. Formulación Matemática

### 2.1. Curva de Rebote Inercial para Snap Zooms
Dado un tiempo de impacto $t_0$, una escala inicial $S_0$, una escala máxima $S_{\text{peak}}$, una tasa de amortiguamiento $\lambda$ y una frecuencia angular $\omega$:
$$S(t) = S_{\text{target}} + (S_{\text{peak}} - S_{\text{target}}) \cdot e^{-\lambda (t - t_0)} \cdot \cos(\omega (t - t_0)), \quad t \ge t_0$$
Para asegurar un rebote natural de videoclip:
$$\lambda \in [12.0, 24.0] \text{ s}^{-1}, \quad \omega \in [20.0, 40.0] \text{ rad/s}$$

### 2.2. Modelo de Deformación Radial de Lente (Fisheye)
Para un punto $(x, y)$ normalizado respecto al centro óptico $(x_c, y_c)$:
$$r_u = \sqrt{(x - x_c)^2 + (y - y_c)^2}$$
$$r_d = r_u \cdot \left(1 + k_1 \cdot r_u^2 + k_2 \cdot r_u^4\right)$$
En After Effects se transpila a `ADBE Optics Compensation` con `FOV Type = Diagonal` o `ADBE Spherize`.

### 2.3. Dispersión Cromática Radial (RGB Split)
Separación radial proporcional al radio al cuadrado:
$$S_R = S_{\text{base}} \cdot (1 + \delta \cdot r_u^2), \quad S_G = S_{\text{base}}, \quad S_B = S_{\text{base}} \cdot (1 - \delta \cdot r_u^2)$$

---

## 3. Contratos y Esquemas Formales (TypeScript & Zod)

```typescript
export interface SnapZoomSpec {
  id: string;
  triggerTimeSeconds: number;
  durationSeconds: number;
  startScalePercent: number; // default: 100%
  peakScalePercent: number;  // default: 185%
  settleScalePercent: number;// default: 105% (permanece ligeramente punch-in)
  dampingRatio: number;      // 0.4 - 0.8
  frequencyHz: number;       // 4.0 - 8.0 Hz
}

export interface FisheyeLensSpec {
  id: string;
  distortionFactor: number;   // 0 a 100 (abombamiento de barril)
  chromaticAberrationPx: number; // 2px a 15px de dispersión periférica
  vignetteAmount: number;     // 0.0 a 1.0
  centerOffset: { x: number; y: number };
}

export interface DollyZoomSpec {
  id: string;
  startTimeSeconds: number;
  durationSeconds: number;
  initialFovDegrees: number; // ej. 35° (teleobjetivo)
  finalFovDegrees: number;   // ej. 85° (gran angular)
  subjectScaleLock: boolean; // true mantiene el sujeto idéntico
}
```

---

## 4. Invariantes de Calidad

1. **Invariante de Monotonía Temporal:** Los triggers de Snap Zoom satisfacen $t_0 < t_1 < \dots < t_n$.
2. **Invariante de Preservación de Sujeto en Dolly Zoom:** El tamaño del sujeto en el plano no puede variar en más de $\pm 1\%$ durante el efecto vertigo.
3. **Invariante de Reversibilidad:** Para distorsión de lente con $k_1 = 0$, $r_d = r_u$ (identidad exacta).
