# 📜 ESPECIFICACIÓN TÉCNICA: FASE 19
## Object Detection, Subject Segmentation & Multi-Instance Compositing Engine

**Documento:** `spec/phase-19-object-detection-subject-compositing.md`  
**Estado:** `FORMAL / NORMATIVO v1.0.0`  
**Módulo:** `src/compositing/subject/`  
**Baseline:** `v4.1.0 (1,432 tests GREEN)`  
**Invariantes:** Determinismo • Zero Network Leak • Cero Colisiones Z-Order • Tolerancia Numérica $\epsilon \le 10^{-10}$  

---

## 1. Declaración de Misión y Alcance

La **Fase 19** extiende la arquitectura del motor audiovisual introduciendo una **capa consciente de sujetos y objetos (*Object-Aware & Subject-Centric Compositing*)**, permitiendo dos de las técnicas visuales de mayor impacto en la postproducción publicitaria, cinematográfica y editorial:

1. **Texto y Gráficos Detrás del Sujeto (*Text Behind Subject / Depth Sandwich*):**
   - Segmentación espacial del sujeto principal en primer plano.
   - Generación de jerarquía de capas 3D donde la tipografía (estilo **TIME Editorial**) se inserta físicamente entre el fondo del video y el cuerpo del sujeto.
   - Desvanecimiento de borde adaptable (*edge feathering*) y desenfoque de profundidad artificial (*depth bokeh*).

2. **Composición Multi-Toma del Mismo Sujeto (*Multi-Take Clone Weaver*):**
   - Fusión espacial y temporal de 2 o más tomas del mismo sujeto actuando en diferentes zonas de un encuadre estático (ej. Izquierda, Centro, Derecha).
   - Generación automática de máscaras divididas (*Split Mattes*) con bordes difuminados continuos.
   - Prevención de artefactos acústicos (desduplicación de ruido de sala para evitar duplicación de decibelios en el fondo ambiental).

### Lo que INCLUYE la Fase 19:
- Esquemas de datos normalizados para detección de sujetos (`DetectedSubject`, `SubjectTrack`, `BoundingBox2D`, `PolygonContour`).
- Motor de detección procedural y adaptativo por diferencia temporal/fondo con filtrado de ruido.
- Suavizado temporal de trayectorias y límites de máscara (*Temporal Trajectory Smoothing*) para eliminar temblores (*jitter*).
- Motor de composición *Text Behind Subject* con transpilación a ExtendScript JSX (`MaskShape`, `maskFeather`, `ParagraphJustification.CENTER_JUSTIFY`).
- Motor de composición *Multi-Take Clone Weaver* con cálculo de fronteras de corte (*Voronoi/Split bounds*) y mezcla de audio desduplicada.
- Registro de herramientas MCP (`compose_text_behind_subject`, `compose_multi_take_clones`, `detect_subjects_in_clip`).
- Suite de pruebas de 7 capas con Property-Based Testing (`fast-check`).

### Lo que NO INCLUYE la Fase 19:
- Descarga en tiempo de ejecución de modelos pesados (>1 GB) desde repositorios externos (en estricto cumplimiento de la política de red cero y air-gapped; los pesos deben ser locales o mediante descriptores estáticos/procedurales).
- Deformación de malla 3D compleja (*rigging*) sobre la anatomía humana.

---

## 2. Principios Arquitectónicos e Invariantes

1. **Invariante de Jerarquía Z (Z-Order Monotonicity):**
   En el modo *Text Behind Subject*, el orden de renderizado en la pila de capas es estrictamente monótono:
   $$Z_{\text{background}} < Z_{\text{graphics/text}} < Z_{\text{foreground\_cutout}}$$
   Ninguna mutación del grafo puede invertir la relación $Z_{\text{graphics}} < Z_{\text{cutout}}$.

2. **Invariante de Borde Suave (Edge Continuity & Feathering):**
   Toda máscara de recorte de sujeto debe poseer un desvanecimiento mínimo no negativo:
   $$\sigma_{\text{feather}} \ge 2.0\text{ px}$$
   para prevenir cortes duros tipo pixelado sobre cabello y extremidades.

3. **Invariante de Partición Espacial (Non-Overlapping Clone Partitioning):**
   En la composición multi-toma, la suma de las máscaras de opacidad en cualquier punto $(x, y)$ del plano compuesto debe normalizarse exactamente a 1:
   $$\sum_{k=1}^{N_{\text{takes}}} \alpha_k(x, y) = 1.0 \pm 10^{-6}$$
   evitando sobreexposición o zonas oscuras en la unión del fondo estático.

4. **Invariante de Conservación Acústica de Sala (Room Tone Neutrality):**
   Al combinar $N$ tomas simultáneas de un mismo ambiente, el nivel de ruido de fondo consolidado no puede exceder el nivel de la toma maestra:
   $$L_{\text{ambient, consolidated}} \le \max_{k}(L_{\text{ambient}, k}) + 0.5\text{ dB}$$

