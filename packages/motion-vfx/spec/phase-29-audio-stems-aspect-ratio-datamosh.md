# Especificación Técnica de Fase 29: Audio Stem Engine, Dynamic Aspect Ratio Breathing & Datamosh Y2K

**Estado:** ESPECIFICACIÓN TÉCNICA FORMAL  
**Versión:** `v1.0.0`  
**Módulo:** `src/stem-kinetics/`  
**Dependencias:** `src/types/`, `src/utils/`, `src/mcp/`  

---

## 1. Alcance y Objetivos

### 1.1 Contexto de Autor
Inspirado en la simbiosis rítmica y mutación de formato en producciones de vanguardia (**Tainy** en *DATA*, **Kendrick Lamar** en *Count Me Out* y los beat drops brutales de **Travis Scott** y **Don Toliver**):
1. **Audio Stem Decoupling & Reactive Physics:**
   - **808 Sub-Bass Reaction:** Extracción de envolvente sub-bass (20-80 Hz) acoplada a escala de rebote sísmico ($S(t) = S_0 + k_{808} \cdot E_{\text{sub}}(t)$), compresión elástica y pulsación de cámara.
   - **Hi-Hat / Snare High-Transient Reaction:** Transitorios de alta frecuencia (5-15 kHz) que gatillan micro-dispersión cromática y jitter de obturador en redobles rápidos (rolls de hi-hat 1/16 y 1/32).
2. **Dynamic Aspect Ratio Breathing:**
   - Modulación dinámica y fluida entre encuadres cinematográficos:
     - $9:16$ (Vertical social) $\longleftrightarrow$ $1:1$ (Cuadrado) $\longleftrightarrow$ $4:3$ (IMAX Academy) $\longleftrightarrow$ $16:9$ (Widescreen estándar) $\longleftrightarrow$ $2.39:1$ (Anamorphic Scope).
   - Barras de Letterbox / Pillarbox calculadas con matemática analítica y animación elástica sin recortes de píxeles indeseados.
3. **Y2K Datamosh & P-Frame Motion Vector Glitch:**
   - Emulación procedural de pérdida de I-Frame (*I-frame drop*) donde los vectores de movimiento de la Toma B arrastran la textura congelada de la Toma A.
   - Cuantización de macrobloques MPEG de $8 \times 8$ o $16 \times 16$ píxeles y mapa de desplazamiento direccional en el eje del movimiento predominante.

---

## 2. Modelos Matemáticos y Algorítmicos

### 2.1 808 Sub-Bass Elastic Bounce Reaction
Dada una envolvente RMS de subgraves $E_{\text{sub}}(t) \in [0, 1]$ y un tiempo de golpe $t_{\text{hit}}$:

$$S_{\text{react}}(t) = S_{\text{base}} \cdot \left[ 1.0 + A_{\text{bounce}} \cdot \exp\left(-\frac{t - t_{\text{hit}}}{\tau_{\text{decay}}}\right) \cdot \cos\left(2\pi f_{\text{resonance}} (t - t_{\text{hit}})\right) \right]$$

Donde:
- $A_{\text{bounce}}$: Amplitud de impacto de escala ($0.04$ a $0.15 \implies +4\%$ a $+15\%$).
- $\tau_{\text{decay}}$: Tiempo característico de amortiguamiento (típicamente $0.15\text{s}$ a $0.35\text{s}$).
- $f_{\text{resonance}}$: Frecuencia de resonancia viscoelástica ($8$ a $16\text{ Hz}$).

### 2.2 Aspect Ratio Matte Geometry
Para una composición de dimensiones $[W_{\text{comp}}, H_{\text{comp}}]$ y una relación de aspecto objetivo $R_{\text{target}} = \frac{W_{\text{target}}}{H_{\text{target}}}$:

$$\begin{cases}
\text{Si } R_{\text{target}} < \frac{W_{\text{comp}}}{H_{\text{comp}}} \text{ (Pillarbox)}: & W_{\text{visible}} = H_{\text{comp}} \cdot R_{\text{target}}, \quad H_{\text{visible}} = H_{\text{comp}} \\
\text{Si } R_{\text{target}} \ge \frac{W_{\text{comp}}}{H_{\text{comp}}} \text{ (Letterbox)}: & W_{\text{visible}} = W_{\text{comp}}, \quad H_{\text{visible}} = \frac{W_{\text{comp}}}{R_{\text{target}}}
\end{cases}$$

Las alturas de las barras superior e inferior son:

$$H_{\text{bar}} = \frac{H_{\text{comp}} - H_{\text{visible}}}{2}$$

Y los anchos de las barras laterales son:

$$W_{\text{bar}} = \frac{W_{\text{comp}} - W_{\text{visible}}}{2}$$

Para una transición dinámica entre dos relaciones de aspecto $R_1 \to R_2$ con tiempo normalizado $\tau \in [0, 1]$:

$$R(\tau) = R_1 + (R_2 - R_1) \cdot (3\tau^2 - 2\tau^3)$$

### 2.3 Y2K Datamosh Macroblock Displacement
En el fotograma de corte $t_{\text{cut}}$, se congela el mapa de píxeles de la Toma A y se modula mediante la velocidad de movimiento $\vec{V}(x,y)$ de la Toma B:

$$P_{\text{datamosh}}(x,y,t) = P_A\left(x - \Delta t \cdot \left\lfloor \frac{V_x}{B} \right\rfloor \cdot B, \quad y - \Delta t \cdot \left\lfloor \frac{V_y}{B} \right\rfloor \cdot B\right)$$

Donde $B \in \{8, 16\}$ es el tamaño del macrobloque en píxeles.

---

## 3. Interfaces y Tipos TypeScript

```typescript
export interface SubBassReactionSpec {
  id: string;
  hitTimesSeconds: number[];     // Tiempos de golpe de 808
  bounceScalePercent: number;    // ej. 8.0 -> +8%
  decaySeconds: number;          // ej. 0.25
  resonanceHz: number;           // ej. 12.0
  chromaticAberrationPx?: number;// micro dispersión en el pico
}

export type AspectRatioFormat = '9:16' | '1:1' | '4:3' | '16:9' | '2.39:1';

export interface AspectRatioBreathingSpec {
  id: string;
  transitions: Array<{
    targetFormat: AspectRatioFormat;
    startTimeSeconds: number;
    durationSeconds: number;
  }>;
  barColor?: [number, number, number];
}

export interface DatamoshSpec {
  id: string;
  cutTimeSeconds: number;
  durationSeconds: number;       // 0.2 a 0.8 seg de arrastre de artefactos
  macroblockSize: 8 | 16;
  displacementIntensity: number; // 20 - 150 px
}
```

---

## 4. Invariantes del Sistema
1. **Preservación de Área Visibile:** Las barras de recorte nunca son negativas ($H_{\text{bar}} \ge 0, W_{\text{bar}} \ge 0$).
2. **Invariante de Motion Blur:** Toda composición generada debe contener `comp.motionBlur = true`.
3. **Determinismo:** SHA-256 idéntico y reproducible para cualquier compilación.
