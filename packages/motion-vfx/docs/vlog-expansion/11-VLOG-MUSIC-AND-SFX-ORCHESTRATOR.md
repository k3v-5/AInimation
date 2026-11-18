# Vlog Music & SFX Orchestrator

**Documento:** `11-VLOG-MUSIC-AND-SFX-ORCHESTRATOR.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog & Multilingual Expansion  

---

## 1. Objetivo

Definir completamente el subsistema responsable de:
- música de fondo;
- selección de pistas;
- análisis BPM;
- detección de beats;
- sincronización musical;
- ducking automático;
- SFX;
- impactos;
- whooshes;
- pops;
- transiciones sonoras;
- cámara fotográfica;
- campanas/chimes;
- enfatización de palabras;
- sincronización con cortes;
- sincronización con overlays;
- sincronización con punch-ins;
- sincronización con mapas;
- sincronización con freeze-frames;
- prioridades de mezcla;
- normalización;
- protección contra clipping;
- exportación de audio;
- integración con After Effects.

El módulo deberá funcionar offline, ser determinista y reutilizar el `SoundBankManager` existente.

---

## 2. Principio Arquitectónico

El audio deberá procesarse como una composición temporal independiente de After Effects.

$$\text{Audio Sources} \longrightarrow \text{Asset Analysis} \longrightarrow \text{Voice Detection} \longrightarrow \text{Music Analysis} \longrightarrow \text{Beat/Transient Det} \longrightarrow \text{Event Timeline} \longrightarrow \text{SFX Selection} \longrightarrow \text{Ducking} \longrightarrow \text{Mixing} \longrightarrow \text{Peak/Loudness} \longrightarrow \text{Manifest} \longrightarrow \text{AE JSX}$$

After Effects será consumidor del resultado, no responsable de tomar decisiones de mezcla.

---

## 3. Fuentes de Audio

```typescript
type AudioSourceType =
  | "VOICE"
  | "MUSIC"
  | "SFX"
  | "AMBIENCE"
  | "ORIGINAL_CAMERA_AUDIO";
```

---

## 4. Audio Asset

```typescript
interface AudioAsset {
  id: string;
  path: string;
  type: AudioSourceType;
  duration: number;
  sampleRate: number;
  channels: number;
  format: string;
  metadata?: AudioMetadata;
}
```

---

## 5. Formato Interno

El pipeline deberá utilizar como formato de referencia:
$$\text{PCM, 16-bit, 44.1 kHz, Mono o Stereo según fuente}$$
Cuando una fuente utilice otro formato, deberá normalizarse antes del análisis.

---

## 6. Voice Track

```typescript
interface VoiceTrack {
  id: string;
  assetId: string;
  language?: SupportedLanguage;
  start: number;
  end: number;
}
```

---

## 7. Music Track

```typescript
interface MusicTrack {
  id: string;
  assetId: string;
  bpm?: number;
  key?: string;
  energy?: number;
  start: number;
  end: number;
  gain: number;
}
```

---

## 8. SFX Event

```typescript
interface SFXEvent {
  id: string;
  assetId: string;
  type: SFXType;
  time: number;
  gain: number;
  pan?: number;
  pitch?: number;
}
```

---

## 9. SFX Types

```typescript
type SFXType =
  | "WHOOSH"
  | "IMPACT"
  | "POP"
  | "SHUTTER"
  | "CHIME"
  | "RISER"
  | "DOWNER"
  | "GLITCH"
  | "SWIPE"
  | "CAMERA_CLICK";
