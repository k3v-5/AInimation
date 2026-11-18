# Especificación Técnica de Fase 27: Nocturnal Photonics & Optical Artefacts

**Estado:** ESPECIFICACIÓN TÉCNICA FORMAL  
**Versión:** `v1.0.0`  
**Módulo:** `src/photonics/`  
**Dependencias:** `src/types/`, `src/utils/`, `src/mcp/`  

---

## 1. Alcance y Objetivos

### 1.1 Contexto de Autor
Inspirado en la dirección de fotografía nocturna y artefactos ópticos de alto impacto vistos en producciones de **Kendrick Lamar / Dave Free** (*N95* thermal aesthetics), **Travis Scott / Don Toliver** (*TORE UP*, *CAN'T SAY* anamorphic blue streak flares y shutter drag ghosts) y **Tainy** (*DATA* nocturnal cyber-optics):
1. **Shutter Drag & Ghost Echo Trails:** Simulación física de obturador abierto lento ($360^\circ$ shutter angle / $\le 1/15\text{s}$) generando estelas luminosas y copias fantasma reactivas al movimiento cinético.
2. **Anamorphic Streak Flares:** Extracción de altas luces especulares ($Y \ge Y_{\text{threshold}}$) con dispersión horizontal extrema ($90^\circ$ directional beam) y tinte cromático cian/ámbar.
3. **Prism Star & Cross-Screen Diffraction:** Difracción óptica de 4 o 6 puntas sobre brillos puntuales simulando cristales de rejilla cinematográfica.
4. **FLIR / Infrared Thermal Vision:** Mapeo espectral térmico basado en luminancia perceptual con falso color (Ironbow / Rainbow / White-Hot) y micro-ruido sensor infrarrojo.

---

## 2. Modelos Matemáticos y Algorítmicos

### 2.1 Shutter Drag & Kinetic Echo Trails
Dada una capa de video con velocidad angular/lineal $\vec{v}(t)$, el efecto de arrastre de obturador genera $N$ ecos temporales muestreados en intervalos $\Delta t_{\text{echo}}$ con decaimiento exponencial:

$$E(x, y, t) = \sum_{k=0}^{N-1} I(x, y, t - k \cdot \Delta t_{\text{echo}}) \cdot \delta^k$$

Donde:
- $N$: Número de ecos ($N \in [2, 12]$).
- $\Delta t_{\text{echo}}$: Intervalo temporal en segundos (típicamente $-0.033\text{s}$ a $-0.100\text{s}$).
- $\delta$: Factor de decaimiento exponencial ($\delta \in [0.5, 0.95]$).
- Modo de fusión: `ADBE Echo` con operador `MAXIMUM` (retiene los bordes de mayor energía lumínica) o `SCREEN`.

### 2.2 Anamorphic Streak Flare (Horizontal Optical Beam)
Para cada píxel $P(x,y)$, se calcula la luminancia perceptual $Y$:

$$Y = 0.299 R + 0.587 G + 0.114 B$$

Se aíslan las altas luces:

$$I_{\text{high}}(x,y) = \begin{cases} P(x,y) & \text{si } Y \ge Y_{\text{threshold}} \\ 0 & \text{en otro caso} \end{cases}$$

Se aplica una convolución unidimensional en el eje horizontal ($\theta = 90^\circ$):

$$I_{\text{streak}}(x, y) = (I_{\text{high}} * K_{\text{dir}, \theta=90^\circ, L})(x, y)$$

Se tiñe con el vector cromático anamórfico $\vec{C}_{\text{tint}}$ (por defecto cian neón $[0.1, 0.7, 1.0]$ o ámbar dorado $[1.0, 0.65, 0.1]$) y se añade al encuadre original:

$$P_{\text{final}} = P + \alpha_{\text{intensity}} \cdot (\vec{C}_{\text{tint}} \odot I_{\text{streak}})$$

### 2.3 Prism Star Diffraction (Cross-Screen)
La difracción de rejilla se modela mediante la superposición de $M$ direcciones simétricas cruzadas ($\theta_m = m \cdot \frac{180^\circ}{M}$):
- **4 Puntas (Cross Screen):** $M = 2 \implies \theta \in \{45^\circ, 135^\circ\}$
- **6 Puntas (Star-6):** $M = 3 \implies \theta \in \{30^\circ, 90^\circ, 150^\circ\}$

$$I_{\text{star}}(x,y) = \sum_{m=1}^M (I_{\text{high}} * K_{\text{dir}, \theta_m, L_{\text{star}}})(x,y)$$

### 2.4 FLIR Thermal Infrared Palette (Ironbow LUT)
Se normaliza la luminancia $Y \in [0, 1]$ y se transfiere a través de la función de transferencia térmica pseudo-color:

$$\vec{C}_{\text{FLIR}}(Y) = \begin{cases} 
[0, 0, 0.5 + Y] & \text{si } 0.0 \le Y < 0.25 \text{ (Fondo Frío / Azul)} \\
[Y \cdot 2, 0, 0.8 - Y] & \text{si } 0.25 \le Y < 0.50 \text{ (Violeta / Magenta)} \\
[1.0, (Y - 0.5) \cdot 2, 0] & \text{si } 0.50 \le Y < 0.75 \text{ (Naranja / Fuego)} \\
[1.0, 1.0, (Y - 0.75) \cdot 4] & \text{si } 0.75 \le Y \le 1.00 \text{ (Amarillo / Blanco Térmico)}
\end{cases}$$

Se orquesta en After Effects mediante `ADBE Colorama` con preset de salida térmico o rampa de mapa de gradiente con inversión de luminancia y realce de bordes infrarrojos (`ADBE Find Edges` o `ADBE Unsharp Mask`).

---

## 3. Interfaces y Tipos TypeScript

```typescript
export interface ShutterDragSpec {
  id: string;
  startTimeSeconds: number;
  durationSeconds: number;
  echoCount: number;         // 2 - 10 ecos
  echoTimeStepSeconds: number; // -0.05 a -0.01 seg
  decay: number;             // 0.60 a 0.90
  blendOperator: 'MAXIMUM' | 'ADD' | 'SCREEN';
  chromaticDispersion?: boolean;
}

export interface AnamorphicStreakSpec {
  id: string;
  startTimeSeconds?: number;
  durationSeconds?: number;
  thresholdPercent: number;  // 70% - 95%
  streakLength: number;      // 50 - 500 px
  directionDegrees: number;  // 90.0 (horizontal)
  tintColor: [number, number, number]; // [0.0-1.0, ...]
  intensity: number;         // 0.5 - 2.5
}

export interface PrismStarSpec {
  id: string;
  points: 4 | 6;
  thresholdPercent: number;
  starLength: number;
  intensity: number;
  rotationDegrees?: number;
}

export interface FlirThermalSpec {
  id: string;
  palette: 'IRONBOW' | 'RAINBOW' | 'WHITE_HOT' | 'ARCTIC';
  thermalNoiseIntensity: number; // 0 - 30%
  edgeEnhancement: boolean;
}
```

---

## 4. Invariantes del Sistema
1. **Conservación de Rango:** La luminancia y parámetros normalizados no exceden el espacio colorimétrico estándar $[0, 1]$.
2. **Invariante de Motion Blur:** Toda composición generada debe contener `comp.motionBlur = true` y cada capa afectada `layer.motionBlur = true`.
3. **Determinismo:** Mismo spec produce idéntico ExtendScript y SHA-256 hash.
