# Especificación Técnica: Fase 5D — Audio Engine & Mixing

**Documento:** `spec/phase-5d-audio-engine.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulos:** `src/audio/`

---

## 0. Propósito y Separación Arquitectónica

La **Fase 5D** construye el motor de audio profesional para mezcla, procesamiento dinámico, análisis rítmico y sincronización de eventos:

```
Audio Asset (archivo físico)
  └── AudioSource (proveedor de muestras decodificadas / sintéticas)
        └── AudioClip (instancia en timeline con in/out, speed, fades, volume, pan)
              └── AudioTrack (pista con ganancia, mute, solo, ducking)
                    └── AudioMixer ──► MasterBus (Limiter) ──► AudioBuffer
```

### Canal Paralelo de Análisis
```
AudioSource ──► AudioAnalyzer ──► [ Waveform, RMS Energy, Silence, Onsets, Beats ] ──► BeatMap
```

---

## 1. Modelo de Datos y Fórmulas Matemáticas

### 1.1. Conversiones de Ganancia y Decibeles
$$\text{gain} = 10^{\frac{\text{gainDb}}{20}}$$
$$\text{gainDb} = 20 \log_{10}(\text{gain})$$

### 1.2. Paneo Estéreo (Equal-Power Pan Rule)
Para $\text{pan} \in [-1, 1]$:
$$\theta = \frac{(\text{pan} + 1) \cdot \pi}{4}$$
$$L = \cos(\theta), \quad R = \sin(\theta)$$

### 1.3. Fades con Modulación de Easing
Para un fade de duración $D_{\text{fade}}$ y progreso relativo $\tau = \frac{t_{\text{rel}}}{D_{\text{fade}}}$:
$$\text{gain}_{\text{fadeIn}}(t) = \text{getEasing}(\text{easing})(\tau)$$
$$\text{gain}_{\text{fadeOut}}(t) = \text{getEasing}(\text{easing})(1 - \tau)$$

### 1.4. Auto-Ducking (Atenuación Automática de Música)
Cuando una pista de voz supera el umbral de actividad de energía RMS, la pista de música reduce su ganancia en $-\Delta\text{ dB}$ (ej. $-8\text{ dB}$) con rampas de suavizado (*attack / release*).

### 1.5. Detección de Onsets y Beats
Calcula la derivada de energía de la señal en ventanas de tiempo consecutivas $W_k$:
$$\text{RMS}_k = \sqrt{\frac{1}{N} \sum_{n=0}^{N-1} x_k[n]^2}$$
Un **Onset / Beat** se detecta cuando $\text{RMS}_k - \text{RMS}_{k-1} > \text{threshold}$ y supera la media móvil local de energía.

---

## 2. Estructura de Clases y Tipos

1. **`AudioBuffer`**: `{ sampleRate, channels, frames, data: Float32Array[] }`.
2. **`AudioClip`**: Clip temporal con `timelineRange`, `sourceRange`, `speed`, `volume`, `gainDb`, `pan`, `fadeIn`, `fadeOut`.
3. **`AudioTrack`**: Pista de audio con `gainDb`, `pan`, `muted`, `solo`, `ducking`.
4. **`AudioMixer`**: Mezclador multi-pista determinista con protección contra clipping y Master Bus limiter.
5. **`AudioAnalyzer`**: Extractor de `Waveform`, `RMS`, `SilenceIntervals`, `BeatMap` y `AudioEvents`.
