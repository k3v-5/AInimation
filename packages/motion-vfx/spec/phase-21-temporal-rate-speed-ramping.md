# 📜 ESPECIFICACIÓN TÉCNICA: FASE 21
## Temporal Rate Modulation, Frame Stylization & Quantized Speed Ramping Engine

**Documento:** `spec/phase-21-temporal-rate-speed-ramping.md`  
**Estado:** `FORMAL / NORMATIVO v1.0.0`  
**Módulo:** `src/temporal/`  
**Baseline:** `v4.3.0 (1,451 tests GREEN)`  
**Invariantes:** Continuidad de Primera Derivada ($\mathcal{C}^1$) • Monotonía Temporal Estricta ($t_s(t_1) \le t_s(t_2)$) • Cero Desfase al Drop  

---

## 1. Declaración de Misión y Alcance

La **Fase 21** (Fase 2 de 5 del Programa de Videoclips de Vanguardia) introduce el control temporal plástico y la modulación de velocidad de fotogramas, características clave de directores como **Dave Free (Kendrick Lamar)**, **Wolf Haley (Tyler, The Creator)** y la estética vanguardista de **Ralphie Choo**:

1. **Posterize Time & Variable Frame-Rate (8fps / 12fps / 15fps):**
   - Conversión procedural de la tasa de muestreo temporal para conferir a los planos la textura orgánica del celuloide clásico de 16mm, animación japonesa tradicional "a doses" ($12\text{ fps}$) o cine de stop-motion experimental ($8\text{ fps}$), dentro de un contenedor master a 30 o 60 fps.
2. **Speed Ramping Cuantizado al Beat:**
   - Aceleración en compases de tensión ($250\% - 400\%$) y aterrizaje en cámara lenta ultra-suave ($35\% - 50\%$) exactamente en el impacto del bombo (*downbeat*) o transiente musical.
   - Interpolación Bézier suave con continuidad $\mathcal{C}^1$ en la curva de *Time Remapping* para erradicar tirones o pérdidas de fotogramas.
3. **Stutter Freeze & Micro-Congelamiento Rítmico:**
   - Congelamientos relámpago de 2 a 4 fotogramas en síncopas o silencios percusivos, seguidos de liberación inercial.
4. **Transpilación ExtendScript a After Effects:**
   - Manejo nativo de `layer.enableTimeRemapping()`, inyección de keyframes Bézier en `timeRemap` y aplicación de `ADBE Posterize Time`.

---

## 2. Formulación Matemática

### 2.1. Muestreo Discreto (Posterize Time)
Dado un tiempo continuo de composición $t$ y una tasa de cuadros objetivo $f_{\text{target}} \in \{8, 12, 15, 24\}$:
$$t_{\text{sampled}}(t) = \frac{\lfloor t \cdot f_{\text{target}} \rfloor}{f_{\text{target}}}$$
Garantiza que la imagen se mantenga fija durante intervalos exactos de $\Delta t = \frac{1}{f_{\text{target}}}$.

### 2.2. Curva de Time Remapping con Continuidad $\mathcal{C}^1$
Sea $t_{\text{timeline}}$ el tiempo en la composición y $t_{\text{source}}(t_{\text{timeline}})$ el tiempo reproducido del clip fuente:
1. **Velocidad Instantánea:**
   $$v(t) = \frac{d t_{\text{source}}}{d t_{\text{timeline}}}$$
2. **Invariante de Monotonía (No marcha atrás involuntaria):**
   $$v(t) \ge 0 \quad \forall t \in [0, T]$$
3. **Aterrizaje en el Beat:**
   Si el transiente musical ocurre en $t_{\text{drop}}$, la transición de alta velocidad a cámara lenta alcanza su punto de inflexión exactamente en:
   $$\left.\frac{d^2 t_{\text{source}}}{d t_{\text{timeline}}^2}\right|_{t = t_{\text{drop}}} = 0 \quad \text{o} \quad v(t_{\text{drop}}) = v_{\text{slow}}$$

---

## 3. Contratos y Esquemas Formales (TypeScript & Zod)

```typescript
export interface PosterizeTimeSpec {
  id: string;
  targetFps: number; // 8, 12, 15, 24
  inTimeSeconds?: number;
  outTimeSeconds?: number;
}

export interface SpeedRampSegment {
  startTimeSeconds: number;
  endTimeSeconds: number;
  speedMultiplier: number; // ej. 3.0 (300%) o 0.4 (40%)
  easing: "BEZIER" | "LINEAR" | "EXPONENTIAL";
}

export interface QuantizedSpeedRampSpec {
  id: string;
  sourceClipDurationSeconds: number;
  segments: SpeedRampSegment[];
  targetBeatDropTimeSeconds: number; // Momento exacto del impacto musical
}

export interface StutterFreezeSpec {
  id: string;
  triggerTimeSeconds: number;
  freezeDurationSeconds: number; // ej. 0.10s (3 frames a 30fps)
  postResumeSpeedMultiplier: number; // default: 1.0
}
```

---

## 4. Invariantes de Calidad

1. **Monotonía Temporal Estricta:** $t_{\text{source}}(t_a) \le t_{\text{source}}(t_b)$ para todo $t_a < t_b$.
2. **Cero Salto de Fotograma:** La curva $t_{\text{source}}(t)$ es estrictamente continua ($\mathcal{C}^0$).
3. **Límites de Metraje:** $0 \le t_{\text{source}}(t) \le \text{duration}_{\text{source}}$ para todo $t$ en la línea de tiempo.
