# Especificación Técnica: Fase 5B — Video Timeline & Multi-Track NLE

**Documento:** `spec/phase-5b-video-timeline.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulos:** `src/timeline/`

---

## 0. Propósito y Separación Arquitectónica

La **Fase 5B** implementa el motor de línea de tiempo no lineal (NLE) multi-pista. Establece la distinción formal entre:

```
Asset (archivo original)
  └── Element (instancia lógica de renderizado: texto, video, imagen, forma)
        └── Clip (aparición temporal en el timeline: [start, end), in/out, speed)
              └── Track (pista con orden z-index, mute, lock, solo)
                    └── Timeline (orquestador temporal global)
```

---

## 1. Modelo Temporal e Invariantes

### 1.1. Convención de Límites de Intervalo
Todo intervalo temporal se evalúa como **semicerrado $[start, end)$**:
- $t \ge start$ y $t < end$.
- Garantiza que dos clips adyacentes $[0, 5)$ y $[5, 10)$ tengan una transición limpia sin fotogramas duplicados ni lagunas en $t = 5$.

### 1.2. Mapeo de Tiempo Global a Tiempo Local y Fuente
Para un clip con `timelineRange = [t_start, t_end)` y `sourceRange = [s_start, s_end)` con velocidad `speed > 0`:
$$\text{localTime} = t_{\text{global}} - t_{\text{start}}$$
$$\text{sourceTime} = s_{\text{start}} + (\text{localTime} \cdot \text{speed})$$

### 1.3. Aislamiento de Animaciones y Efectos
Las animaciones y propiedades animables del elemento se evalúan respecto a $\text{localTime}$. Mover un clip de $t = 5\text{s}$ a $t = 20\text{s}$ no altera los keyframes internos de su animación de entrada ($0 \to 1\text{s}$).

---

## 2. Estructura de Clases y Tipos

### 2.1. `TimeRange`
```typescript
interface TimeRange {
  start: number;
  end: number;
  duration: number; // end - start
}
```

### 2.2. `Clip`
- `id`: Identificador único.
- `elementId`: ID del elemento gráfico/audiovisual asociado.
- `timelineRange`: `TimeRange` en tiempo global de composición.
- `sourceRange?`: `TimeRange` en el medio fuente original.
- `speed`: Factor de velocidad multiplicador (default $1.0$).
- Métodos: `isActive(time)`, `getLocalTime(time)`, `getSourceTime(time)`.

### 2.3. `Track`
- `id`: Identificador único.
- `name`: Nombre descriptivo.
- `type`: `"video" | "audio" | "graphics"`.
- `order`: Prioridad de composición / Z-Index (a mayor valor, se renderiza encima).
- `enabled`, `muted`, `locked`, `solo`, `opacity`.
- `clips`: Array ordenado de clips.

### 2.4. `Timeline`
- `timeBase`: `{ fps: number }`.
- `duration`: Duración total.
- `tracks`: Lista de pistas ordenadas.
- `markers`: Marcadores temporales (`id`, `time`, `label`, `color`).
- `evaluate(time)`: Función pura y determinista que retorna `TimelineState` sin mutar el proyecto.
- Operaciones NLE: `splitClip()`, `trimClip()`, `moveClip()`, `addTrack()`, `removeTrack()`.
