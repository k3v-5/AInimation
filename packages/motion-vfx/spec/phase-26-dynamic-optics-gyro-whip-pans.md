# Especificación Técnica: Fase 26 — Dynamic Optics & Mechanics: 360° Centrifugal Gyro Rolls, Directional Whip-Pans & Lens Breathing

**Versión:** 1.0.0  
**Fecha:** 2026-09-05  
**Módulo:** `src/dynamic-mechanics/`  
**Objetivo:** Implementar la segunda fase de la Suite de Cinematografía Auteur Elite para After Effects, incorporando la física de cámara de *Big Dawgs* (Hanumankind / Bijoy Shetty) y transiciones invisibles por velocidad angular de Dave Free / Kendrick Lamar y Hiro Murai.

---

## 1. Fundamentos Físicos y Matemáticos

### 1.1 Giro Centrífugo de Giroscopio $360^\circ$ (Centrifugal Gyro Barrel Roll)
Rotación continua o acelerada sobre el eje óptico Z de la cámara, sincronizada con la aceleración física de vehículos, motocicletas o acrobacias:
- Ángulo de rotación en el tiempo:
  $$\theta(t) = \theta_0 + \omega_0 \cdot t + \frac{1}{2} \alpha \cdot t^2$$
- Para giros discretos de $180^\circ$ o $360^\circ$ sincronizados a compás musical:
  $$\theta(\tau) = \theta_{\text{start}} + \Delta \theta \cdot f_{\text{smooth}}(\tau), \quad \tau = \frac{t - t_0}{\Delta t}$$
  con interpolación Bézier $\mathcal{C}^1$ o sinusoidal:
  $$f_{\text{smooth}}(\tau) = \frac{1 - \cos(\pi \tau)}{2}$$
- Para evitar costuras negras durante rotaciones angulares inclinadas, se calcula el factor de escala mínimo circunscrito:
  $$S_{\text{min}} = \sqrt{2} \approx 141.42\% \quad (\text{para cualquier } \theta)$$
  reforzado por `ADBE Motion2` (*Motion Tile*) con `Mirror Edges = true`.

### 1.2 Directional Whip-Pan Match Cut (Barrido Direccional Invisible)
Transición entre dos tomas distantes mediante un paneo ultrarrápido a velocidad angular crítica $\omega_{\text{crit}} > 600^\circ/\text{s}$:
- Perfil de velocidad angular acampanada (Gaussian Bell Curve):
  $$v(t) = v_{\text{max}} \cdot \exp\left( - \frac{(t - t_{\text{cut}})^2}{2 \sigma_{\text{whip}}^2} \right)$$
- En el instante exacto de máximo desenfoque ($t = t_{\text{cut}}$), se conmuta la capa saliente (Toma A) por la entrante (Toma B).
- Integración de `ADBE Directional Blur` direccional dinámico:
  $$\text{Blur Length}(t) = L_{\text{max}} \cdot \frac{v(t)}{v_{\text{max}}}$$
  con dirección horizontal ($\text{Direction} = 90^\circ$) o vertical ($\text{Direction} = 0^\circ$).

### 1.3 Procedural Lens Breathing (Respiración de Foco Óptico)
En ópticas anamórficas de cine (Cooke, Panavision, Lomo), el cambio de plano focal entre primer plano y fondo produce un cambio parásito sutil en la distancia focal efectiva (respiración del lente):
- Desplazamiento de escala acoplado al tirón de foco:
  $$S_{\text{breathe}}(t) = 100.0\% + \Delta S_{\text{breathe}} \cdot f_{\text{rack}}(\tau)$$
  donde $\Delta S_{\text{breathe}} \in [0.8\%, 2.5\%]$.
- Acompañado de desenfoque Gaussiano inverso entre planos:
  $$\text{Blur}_{\text{foreground}}(t) \propto (1 - \tau), \quad \text{Blur}_{\text{background}}(t) \propto \tau$$

---

## 2. Tipos e Interfaces (`src/dynamic-mechanics/mechanics-types.ts`)

```typescript
export interface CentrifugalGyroRollSpec {
  id: string;
  startTimeSeconds: number;
  durationSeconds: number;
  totalRollDegrees: number; // 180, 360, 720
  direction: "CLOCKWISE" | "COUNTER_CLOCKWISE";
  mirrorEdges: boolean;
  scaleBufferPercent: number; // 142% por defecto
}

export interface WhipPanMatchCutSpec {
  id: string;
  cutTimeSeconds: number;
  transitionDurationSeconds: number; // 0.25s a 0.40s
  direction: "PAN_LEFT" | "PAN_RIGHT" | "TILT_UP" | "TILT_DOWN";
  maxBlurLengthPx: number; // 160 - 240 px
  seamlessOffsetPx: number; // Desplazamiento de posición de cuadro
}

export interface LensBreathingSpec {
  id: string;
  startTimeSeconds: number;
  durationSeconds: number;
  breatheScalePercent: number; // 1.5%
  focusPullDirection: "NEAR_TO_FAR" | "FAR_TO_NEAR";
}

export interface DynamicMechanicsPlan {
  id: string;
  gyroRoll?: CentrifugalGyroRollSpec;
  whipPan?: WhipPanMatchCutSpec;
  lensBreathing?: LensBreathingSpec;
  extendScriptLines: string[];
  checksumSha256: string;
}
```

---

## 3. Invariantes y Certificación

1. **Circunscripción de Rotación:** Toda rotación giroscópica debe tener un factor de escala $\ge 141.4\%$ o *Motion Tile* para garantizar cobertura perimetral $100\%$ continua.
2. **Invariante de Motion Blur:** `comp.motionBlur = true` y `layer.motionBlur = true`.
3. **Simetría de Whip Pan:** El desenfoque direccional debe alcanzar su pico idéntico en el corte $t = t_{\text{cut}}$ tanto en la toma saliente como en la entrante.
