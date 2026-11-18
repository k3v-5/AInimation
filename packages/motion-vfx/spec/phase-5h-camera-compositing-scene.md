# Especificación Técnica: Fase 5H — Camera, Compositing & Scene System

**Documento:** `spec/phase-5h-camera-compositing-scene.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulos:** `src/scene/`, `src/camera/`, `src/compositing/`, `src/graph/`

---

## 0. Propósito y Separación Arquitectónica

La **Fase 5H** unifica todos los subsistemas anteriores (video, audio, tipografía, máscaras, tracking y efectos) dentro de un modelo de **Escena Cinemática con Cámara 2D/2.5D, Jerarquías de Capas y Grafo de Renderizado (DAG)**:

```
                    SCENE
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
   BACKGROUND      SUBJECT        TEXT (Kinetic)
        │             │             │
        │          TRACKING      ANIMATION
        │             │             │
        └─────────────┼─────────────┘
                      ↓
              CAMERA 2D / 2.5D
            (Zoom, Pan, Shake)
                      ↓
           RENDER GRAPH & COMPOSITING
         (Blend Modes, Alpha, DAG)
                      ↓
                 FRAME BUFFER
```

---

## 1. Modelo de Datos y Capas (`Scene`, `Layer`)

### 1.1. Capas y Jerarquías (`Layer`, `LayerType`)
- **`LayerType`:** `"video" | "image" | "text" | "shape" | "composition" | "particle" | "adjustment" | "controller"`.
- **`parentId` & `children`:** Propagación matricial de transformaciones relativas ($T_{world} = T_{parent} \cdot T_{local}$).
- **`Controller` (Null Layer):** Capa invisible utilizada para emparentar y controlar múltiples capas secundarias o la cámara.
- **`Adjustment Layer`:** Aplica su `EffectStack` al acumulador de píxeles resultante de todas las capas inferiores.

### 1.2. Modos de Fusión y Alfa (`BlendMode`, `AlphaMode`)
- **`BlendMode`:** `normal`, `multiply`, `screen`, `overlay`, `add`, `darken`, `lighten`.
- **`AlphaMode`:** `straight`, `premultiplied`.

---

## 2. Sistema de Cámara 2D / 2.5D (`Camera`)

1. **Parámetros de Cámara:** `position` $(x, y, z)$, `rotation` $(roll, pitch, yaw)$, `zoom` (escala $1.0\text{x}, 1.2\text{x}$), `focalLength`.
2. **Espacios de Coordenadas:**
   $$\text{World Space} \xrightarrow{T_{layer}} \text{Layer Space} \xrightarrow{V_{camera}} \text{Camera Space} \xrightarrow{P} \text{Screen Space}$$
3. **Modificadores Procedurales (`CameraModifier`):**
   - `CameraShake`: Simulación de cámara en mano con vibración determinista por semilla PRNG.
   - `PunchIn`: Zoom rápido hacia un punto de interés.
4. **Presets:** `subtle-zoom`, `punch-in`, `handheld-shake`, `dramatic-whip`.

---

## 3. Grafo de Renderizado (`RenderGraph`, `RenderNode`)

1. **Estructura DAG:** Nodos de entrada de medios, transformaciones, efectos y composición.
2. **Ordenación Topológica:** Detección estricta de ciclos (`GraphCycleError`) y evaluación paralela/secuencial determinista.
3. **Marcadores Semánticos de Escena (`SceneMarker`):**
   - Etiquetas para IA: `"HOOK"`, `"EMPHASIS"`, `"PUNCHLINE"`, `"CTA"`, `"BROLL"`.
