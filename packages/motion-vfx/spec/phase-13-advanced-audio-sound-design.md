# Especificación Técnica: Fase 13 — Advanced Audio & Sound Design Engine

**Documento:** `spec/phase-13-advanced-audio-sound-design.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulo:** `src/audio-design/`

---

## 0. Propósito y Principio Arquitectónico

La **Fase 13** implementa el motor avanzado de audio y diseño sonoro (*Sound Design Engine*), integrando análisis espectral/rítmico, atenuación inteligente (*Smart Ducking*), catálogo semántico de efectos de sonido (*SFX*), y un grafo unificado de sincronización audiovisual (*Audiovisual Sync Events*):

$$\text{Semantic Intent} \longrightarrow \text{SyncGroup} \longrightarrow \{\text{Voice, Music, SFX}\} \longrightarrow \text{Smart Ducking \& Bus Mixer} \longrightarrow \text{Master}$$

```
                           AI DIRECTIVE
                                │
                                ↓
                        SYNC EVENT GRAPH
         (Une Visual Impact + Camera Punch + SFX + Ducking)
                                │
        ┌───────────────────────┼───────────────────────┐
        ↓                       ↓                       ↓
    VOICE BUS               MUSIC BUS                SFX BUS
 (Speech / Normalizer)  (Smart Ducking Envelope)  (Semantic SFX Library)
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ↓
                          AUDIO MIX BUS
                     (Summing & Peak Limiter)
                                ↓
                              MASTER
```

---

## 1. Módulos y Capacidades Clave

### 1.1. Análisis de Audio y Detección de Ritmo (`AudioAnalysisEngine`)
- Detección de picos RMS, transientes, silencios e intervalos de voz (*speech regions*).
- Generación de rejilla de beats (*beat grid*) y cálculo de compases (*downbeats*).

### 1.2. Atenuación Inteligente de Música (`SmartDuckingEngine`)
- Atenuación automática de música durante segmentos de voz activa con transiciones suaves (*attack/release*).

### 1.3. Biblioteca Semántica de SFX (`SemanticSFXLibrary`)
- Búsqueda basada en intención (`intent`), energía (`energy`) y categoría (`whoosh`, `impact`, `pop`, `riser`, `glitch`).

### 1.4. Grafo de Sincronización Audiovisual (`SyncEventGraph`, `SoundDesignMacroEngine`)
- Creación de `SyncGroup` para coordinar de forma determinista eventos visuales y sonoros.
- Macros de diseño sonoro: `text-pop`, `social-hook`, `impact-reveal`.

### 1.5. Mezclador Multicanal y Limitador de Picos (`AudioMixBus`)
- Suma de buses con control de volumen, balance estéreo y limitador contra clipping.
