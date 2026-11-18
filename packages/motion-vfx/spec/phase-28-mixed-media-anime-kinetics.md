# Especificación Técnica de Fase 28: Mixed-Media & Anime Kinetics

**Estado:** ESPECIFICACIÓN TÉCNICA FORMAL  
**Versión:** `v1.0.0`  
**Módulo:** `src/mixed-media/`  
**Dependencias:** `src/types/`, `src/utils/`, `src/mcp/`  

---

## 1. Alcance y Objetivos

### 1.1 Contexto de Autor
Inspirado en los directores creativos que fusionan animación tradicional, estética de manga y colisión de medios físicos con acción en vivo (**Khantrast**, **JID / Cole Bennett**, **Kendrick Lamar / Dave Free** y secuencias de anime de alta energía):
1. **1-Frame Manga Impact Frames:** Inserción de 1 a 2 fotogramas estroboscópicos de blanco y negro hiper-contrastado o negativo invertido en el impacto del beat/golpe sonoro.
2. **Procedural Speed Lines:** Generación procedural de haces radiales de velocidad estilo Shonen/Cyberpunk convergentes hacia el punto de fuga del sujeto con parpadeo estocástico a 12/24 fps.
3. **35mm Film Sprocket Holes & Physical Gate Jitter:** Perforaciones laterales mecánicas de celuloide de 35mm (4 perforaciones por fotograma) y 16mm con texto KeyKode marginal de película y temblor analógico de arrastre mecánico.
4. **Paper Tear & Collage Cutout Wipes:** Máscaras de rasgado orgánico con textura de borde fibroso desgarrado y revelado de capas subyacentes estilo collage de técnica mixta.
5. **Stop-Motion Doodle Boil:** Garabatos y contornos dibujados a mano con ebullición (*boiling*) a 8 o 12 fps desfasados mediante semillas procedurales.

---

## 2. Modelos Matemáticos y Algorítmicos

### 2.1 1-Frame Manga Impact Frame
En el instante de impacto sonoro $t_{\text{impact}}$, para una ventana de duración de $K$ fotogramas ($K \in \{1, 2\}$, típicamente $\Delta t = K / \text{fps}$):

$$I_{\text{impact}}(x,y,t) = \begin{cases}
1.0 - \text{Binarize}(I(x,y,t), \theta_{\text{manga}}) & \text{si } t_{\text{impact}} \le t < t_{\text{impact}} + \frac{K}{\text{fps}} \\
I(x,y,t) & \text{en otro caso}
\end{cases}$$

Donde $\text{Binarize}(I, \theta)$ comprime el rango tonal a blanco y negro puro con umbral de tinta $\theta_{\text{manga}} \approx 0.5$.

### 2.2 Procedural Radial Speed Lines
Dado un centro de foco cinético $\vec{C} = (x_c, y_c)$ y un radio de exclusión $R_{\text{inner}}$, para un ángulo $\phi = \text{atan2}(y - y_c, x - x_c)$:

$$I_{\text{line}}(r, \phi, t) = \Theta(r - R_{\text{inner}}) \cdot \Pi\left(\frac{(\phi + \delta\phi(t)) \pmod{\Delta\phi}}{\Delta\phi}\right) \cdot \text{Noise}(\phi, \lfloor t \cdot \text{fps}_{\text{boil}} \rfloor)$$

Donde:
- $\Delta\phi = \frac{2\pi}{N_{\text{lines}}}$
- $\Theta$: Función escalón de Heaviside que asegura que el rostro del sujeto permanezca libre de líneas.
- $\text{Noise}$: Modulador de intensidad y grosor por rayo renovado a la tasa de posterización ($\text{fps}_{\text{boil}} = 12$ fps).

### 2.3 35mm Sprocket Holes Geometry
Para un fotograma estándar de 35mm con relación de aspecto $4:3$ o $16:9$, las perforaciones rectangulares KS-1870 tienen dimensiones normalizadas:
- Ancho de perforación: $w_p = 2.80\text{ mm}$
- Alto de perforación: $h_p = 1.98\text{ mm}$ con radio de esquina $r = 0.5\text{ mm}$
- Paso mecánico: $p = 4.75\text{ mm}$ (4 perforaciones por fotograma estándar de 35mm).
- Inestabilidad de arrastre mecánico (*gate weave*):

$$\vec{J}_{\text{jitter}}(t) = [A_x \cdot \sin(2\pi f_1 t) + \text{wiggle}(12, 1.5)_x, \quad A_y \cdot \sin(2\pi f_2 t) + \text{wiggle}(12, 2.5)_y]$$

### 2.4 Doodle Boil (Boiling Linework)
Para un contorno vectorial $V(s) = (x(s), y(s))$ indexado por la longitud de arco $s$:

$$V_{\text{boiled}}(s, t) = V(s) + \vec{n}(s) \cdot \text{Perlin}(s \cdot f_{\text{spatial}}, \lfloor t \cdot \text{fps}_{\text{boil}} \rfloor) \cdot A_{\text{jitter}}$$

Donde $\vec{n}(s)$ es el vector normal unitario y $\text{fps}_{\text{boil}} \in \{8, 12\}$.

---

## 3. Interfaces y Tipos TypeScript

```typescript
export interface ImpactFrameSpec {
  id: string;
  impactTimeSeconds: number;
  frameDuration: 1 | 2; // 1 o 2 frames
  mode: 'INVERT_NEGATIVE' | 'HIGH_CONTRAST_BW' | 'CHROMATIC_FLASH';
  invertColors?: boolean;
}

export interface SpeedLinesSpec {
  id: string;
  startTimeSeconds: number;
  durationSeconds: number;
  centerPoint: [number, number]; // Centro de convergencia
  innerRadiusPx: number;         // Área de exclusión alrededor del sujeto
  lineCount: number;             // 30 - 120 líneas
  color: [number, number, number]; // [r, g, b]
  boilFps: number;               // 12 o 24 fps
  density: number;               // 0.2 - 1.0
}

export interface SprocketHolesSpec {
  id: string;
  gauge: '35MM' | '16MM';
  side: 'LEFT' | 'RIGHT' | 'BOTH';
  gateWeaveJitterPx: number;     // 1 - 6 px
  keyKodeText?: string;          // ej. "EASTMAN 5219 48 1024"
  opacity: number;
}

export interface PaperTearWipeSpec {
  id: string;
  startTimeSeconds: number;
  durationSeconds: number;
  direction: 'HORIZONTAL' | 'VERTICAL' | 'DIAGONAL';
  tearRoughness: number;         // 10 - 80 px de rugosidad fractal
  fiberFringePx: number;         // Flecos blancos de papel
}

export interface DoodleBoilSpec {
  id: string;
  startTimeSeconds: number;
  durationSeconds: number;
  boilFps: 8 | 12;
  jitterAmplitudePx: number;     // 2 - 8 px
  strokeColor: [number, number, number];
  strokeWidthPx: number;
}
```

---

## 4. Invariantes del Sistema
1. **Precisión Sub-Fotograma:** Los fotogramas de impacto se cuantizan estrictamente a la grilla temporal $\text{round}(t \cdot \text{fps}) / \text{fps}$.
2. **Invariante de Motion Blur:** Toda composición generada debe contener `comp.motionBlur = true`.
3. **Determinismo:** El plan compila con SHA-256 inmutable e idéntico para los mismos parámetros.