---

## 3. Modelo Matemático y Algorítmico

### 3.1. Suavizado Temporal de Trayectorias y Bounding Boxes
Dada una secuencia de límites detectados $B_t = [x_t, y_t, w_t, h_t]$ con posibles fluctuaciones de detección fotograma a fotograma:
$$\hat{B}_t = \alpha \cdot B_t + (1 - \alpha) \cdot \hat{B}_{t-1}, \quad \alpha \in [0.15, 0.40]$$
donde $\alpha$ equilibra la respuesta a movimientos corporales reales y la supresión de temblor (*jitter*).

### 3.2. División Espacial Óptima para Clones (Optimal Split Boundaries)
Dadas $N$ tomas con centroides de sujeto $C_k = (x_k, y_k)$:
- Se calculan las mediatrices ortogonales entre centroides contiguos:
  $$x_{\text{split}, k} = \frac{x_k + x_{k+1}}{2}$$
- La función de transición de la máscara $\alpha_k(x)$ sigue una sigmoide suave con parámetro de desvanecimiento $W_{\text{feather}}$:
  $$\alpha_k(x) = \frac{1}{1 + \exp\left(-\frac{x - x_{\text{split}, k}}{W_{\text{feather}} / 4}\right)}$$

---

## 4. Contratos y Esquemas Formales (TypeScript & Zod)

```typescript
export interface BoundingBox2D {
  x: number;      // Normalizado [0.0, 1.0] o píxeles
  y: number;
  width: number;
  height: number;
}

export interface DetectedSubject {
  id: string;
  frameIndex: number;
  timestampSeconds: number;
  label: "PERSON" | "FACE" | "OBJECT" | "ANIMAL";
  confidence: number;
  boundingBox: BoundingBox2D;
  contourPoints?: Array<{ x: number; y: number }>; // Trazado cerrado
  trackId: string;
}

export interface TextBehindSubjectConfig {
  id: string;
  sourceClipId: string;
  subjectTrackId: string;
  text: string;
  typography: {
    fontFamily: string; // Anton, Impact, Arial Black
    fontSize: number;
    colorHex: string;   // Crimson #FF1424 o #FFFFFF
    verticalStretch: number; // 1.20 - 1.50 per USER_DESIGN_PREFERENCES
    tracking: number;   // Espaciado negativo
  };
  position: { x: number; y: number };
  featherPx: number;
  backgroundBlurPx: number; // Desenfoque sutil del fondo (0 - 40)
  inTimeSeconds: number;
  outTimeSeconds: number;
}

export interface MultiTakeCloneConfig {
  id: string;
  takes: Array<{
    takeId: string;
    assetPath: string;
    subjectZone: "LEFT" | "CENTER" | "RIGHT" | "CUSTOM";
    customSplitX?: number; // Punto de corte horizontal relativo
    inPointSeconds: number;
    durationSeconds: number;
    volumeDb: number;
  }>;
  masterBackgroundTakeId: string;
  edgeFeatherPx: number;
  totalDurationSeconds: number;
}
```

---

## 5. Salida ExtendScript para Adobe After Effects

El compilador de la Fase 19 genera sentencias nativas de After Effects para garantizar ejecución impecable:
1. **Creación de máscara Bezier en la capa superior:**
   ```javascript
   var myMask = fgLayer.property("Masks").addProperty("Mask");
   var myShape = myMask.property("maskShape").value;
   myShape.vertices = [[x1, y1], [x2, y2], ...];
   myShape.closed = true;
   myMask.property("maskShape").setValue(myShape);
   myMask.property("maskFeather").setValue([featherPx, featherPx]);
   ```
2. **Capa intermedia de texto centrada TIME Style:**
   ```javascript
   var textLayer = comp.layers.addText(config.text);
   textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
   textDoc.font = "Impact";
   ```
3. **Capa inferior con desenfoque de fondo:**
   ```javascript
   var blurFx = bgLayer.property("Effects").addProperty("ADBE Fast Blur");
   blurFx.property("Blurriness").setValue(blurPx);
   ```

---

## 6. Verificación de Calidad de 7 Capas Obligatoria

1. **Unit Tests:** Validación de parsing de bounding boxes, polígonos y cálculo de centroides.
2. **Invariant Tests:** Verificación inquebrantable de orden Z ($Z_{\text{bg}} < Z_{\text{txt}} < Z_{\text{fg}}$) y suma de alfas para clones.
3. **Mathematical Tests:** Algoritmo de punto en polígono (Ray Casting) y suavizado exponencial.
4. **Serialization Tests:** Schemas Zod y hashes SHA-256 de planes de composición.
5. **Property-Based Testing (`fast-check`):** Generación de coordenadas aleatorias comprobando que las máscaras nunca generan cotas NaN ni áreas negativas.
6. **Integration Tests:** Pipeline completo desde detección hasta generación JSX.
7. **Regression Tests:** Verificación de que los 1,432 tests existentes continúan en 100% verde sin perturbaciones.