```

---

## 10. Existing Procedural SFX

El módulo deberá reutilizar:
- `whoosh_fast.wav`
- `impact_sub_boom.wav`
- `ui_pop_click.wav`
- `camera_shutter.wav`
- `bell_chime.wav`
No deberá generar duplicados innecesarios.

---

## 11. Procedural SFX

Si un SFX no existe:
$$\text{SFX Request} \longrightarrow \text{SoundBankManager} \longrightarrow \text{Deterministic Synthesis} \longrightarrow \text{WAV PCM}$$

---

## 12. Determinism

Toda generación procedural deberá utilizar `seed` cuando exista cualquier componente variable.

---

## 13. No Random Audio

No utilizar `Math.random()` para pitch, gain, timing, selección o duración.

---

## 14. Music Selection

La selección musical podrá basarse en: `energy`, `BPM`, `duration`, `style`, `scene type`, `language`, `creator preset`.

---

## 15. Music Selection Score

$$\text{musicScore} = \text{styleMatch} \times 0.30 + \text{energyMatch} \times 0.25 + \text{bpmMatch} \times 0.20 + \text{durationFit} \times 0.15 + \text{sceneFit} \times 0.10$$
Los pesos deberán ser configurables.

---

## 16. Energy Scale

- $0.00 \longrightarrow$ ambient
- $0.25 \longrightarrow$ calm
- $0.50 \longrightarrow$ medium
- $0.75 \longrightarrow$ energetic
- $1.00 \longrightarrow$ extreme

---

## 17. Scene Energy

```typescript
interface SceneEnergy {
  start: number;
  end: number;
  value: number;
}
```

---

## 18. Music Energy Matching

El sistema deberá evitar música extremadamente energética durante explicaciones complejas, voz emocional, entrevistas o segmentos delicados.

---

## 19. BPM Detection

Si una pista no declara BPM, el sistema deberá detectarlo localmente:

```typescript
interface BPMAnalysis {
  bpm: number;
  confidence: number;
}
```

---

## 20. Beat Grid

```typescript
interface BeatGrid {
  bpm: number;
  beats: number[];
  bars?: number[];
}
```

---

## 21. Beat Alignment

Los eventos musicales podrán ajustarse al beat más cercano:
$$\text{eventTime} \longrightarrow \text{nearestBeat}$$

---

## 22. Snap Threshold

Por defecto $0.12\text{ s}$. Si el evento está más lejos del beat, no deberá moverse automáticamente.

---

## 23. Voice Priority

La voz siempre tendrá prioridad sobre música, ambientación y SFX no críticos.

---

## 24. Critical SFX

Algunos SFX podrán superar temporalmente la música, pero nunca deberán destruir la inteligibilidad de la voz.

---

## 25. Audio Priority

$$\text{VOICE} > \text{IMPORTANT DIALOGUE} > \text{CRITICAL SFX} > \text{MUSIC} > \text{AMBIENCE}$$

---

## 26. Ducking

```typescript
interface DuckingConfig {
  threshold: number;
  targetGain: number;
  attack: number;
  release: number;
}
```

---

## 27. Default Ducking

$$\text{targetGain} = -10\text{ dB}, \quad \text{attack} = 50\text{ ms}, \quad \text{release} = 250\text{ ms}$$

---

## 28. Voice Detection

El motor utilizará la envolvente RMS de la voz, sin depender exclusivamente de un threshold fijo.

---

## 29. Adaptive Voice Threshold

El threshold deberá adaptarse al nivel medio de la pista.

---

## 30. Ducking Curve

$$\text{normal} \longrightarrow \text{attack} \longrightarrow \text{ducked} \longrightarrow \text{release} \longrightarrow \text{normal}$$

---

## 31. No Pumping

El algoritmo deberá evitar modulaciones erráticas de volumen (*pumping*) ante micro-pausas.

---

## 32. Voice Pause Handling

Pausas inferiores a $0.30\text{ s}$ no deberán restaurar completamente la música.

---

## 33. Long Pause

Pausas mayores a $0.30\text{ s}$ podrán comenzar la fase de release.

---

## 34. Music Fade

Al terminar una pista: `fadeOut` para evitar cortes bruscos.

---

## 35. Default Fade

$$\text{fadeIn} = 300\text{ ms}, \quad \text{fadeOut} = 500\text{ ms}$$

---

## 36. Music Crossfade

Al cambiar de pista: pista A atenúa mientras pista B entra progresivamente.

---

## 37. Crossfade Default

Valor por defecto: $1.0\text{ s}$.

---

## 38. Hard Cut Music

Permitido únicamente ante cambios de capítulo, saltos drásticos de energía o efectos creativos explícitos.

---

## 39. SFX Event Generation

Los eventos podrán provenir de: `Timeline`, `Subtitle Engine`, `ViralMomentDetector`, `VlogJumpCutEngine`, `TravelOverlayEngine`, `DynamicPunchIn`, `Transition Engine`.

---

## 40. Cut SFX

Un corte podrá generar `WHOOSH`, `POP` o `IMPACT` dependiendo del estilo.

---

## 41. Punch-In SFX

Un punch-in del $115\%$ podrá generar `POP`, `WHOOSH` o `IMPACT` según intensidad.

---

## 42. Punch-In Intensity

$$\text{intensity} \in [0, 1]$$
dependiendo del cambio semántico, énfasis y energía.

---

## 43. Subtitle Emphasis SFX

Una palabra marcada con `emphasis = true` podrá producir un `POP` discreto (sin saturar todas las palabras).

---

## 44. SFX Density Limit

$$\text{maxSFXPerSecond} = 2$$

---

## 45. Anti-Spam

Si múltiples eventos ocurren simultáneamente, deberán agruparse o filtrarse por prioridad.

---

## 46. Event Priority

$$\text{critical transition} > \text{major emphasis} > \text{punch-in} > \text{subtitle emphasis} > \text{decorative}$$

---

## 47. SFX Collision

Dos SFX idénticos no deberán dispararse simultáneamente salvo override explícito.

---

## 48. Pitch Variation

Variación aleatoria controlada de $\pm 2\text{ semitonos}$ si el preset lo permite.

---

## 49. Gain Variation

Variación leve de $\pm 3\text{ dB}$ sobre el nivel base.

---

## 50. Pan

$$\text{pan} \in [-1, 1] \quad (-1 = \text{izq}, \; 0 = \text{centro}, \; 1 = \text{der})$$

---

## 51. Spatial SFX

Cálculo de pan según posición visual en pantalla.

---

## 52. Travel Vlog Shutter

`PolaroidFreezeFrame` activará `camera_shutter.wav` exactamente al congelar el fotograma.

---

## 53. Map Route Sound

El trazado de una ruta podrá acompañarse de `ui_pop_click.wav`.

---

## 54. Geo-Badge

La entrada de un Geo-Badge podrá generar `ui_pop_click.wav`.

---

## 55. Impact Moment

Un clímax viral podrá generar `impact_sub_boom.wav` si supera el umbral configurado.

---

## 56. Transition Mapping

```typescript
interface TransitionAudioMap {
  CUT?: SFXType;
  CROSSFADE?: SFXType;
  WHIP_PAN?: SFXType;
  FLASH?: SFXType;
  GLITCH?: SFXType;
  IMPACT?: SFXType;
}
```

---

## 57. Style Preset Integration

```typescript
interface AudioStyleProfile {
  musicEnergy: number;
  sfxDensity: number;
  preferredSFX: SFXType[];
  ducking: DuckingConfig;
}
```

---

## 58. Example — MrBeast

- `musicEnergy`: $0.85$
- `sfxDensity`: high
- `impactFrequency`: high
- `subtitlePop`: enabled

---

## 59. Example — Documentary

- `musicEnergy`: $0.45$
- `sfxDensity`: low
- `impactFrequency`: low
- `ducking`: strong

---

## 60. Example — Cinematic Travel

- `musicEnergy`: $0.55$
- `sfxDensity`: medium
- `ambience`: enabled
- `whipSFX`: enabled
- `shutter`: enabled

---

## 61. Ambient Audio

Soporte de pistas ambientales de fondo: calle, restaurante, naturaleza, multitud, transporte o room tone.

---

## 62. Original Camera Audio

Posibilidad de conservar `ORIGINAL_CAMERA_AUDIO` para realismo documental.

---

## 63. Original Audio Ducking

Si existe nueva locución, el audio original de cámara se atenúa en lugar de eliminarse por completo.

---

## 64. Ambience Ducking

Atenuación menor para la ambientación: $-4\text{ dB}$ durante el diálogo.

---

## 65. Voiceover vs Original Voice

La pista de doblaje/locución (`VOICEOVER`) tiene prioridad absoluta sobre la voz original.

---

## 66. Multilingual Tracks

Mezcla independiente por idioma: `MASTER_ES`, `MASTER_EN`, `MASTER_PT`, `MASTER_FR`, `MASTER_DE`.

---

## 67. Music Reuse

La pista musical puede compartirse entre idiomas cuando el montaje visual sea compatible.

---

## 68. Language Timing Adaptation

Si el idioma altera el timing, los cues musicales y eventos de SFX se recalculan sobre el timeline adaptado.

---

## 69. No Fixed SFX Timing

Los eventos se almacenan vinculados a hitos semánticos/narrativos, resolviendo los timestamps finales dinámicamente.

---

## 70. Semantic Audio Event

```typescript
interface SemanticAudioEvent {
  id: string;
  type: string;
  anchor:
    | { kind: "TIMELINE"; time: number }
    | { kind: "SUBTITLE_WORD"; wordId: string }
    | { kind: "SEGMENT"; segmentId: string }
    | { kind: "TRANSITION"; transitionId: string };
}
```

---

## 71. Event Resolution

$$\text{Semantic Event} \longrightarrow \text{Localized Timeline} \longrightarrow \text{Resolved Timestamp} \longrightarrow \text{SFX Event}$$

---

## 72. Audio Manifest

```typescript
interface AudioManifest {
  projectId: string;
  tracks: AudioTrackManifest[];
  events: SFXEvent[];
  duckingRegions: DuckingRegion[];
  masterSettings: MasterAudioSettings;
}
```

---

## 73. Ducking Region

```typescript
interface DuckingRegion {
  start: number;
  end: number;
  source: "VOICE" | "DIALOGUE" | "MANUAL";
  amountDb: number;
}
```

---

## 74. Master Audio Settings

```typescript
interface MasterAudioSettings {
  peakLimitDb: number;
  targetLoudnessLUFS: number;
  truePeakLimitDbTP: number;
}
```

---

## 75. Internal Peak Protection

$$\text{sample} \le +0.0\text{ dBFS} \quad (\text{cero clipping digital})$$

---

## 76. True Peak

Monitoreo de inter-sample peaks y True Peak cuando el analizador local esté disponible.

---

## 77. Limiter

Etapa final del bus de mezcla:
$$\text{Sources} \longrightarrow \text{Ducking} \longrightarrow \text{Mix} \longrightarrow \text{Limiter}$$

---

## 78. Limiter Ceiling

Techo de limitación por defecto: $-1.0\text{ dBTP}$.

---

## 79. Loudness Target

Objetivos configurables por plataforma (YouTube $-14\text{ LUFS}$, Shorts/Reels $-13\text{ LUFS}$).

---

## 80. Loudness Analysis

```typescript
interface LoudnessAnalysis {
  integratedLUFS: number;
  shortTermLUFS?: number;
  momentaryLUFS?: number;
  truePeak?: number;
}
```

---

## 81. Validation

Fallo bloqueante ante clipping crítico, archivo corrupto, sample rate incompatible o pistas faltantes.

---

## 82. Warning

Advertencias ante: `LOUDNESS_OUT_OF_TARGET`, `HIGH_TRUE_PEAK`, `LOW_AUDIO_LEVEL`, `EXCESSIVE_SFX_DENSITY`, `EXCESSIVE_DUCKING`, `MUSIC_MASKING_VOICE`.

---

## 83. Silence

El silencio deliberado está permitido; no normalizar forzadamente ruidos de fondo en pausas dramáticas.

---

## 84. Dramatic Silence

```typescript
interface SilenceCue {
  start: number;
  end: number;
  preserve: boolean;
}
```

---

## 85. Music Stop Cue

Corte total de música ($\text{gain} \to -\infty$) durante momentos de suspenso o sorpresa.

---

## 86. Riser

SFX de elevación (*risers*) previo a transiciones importantes, mapas o clímax.

---

## 87. Downer

SFX de relajación o caída (*downers*) tras momentos intensos o desenlaces.

---

## 88. Glitch Audio

Sonidos digitales de glitch acotados estrictamente en duración y densidad.

---

## 89. SFX Duration

Los efectos de sonido preservan su duración natural sin recortes abruptos salvo diseño intencional.

---

## 90. Time Stretch

Time-stretch transparente entre $0.90\text{x}$ y $1.10\text{x}$ cuando se requiera ajuste métrico.

---

## 91. Pitch Preservation

Preservación del tono original mediante algoritmos WSOLA / elastique al estirar audio vocal.

---

## 92. Voice Speed Range

Rango normal de stretch vocal: $[0.95\text{x}, 1.05\text{x}]$; fuera de ese margen se emite advertencia.

---

## 93. Beat-Safe Editing

Cortes musicales ajustados a compases o pulsos según el preset de edición.

---

## 94. Music Looping

Bucle musical en puntos armónicos estables con micro-crossfades para evitar saltos.

---

## 95. Loop Crossfade

Valor por defecto: $250\text{ ms}$.

---

## 96. Music Intro

Reserva de $1\text{ a }2\text{ compases}$ de música previa a la entrada de la locución.

---

## 97. Outro

Cierre natural con cola sonora (*tail*) de la pista en lugar de corte seco.

---

## 98. Chapter Transitions

Cambio de pista musical o acento con impacto sonoro en giros narrativos.

---

## 99. Audio Event Graph

Grafo formal de eventos de audio (`AudioEventGraph`) inspeccionable antes del render.

---

## 100. Dry Run

```bash
npm run vlog:audio -- --dry-run
```
emite `audio-manifest.json`, `audio-events.json` y `audio-validation.json`.

---

## 101. Debug

```bash
npm run vlog:audio -- --debug
```
muestra BPM, beat grid, zonas de ducking, SFX mapeados y niveles pico.

---

## 102. Preview

Representación previa de la mezcla sin necesidad de After Effects.

---

## 103. Reproducibility

Misma entrada genera idéntica selección musical, curva de ducking y niveles de mezcla.

---

## 104. Audio Hash

Identidad criptográfica SHA-256 de cada archivo de audio.

---

## 105. Asset Validation

Comprobación previa de existencia, legibilidad, duración y canales.

---

## 106. Missing Asset

Fallback procedural automático a través de `SoundBankManager` si falta un SFX.

---

## 107. Missing Music

Estrategias ante pista faltante: reintentar selección, fallback compatible o continuar sin música.

---

## 108. Offline Requirement

100% offline sin servicios en la nube para análisis o síntesis sonora.

---

## 109. External Libraries

Dependencias locales, reproducibles y documentadas.

---

## 110. Test Matrix

Matriz de pruebas: solo voz, voz + música, voz + música + SFX, voz + ambiente, multilingüe, diálogos rápidos/lentos, pausas largas, densidad alta de SFX, BPMs extremos y bucles musicales.

---

## 111. Property-Based Testing

Generar regiones aleatorias de voz, música y SFX verificando invariantes acústicas.

---

## 112. Audio Invariants

$$\text{gain} \ne \text{NaN}, \quad \text{gain} \ne \infty, \quad \text{duration} > 0, \quad \text{time} \ge 0$$

---

## 113. Gain Bounds

Límites de ganancia estables $[-60\text{ dB}, +12\text{ dB}]$.

---

## 114. Ducking Invariant

El ducking nunca puede subir el volumen de la música cuando entra la voz.

---

## 115. Voice Invariant

La voz nunca puede quedar accidentalmente silenciada por atenuaciones secundarias.

---

## 116. SFX Invariant

Un efecto de sonido decorativo defectuoso nunca detiene el render final.

---

## 117. Critical Error

Detienen la ejecución: `VOICE_TRACK_MISSING`, `MASTER_AUDIO_INVALID`, `OUTPUT_CORRUPTED`, `TIMELINE_INVALID`.

---

## 118. Integration With Subtitle Engine

Énfasis en palabras y cambios de tarjeta pueden activar disparadores sonoros discretos.

---

## 119. Integration With Jump Cut Engine

Cada corte de montaje puede activar un whoosh o corte musical sutil.

---

## 120. Integration With Punch-In

```typescript
interface PunchInAudioCue {
  punchInId: string;
  intensity: number;
}
```

---

## 121. Integration With Travel Overlays

Disparo de `camera_shutter.wav` en polaroids y clicks suaves en rutas/badges.

---

## 122. Integration With Viral Detector

Los momentos virales determinan elegibilidad de impactos graves y elevación de energía musical.

---

## 123. Integration With AE

Generación de capas de audio en After Effects con automatización de volumen y keyframes de ducking.

---

## 124. AE Layer Naming

$$\text{VLOG\_AUDIO\_<TYPE>\_<ID>}$$
Ejemplo: `VLOG_AUDIO_MUSIC_MAIN`, `VLOG_AUDIO_VOICE_ES-MX`, `VLOG_AUDIO_SFX_0042`.

---

## 125. AE Metadata

Conserva: `audioAssetId`, `audioEventId`, `language`, `sourceType`, `schemaVersion`.

---

## 126. JSX Safety

Rutas de archivo sanitizadas y escapadas antes de escribirse en código JSX.

---

## 127. Path Handling

Normalización multiplataforma de rutas para Windows, macOS y Linux.

---

## 128. Relative Paths

Uso prioritario de rutas relativas dentro de la estructura del proyecto.

---

## 129. Absolute Path Fallback

Rutas absolutas permitidas únicamente como fallback para la importación en After Effects.

---

## 130. Manifest Example

```json
{
  "projectId": "vlog_001",
  "language": "es-MX",
  "voiceTrack": "voice_es",
  "music": "travel_03",
  "events": [
    {
      "type": "SHUTTER",
      "time": 42.31
    }
  ]
}
```

---

## 131. Definition of Done

- [ ] AudioAsset definido
- [ ] VoiceTrack definido
- [ ] MusicTrack definido
- [ ] SFXEvent definido
- [ ] SFX types definidos
- [ ] Procedural SFX integrado
- [ ] Determinismo garantizado
- [ ] BPM analysis definido
- [ ] Beat grid definido
- [ ] Beat snapping definido
- [ ] Music selection definido
- [ ] Energy model definido
- [ ] Ducking definido
- [ ] Adaptive threshold definido
- [ ] Attack definido
- [ ] Release definido
- [ ] Anti-pumping definido
- [ ] Music fade definido
- [ ] Crossfade definido
- [ ] SFX mapping definido
- [ ] Punch-in integration definida
- [ ] Subtitle integration definida
- [ ] Travel overlay integration definida
- [ ] Viral detector integration definida
- [ ] Ambient audio definido
- [ ] Original audio definido
- [ ] Multilingual mix definido
- [ ] Time-stretch definido
- [ ] Pitch preservation definido
- [ ] Music looping definido
- [ ] Chapter transitions definidos
- [ ] Audio manifest definido
- [ ] Loudness analysis definido
- [ ] Peak protection definido
- [ ] Limiter definido
- [ ] Validation definido
- [ ] Error types definidos
- [ ] Warning types definidos
- [ ] Offline requirement definido
- [ ] Asset validation definido
- [ ] Missing asset fallback definido
- [ ] CLI definido
- [ ] Dry-run definido
- [ ] Debug definido
- [ ] Deterministic output definido
- [ ] Property tests definidos
- [ ] Integration tests definidos
- [ ] AE export definido
- [ ] AE metadata definido
- [ ] Path handling definido

---

## 132. Estado Final

**Documento:** `11-VLOG-MUSIC-AND-SFX-ORCHESTRATOR.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

El sistema de audio deberá considerarse un motor de orquestación semántica, no simplemente un mezclador. Los eventos deberán permanecer vinculados a su causa audiovisual para que puedan recalcularse automáticamente cuando cambie el idioma, el timing o el montaje.
