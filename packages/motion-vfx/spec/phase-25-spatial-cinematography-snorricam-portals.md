# Especificación Técnica: Fase 25 — Spatial Cinematography: Snorricam Body Lock, Infinite Zoom Portals & Parallax Occlusion Wipes

**Versión:** 1.0.0  
**Fecha:** 2026-09-05  
**Módulo:** `src/spatial-cinematography/`  
**Objetivo:** Implementar la primera fase de la Suite de Cinematografía de Vanguardia Auteur Elite, introduciendo tres técnicas visuales definitorias del cine musical contemporáneo (vistas en trabajos de Dave Free / Kendrick Lamar, Hiro Murai y Daniel Scheinert): cámara anclada al cuerpo (Snorricam), transiciones de agujero de gusano (Infinite Zoom Portals) y transiciones por oclusión de transeúntes (Parallax Occlusion Wipes).

---

## 1. Fundamentos Matemáticos y Físicos

### 1.1 Snorricam / Body-Rig Motion Locking
En un plano *Snorricam*, una cámara sujeta mecánicamente al torso o cabeza del artista mantiene su rostro $100\%$ inmóvil en el centro exacto de la pantalla mientras el mundo de fondo se desplaza violentamente:
- Dado un punto de rastreo del sujeto $\mathbf{P}_{\text{subject}}(t) = [X_s(t), Y_s(t)]$ y una orientación $\theta_s(t)$:
- Centro objetivo de la composición:
  $$\mathbf{C}_{\text{comp}} = \left[ \frac{W_{\text{comp}}}{2}, \; \frac{H_{\text{comp}}}{2} \right]$$
- El punto de anclaje de la capa se fija exactamente en el sujeto:
  $$\mathbf{A}_{\text{layer}}(t) = \mathbf{P}_{\text{subject}}(t)$$
- La posición de la capa se fija en el centro de pantalla:
  $$\mathbf{Pos}_{\text{layer}}(t) = \mathbf{C}_{\text{comp}}$$
- Rotación compensatoria inversa para cancelar giros de cabeza si se desea anclaje axial:
  $$\theta_{\text{comp}}(t) = -\theta_s(t)$$
- Compensación de escala por movimiento hacia la cámara (*scaling margin*):
  $$S_c \ge 100\% \cdot \max_{t} \left( \frac{\|\mathbf{P}_s(t) - \mathbf{C}_{\text{comp}}\|}{\min(W, H)} + 1 \right)$$
  para garantizar que el metraje nunca deje al descubierto los bordes de la composición (apoyado por `ADBE Motion2` / *Motion Tile* procedural).

### 1.2 Infinite Zoom Portal (Transición de Agujero de Gusano)
Un crash zoom continuo que se adentra exponencialmente en una Región de Interés (ROI) microscópica (la pupila del cantante, la lente de sus gafas, una cerradura, o un espejo retrovisor) y emerge en el siguiente plano:
- Intervalo de transición: $[t_{\text{start}}, t_{\text{end}}]$, con duración $\Delta t = t_{\text{end}} - t_{\text{start}}$.
- Progresión temporal normalizada: $\tau = \frac{t - t_{\text{start}}}{\Delta t} \in [0, 1]$.
- Modelo de escala super-exponencial:
  $$S(t) = S_{\text{base}} \cdot \exp\left( k \cdot \tau^\gamma \right)$$
  donde $k = \ln\left(\frac{S_{\text{max}}}{S_{\text{base}}}\right)$, con $S_{\text{max}} \ge 5000\%$ y exponente de aceleración $\gamma \in [2.5, 4.0]$.
- Trayectoria del punto de anclaje convergiendo hacia el centro del portal:
  $$\mathbf{A}(t) = \mathbf{A}_0 + (\mathbf{P}_{\text{roi}} - \mathbf{A}_0) \cdot \tau^2$$
- Apertura del plano de destino mediante máscara elíptica expansiva sincronizada o punch-through de luminancia en $\tau > 0.85$.

### 1.3 Parallax Occlusion Wipe (Wipe de Transeúnte / Poste de Hiro Murai)
Un elemento en primer plano (una persona caminando delante de cámara, una columna, un árbol) atraviesa el encuadre de izquierda a derecha o viceversa, dividiendo la pantalla:
- Borde de avance del oclusor en el tiempo:
  $$X_{\text{edge}}(t) = X_{\text{start}} + (X_{\text{end}} - X_{\text{start}}) \cdot f_{\text{ease}}\left( \frac{t - t_{\text{in}}}{\Delta t_{\text{wipe}}} \right)$$
- En la zona posterior al borde de avance, se proyecta la toma entrante (Escena B), mientras que la zona no ocluida mantiene la toma saliente (Escena A).
- Calado de máscara suave proporcional a la velocidad del oclusor ($W_{\text{feather}} \propto v_{\text{occluder}}$) para integrar el desenfoque de movimiento natural de la silueta.

---

## 2. Tipos y Esquemas de Datos (`src/spatial-cinematography/spatial-types.ts`)

```typescript
export interface SnorricamSpec {
  id: string;
  subjectAnchorPoint: [number, number]; // [X, Y] inicial del sujeto en la toma
  compensateRotation: boolean;
  stabilizationSmoothingFrames: number; // 0 = rigidez robótica absoluta, >0 = suavizado
  scaleBufferPercent: number; // Margen para evitar bordes negros (115% - 140%)
  motionTileMirror: boolean;
}

export interface InfiniteZoomPortalSpec {
  id: string;
  startTimeSeconds: number;
  durationSeconds: number;
  portalCenterPoint: [number, number]; // Coordenadas del punto hacia donde se colapsa la cámara
  maxScalePercent: number; // ej. 6000%
  accelerationExponent: number; // 3.0
  destinationSceneOpacityTrigger: number; // 0.85
}

export interface ParallaxOcclusionWipeSpec {
  id: string;
  startTimeSeconds: number;
  durationSeconds: number;
  direction: "LEFT_TO_RIGHT" | "RIGHT_TO_LEFT" | "TOP_TO_BOTTOM" | "BOTTOM_TO_TOP";
  featherPx: number; // 15 - 50 px
  curvatureDistortion: number; // 0.0 = línea recta, >0 = silueta curva orgánica
}

export interface SpatialCinematographyPlan {
  id: string;
  snorricam?: SnorricamSpec;
  portal?: InfiniteZoomPortalSpec;
  occlusionWipe?: ParallaxOcclusionWipeSpec;
  extendScriptLines: string[];
  checksumSha256: string;
}
```

---

## 3. Invariantes y Certificación

1. **Continuidad de Encuadre sin Huecos:** Todo desplazamiento Snorricam o Zoom Portal debe estar respaldado por escala aumentada o `ADBE Motion2` en modo espejo (`Mirror Edges = true`).
2. **Invariante de Motion Blur:** `comp.motionBlur = true` y `layer.motionBlur = true` en cada capa generada.
3. **Determinismo SHA-256:** Garantía criptográfica de idempotencia en la compilación ExtendScript.
