# Especificación Técnica: Fase 5I — Audio Intelligence & Beat Synchronization

**Documento:** `spec/phase-5i-audio-intelligence.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulo:** `src/audio-intelligence/`

---

## 0. Principio Arquitectónico

$$\text{Audio Analysis} \neq \text{Animation}$$

El análisis acústico no altera directamente propiedades gráficas; produce **datos y señales temporales deterministas**. El motor visual se vincula a estas señales a través de **`AudioSignal`**, **`AudioBinding`** y **`AudioTrigger`**:

```
                  AUDIO SOURCE
                       │
       ┌───────────────┼───────────────┐
       ↓               ↓               ↓
  Waveform & RMS    Frequency Bands   Beats & Onsets
       │               │               │
       └───────────────┼───────────────┘
                       ↓
               TEMPORAL SIGNALS
       (Attack/Release Envelope Follower)
                       ↓
         AUDIO REACTIVE PROPERTY BINDING
       (Linear, Ease, Threshold Mappings)
                       ↓
    VISUAL PROPERTIES (Scale, Camera, Glow, Cut)
```

---

## 1. Modelo de Datos y Señales (`AudioSignal`, `AudioEvent`)

### 1.1. Bandas de Frecuencia Configurables
- **`sub`:** $20 - 60\text{ Hz}$
- **`bass`:** $60 - 250\text{ Hz}$
- **`mid`:** $250 - 2000\text{ Hz}$
- **`high`:** $2000 - 8000\text{ Hz}$
- **`air`:** $8000 - 20000\text{ Hz}$

### 1.2. Seguidor de Envolvente Acústica (*Attack / Release Envelope*)
$$E(t) = \begin{cases} E(t-\Delta t) + \alpha_{attack} \cdot (x(t) - E(t-\Delta t)) & \text{si } x(t) > E(t-\Delta t) \\ E(t-\Delta t) + \alpha_{release} \cdot (x(t) - E(t-\Delta t)) & \text{si } x(t) \le E(t-\Delta t) \end{cases}$$
donde $\alpha = 1 - e^{-\Delta t / \tau}$.

---

## 2. Cuantización y Cuadrícula Rítmica (`Quantizer`, `BeatGrid`)

1. **`BeatGrid`:** Parámetros $\{ bpm, offset, subdivision \}$.
2. **`SnapMode`:** `none`, `beat`, `bar`, `subdivision`, `onset`, `word`.
3. **Cálculo de Compás (*MusicalBar*):** Agrupación en compases de 4 tiempos ($1\text{ bar} = 4\text{ beats}$).

---

## 3. Disparadores y Vinculación Reactiva (`AudioBinding`, `AudioTrigger`)

1. **`AudioBinding`:** Asocia una señal a una propiedad de capa con funciones de mapeo: `linear`, `clamp`, `exponential`, `logarithmic` y umbrales (*threshold*).
2. **`AudioTrigger`:** Reinicia animaciones o transiciones en eventos rítmicos (`beat`, `onset`, `word`) con tiempo de enfriamiento (*cooldown*).
