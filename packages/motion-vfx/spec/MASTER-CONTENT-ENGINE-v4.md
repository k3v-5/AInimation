# 📜 MASTER CONTENT ENGINE v4.0: ESPECIFICACIÓN ARQUITECTÓNICA Y CONCEPTUAL
## AI-Assisted Professional Content Finishing & Editorial Engine

**Proyecto:** `after-effects-mcp`  
**Estado:** `ESPECIFICACIÓN MAESTRA v4.0.0 (DRAFT / APROBACIÓN)`  
**Baseline:** `v3.5.0 Gold Master (884 tests GREEN)`  
**Filosofía Central:** Declarativo • Determinista • Offline-First • Zero API Cost • Explicable • No Destructivo  

---

## 1. Declaración de Misión y Salto de Paradigma

La suite `after-effects-mcp` v3.5.0 alcanzó la certificación **Gold Master** resolviendo con rigor matemático y determinismo el pipeline físico-audiovisual completo:
$$\text{Ingesta} \longrightarrow \text{Jump Cuts} \longrightarrow \text{TTS Offline} \longrightarrow \text{Adaptive Pacing} \longrightarrow \text{Karaoke Subtitles} \longrightarrow \text{Overlays} \longrightarrow \text{Audio Ducking} \longrightarrow \text{AE JSX Exporter}$$

El objetivo de la **Versión 4.0** no es añadir más plugins o efectos aislados, sino transformar el motor de un *automatizador de vlogs* en un:
$$\mathbf{Compilador\ Audiovisual\ Declarativo\ y\ Motor\ de\ Inteligencia\ Editorial}$$

El sistema deja de aplicar una receta rígida para convertirse en un **asistente de dirección y postproducción consciente del formato, intención y género**.

---

## 2. Auditoría Arquitectónica del Baseline v3.5.0 (M1–M9)

Para construir la v4.0 sin romper ninguno de los **884 tests existentes**, se audita qué componentes ya son genéricos y cuáles presentan acoplamiento léxico o semántico a "vlog":

| Componente Actual | Estado de Acoplamiento | Diagnóstico Técnico | Estrategia v4.0 |
|---|---|---|---|
| `contracts/` (Zod schemas) | **85% Genérico / 15% Acoplado** | Tipos como `VoiceoverTrack`, `DuckingEnvelope`, `PacingResult` son 100% universales. `VlogPhase` y `VlogOverlayItem` tienen prefijos específicos. | Preservar intactos para retrocompatibilidad; introducir `EditorialProfile` y `ContentIntent` como superconjunto. |
| `VlogMediaIngestionEngine` (M2) | **100% Genérico** | Extrae hashes SHA-256, metadatos y duraciones reales $O(1)$. | Reutilizar directamente como base de `AssetIntelligence 2.0`. |
| `VlogFootageClassifier` (M2) | **70% Genérico** | Clasifica `A_ROLL`, `B_ROLL`, etc. Le faltan roles documentales (`INTERVIEW`, `ARCHIVE`, `DOCUMENT`). | Extender la taxonomía sin alterar las etiquetas base. |
| `VlogJumpCutEngine` (M3) | **60% Genérico / 40% Acoplado** | Elimina silencios $>0.25\text{s}$ sin distinguir pausas dramáticas. | Subordinar a `SilenceIntelligenceEngine`: si el perfil marca `DRAMATIC_PAUSE`, no podar. |
| `DynamicPunchIn` (M3) | **90% Genérico** | Aplica escala al 115% y centra en ancla visual. Invariante `B-Roll > Punch-In` probado. | Subordinar a `ShotGrammar`: prohibir en documentales sobrios, permitir en vlogs/ensayos. |
| `MultilingualVoiceoverEngine` (M4) | **100% Genérico** | Soporte offline para los 7 locales oficiales con WAV canónico y caché determinista. | Reutilizar directamente como motor vocal multilingüe universal. |
| `VlogAdaptivePacingEngine` (M5) | **95% Genérico** | Retiming elástico (`TRIM`, `EXTEND`, `HOLD`, `SLOW_DOWN`) y stretch vocal $[0.95, 1.05]$. | Conectar a la `NarrativeEnergyCurve` para modular la cadencia temporal. |
| `VlogSubtitleEngine` (M6) | **95% Genérico** | Generador de karaoke palabra por palabra y wrapping por aspect ratio. | Reutilizar; añadir perfiles tipográficos (News Ticker, Doc Lower-Third, Corporate). |
| `VlogTravelOverlayEngine` (M6) | **40% Específico de Viajes** | Haversine y Polaroid son geniales pero específicos de travel/vlog. | Generalizar a `MotionGraphicsOverlayEngine` (Lower Thirds, Mapas, Gráficos de Datos, Citas). |
| `VlogAudioMixer` (M7) | **90% Genérico** | 4 buses jerárquicos y auto-ducking con anti-pumping a 44.1 kHz Stereo. | Incorporar `J-Cut / L-Cut Engine` y `RoomToneMatching`. |
| `VlogAfterEffectsExporter` (M7) | **95% Genérico** | Compilador ExtendScript JSX limpio con `comp.motionBlur = true` y Undo groups. | Mantener como Backend AE primario; diseñar interfaz para OTIO / FCPXML. |
| `VlogProductionOrchestrator` (M8) | **75% Genérico** | FSM de 22 fases y registro inmutable de artefactos. Flujo lineal fijado para vlog. | Parametrizar las fases mediante el `EditorialProfile` seleccionado. |

---

## 3. Taxonomía de Content Profiles (10 Perfiles Canónicos)

Cada perfil define una **gramática de montaje** con prioridades y restricciones explícitas:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CONTENT PROFILES                                      │
├───────────────────┬─────────────────────────────────────────────────────────────────────┤
│ 1. VLOG           │ Ritmo rápido, Jump cuts, Punch-ins, B-roll frecuente, Subtítulos    │
│ 2. DOCUMENTARY    │ Pacing pausado, Entrevistas, Evidencias, Archivo, Mapas, J/L Cuts   │
│ 3. JOURNALISM     │ Verificación de hechos, Citas en pantalla, Ticker, Atribución       │
│ 4. EDUCATIONAL    │ Diagramas, Callouts, Highlight de términos, Retención conceptual    │
│ 5. INTERVIEW      │ Multi-cámara, Speaker tracking, Eye-line continuity, Soundbites     │
│ 6. NEWS           │ Breaking-news layout, Lower-thirds sobrios, Cronología estricta     │
│ 7. CINEMATIC      │ Composición de planos, Continuidad de eje 180°, Curva emocional     │
│ 8. CORPORATE      │ Brand kit, Tipografía institucional, Testimonios formales           │
│ 9. SHORT-FORM     │ 9:16 vertical, Safe zones, Hook en <3s, Retención agresiva          │
│ 10. TECHNICAL     │ Precisión terminológica, Unidades, Demostraciones, Datos métricos   │
└───────────────────┴─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Las 12 Capacidades Editoriales de la v4.0

### 4.1. Production Intent Engine (`src/editorial/intent/`)
Antes de procesar un solo fotograma, el proyecto declara su propósito:
```typescript
export interface ProductionIntent {
  format: "VLOG" | "DOCUMENTARY" | "JOURNALISM" | "EDUCATIONAL" | "INTERVIEW" | "NEWS" | "CINEMATIC" | "CORPORATE" | "SHORT_FORM" | "TECHNICAL" | "AUTO";
  targetDurationSeconds?: number;
  primaryObjective: "INFORM" | "ENTERTAIN" | "PERSUADE" | "TEACH" | "EMOTE";
  pacingPreference: "CONTEMPLATIVE" | "MODERATE" | "AGGRESSIVE" | "DYNAMIC_WAVE";
  visualDensity: number; // 0.0 (minimalista) a 1.0 (ultra-denso)
  primaryPlatform: "YOUTUBE_16x9" | "VERTICAL_SOCIAL" | "BROADCAST" | "CINEMA";
}
```

### 4.2. Editorial Intelligence Engine (`src/editorial/director/`)
Evalúa cada plano según una métrica multidimensional auditable:
$$\text{EditorialScore} = w_1 \cdot \text{NarrativeValue} + w_2 \cdot \text{EmotionalValue} + w_3 \cdot \text{InformationValue} - w_4 \cdot \text{Redundancy} + w_5 \cdot \text{Continuity}$$
* Emite `EditorialDecisionNode`: no solo qué se corta, sino el **por qué**, la confianza y el efecto narrativo.

### 4.3. Visual Continuity Engine (`src/editorial/continuity/`)
Audita el montaje contra las reglas fundamentales del lenguaje cinematográfico:
* **Ley del Eje ($180^\circ$):** Detecta saltos de cámara que invierten la posición espacial relativa de los sujetos.
* **Dirección de Pantalla (Screen Direction):** Si el sujeto se mueve hacia la derecha en Plano A, no puede aparecer moviéndose a la izquierda en Plano B sin un plano neutro intermedio.
* **Continuidad Cromática:** Alerta de saltos térmicos ($|\Delta T| > 800\text{K}$) entre planos contiguos de la misma escena.

### 4.4. Semantic B-Roll Director 2.0 (`src/editorial/broll/`)
Evolución de la coincidencia simple a storytelling semántico:
* Puntuación de relevancia por concepto, acción y emoción.
* **Penalización de Repetición:** Si un plano o familia de metraje ya fue utilizado, su puntuación cae exponencialmente para evitar clichés.

### 4.5. Documentary Narrative Arc Engine (`src/editorial/narrative/`)
Modela la estructura formal de un documental en 10 beats canónicos:
$$\text{HOOK} \to \text{CONTEXT} \to \text{QUESTION} \to \text{EVIDENCE} \to \text{TESTIMONY} \to \text{CONFLICT} \to \text{ESCALATION} \to \text{REVELATION} \to \text{RESOLUTION} \to \text{REFLECTION}$$
* Alerta de desbalance narrativo si falta evidencia o si el contexto es desproporcionado respecto al conflicto.

### 4.6. Multi-Camera Director (`src/editorial/multicam/`)
Para entrevistas y podcasts con 2 o más cámaras:
* Detección activa de hablante (*speaker tracking*).
* Regla editorial: prohibido cortar a plano medio idéntico; prohibido cortar en medio de una confesión emocional íntima.

### 4.7. Silence Intelligence Engine (`src/editorial/silence/`)
Clasificación semántica de pausas antes de aplicar corte:
* `FILLER_SILENCE`: Silencio muerto / vacilación $\longrightarrow$ **Podar**.
* `BREATH`: Respiración natural $\longrightarrow$ **Preservar**.
* `THINKING_PAUSE`: Sujeto reflexionando $\longrightarrow$ **Preservar con Room Tone**.
* `DRAMATIC_PAUSE`: Tensión o revelación clave $\longrightarrow$ **INTOCABLE**.

### 4.8. Sound Design & Acoustic Continuity (`src/editorial/sound/`)
* **J-Cuts y L-Cuts Automáticos:** El audio de la siguiente escena entra $0.3\text{--}0.6\text{s}$ antes del corte visual, o el diálogo anterior se extiende sobre el B-Roll.
* **Room Tone Matching:** Detecta saltos en el suelo de ruido entre planos y aplica parches acústicos para evitar silencios digitales artificiales.

### 4.9. Fact & Evidence Layer (`src/editorial/evidence/`)
* Clasificación ontológica de declaraciones: `HECHO` vs `OPINIÓN` vs `TESTIMONIO`.
* Asociación obligatoria de afirmaciones críticas con metraje de archivo, citas textuales o documentos en pantalla.

### 4.10. Multi-Version & Version-Aware Engine (`src/editorial/versions/`)
Del mismo grafo editorial maestro derivan múltiples piezas con estrategias diferentes:
* **Master 16:9 (40 min):** Ritmo reflexivo y contexto profundo.
* **YouTube 16:9 (12 min):** Hook rápido, condensación de evidencia.
* **Vertical 9:16 (45 s):** Sustitución de planos generales por primeros planos legibles en móvil.

### 4.11. Editorial Quality Assurance (QA) Engine (`src/editorial/qa/`)
Auditoría multidimensional previa a la exportación:
* **Technical QC:** Clipping, silencios corruptos, frame rate, safe zones.
* **Editorial QC:** Repetición visual, saltos de eje, densidad de subtítulos, inteligibilidad.
* Emite un `EditorialQAReport` formal con scoring numérico ($0\text{--}100$).

### 4.12. Editorial Explainability & Human-in-the-Loop (`src/editorial/explain/`)
* Cada decisión almacena sus causas, confianza y alternativas rechazadas.
* Tres modos de control: `AUTO` (decide el motor), `SUGGEST` (propone para revisión), `LOCKED_BY_EDITOR` (el montador humano manda y el motor construye alrededor).

---

## 5. Arquitectura del Compilador Audiovisual

```
SOURCE MEDIA ──► [FRONTEND: Ingest + Metadata + NLP] ──► Editorial IR
                                                             │
                                                             ▼
                                                    [OPTIMIZATION PASSES]
                                                    • RedundancyPass
                                                    • ContinuityPass
                                                    • PacingCurvePass
                                                    • SoundDesignPass
                                                             │
                                                             ▼
                                                    [DECISION GRAPH: EDG]
                                                             │
                                                             ▼
                                                    [BACKEND CODE GENERATOR]
                                                    ├── After Effects JSX
                                                    ├── OpenTimelineIO (Resolve)
                                                    └── FCPXML (Premiere / FCP)
```

---

## 6. Plan de Implementación por Fases (Fases 4A a 4E)

```yaml
Fase 4A: Editorial Core & Multi-Format Profiles
  - EditorialProfileSchema & 10 Perfiles Canónicos
  - ProductionIntentSchema
  - EditorialDecisionGraph & Explainability
  - SilenceIntelligenceEngine (Dramatic vs Filler vs Room Tone)

Fase 4B: Visual & Acoustic Continuity
  - VisualContinuityEngine (Eje 180°, eyeline, saltos de escala)
  - SemanticBRollDirector 2.0 (scoring conceptual + anti-repetición)
  - SoundDesignEngine (J-Cuts, L-Cuts, Room Tone matching)
  - MultiCameraDirector (Switching de entrevistas)

Fase 4C: Documentary & Narrative Intelligence
  - NarrativeArcEngine (10 beats documentales)
  - Fact & Evidence Layer (Citas, documentos, atribuciones)
  - ArchivalMediaEngine (Tratamientos de archivo, Ken Burns, date stamps)

Fase 4D: Multi-Version Engine & Version-Aware Delivery
  - MultiVersionEngine (Master 16:9, YouTube, Shorts 9:16, Trailers)
  - Version-aware shot substitution (primer plano en vertical en lugar de crop ciego)
  - EditorialTransactions & Diff Engine (Commit, Rollback, Branching)

Fase 4E: Professional QA & Render-Agnostic Export
  - EditorialQualityAssuranceEngine (Scoring 0-100, warnings, checklist)
  - RenderValidation & Golden Render Testing
  - OpenTimelineIO (OTIO) Backend Bridge (Resolve / Premiere)
```

---

## 7. Invariantes Absolutos de la v4.0

1. **Blindaje del Baseline:** Los **884 tests** de la suite v3.5.0 deben permanecer **100% en verde** en todo momento. Ninguna adición editorial puede romper la compatibilidad con los proyectos existentes.
2. **AI Guardrails:** Ningún modelo de IA (LLM o visión) podrá modificar directamente el timeline. Toda propuesta pasa por validación estricta de esquemas Zod y es ejecutada por el planificador determinista.
3. **Determinismo:** Mismos assets + Mismo intent + Mismo perfil $\implies$ Idéntico resultado, byte por byte, con hashes inmutables.
4. **Offline-First:** Cero servicios externos obligatorios, cero telemetría invasiva, cero costos ocultos por minuto de video.

---

## 8. Matriz Formal de Requerimientos (REQ-001 a REQ-040)

### 8.1. Intención y Perfiles
- **REQ-001 — Motor agnóstico al tipo de contenido:** El sistema NO DEBE asumir que el contenido es un vlog. Debe soportar VLOG, DOCUMENTARY, JOURNALISM, EDUCATIONAL, INTERVIEW, NEWS, CINEMATIC, CORPORATE, SHORT_FORM y TECHNICAL. El tipo de contenido es un `EditorialProfile`, no código hardcodeado.
- **REQ-002 — Declaración de intención editorial:** Toda producción comienza con un `ProductionIntent` tipado (formato, objetivo: INFORM, EMOTE, PERSUADE, ENTERTAIN, DOCUMENT, EDUCATE; audiencia, plataforma, duración objetivo, idioma, tono, prioridad de ritmo vs emoción).
- **REQ-003 — Editorial Intelligence Engine:** Análisis multidimensional de cada segmento (Narrative, Emotional, Information, Visual, Audio, Redundancy, Continuity, Evidence, Transition) produciendo un `EditorialScore`.

### 8.2. Gramática Visual y Continuidad
- **REQ-004 — Shot Intelligence:** Clasificación automática de planos (WIDE, MEDIUM, CLOSE_UP, EXTREME_CLOSE_UP, OVER_SHOULDER, POV, ESTABLISHING, DETAIL, INSERT, CUTAWAY, ARCHIVAL, SCREEN_CAPTURE, DRONE, TALKING_HEAD) con sujeto, movimiento, escala y composición.
- **REQ-005 — Shot Grammar:** Comprensión de sintaxis cinematográfica (WIDE $\to$ MEDIUM $\to$ CLOSE, CLOSE $\to$ CLOSE como jump cut a justificar, regla de 180°, screen direction, eyeline, shot/reverse-shot; acciones: ALLOW, REPAIR, REPLACE, WARN, BLOCK).
- **REQ-017 — Visual Continuity Engine 2.0:** Detección de saltos de eje, inversiones de screen direction y disparidad cromática produciendo `CONTINUITY_SCORE` y sugerencias de plano puente.
- **REQ-018 — Color Continuity:** Detección de desajustes térmicos ($\Delta\text{K}$), exposición, contraste, balance de blancos y tonos de piel con correcciones relativas declarativas.

### 8.3. Inteligencia de Audio y Silencio
- **REQ-006 — Silence Intelligence 2.0:** Clasificación de pausas (FILLER, BREATH, THINKING, DRAMATIC, ROOM_TONE, EDITING_GAP, NATURAL_PAUSE). Los silencios de pensamiento y tensión dramática se conservan; los fillers se podan.
- **REQ-019 — Audio Intelligence 2.0:** 8 buses jerárquicos (VOICE, DIALOGUE, MUSIC, AMBIENCE, ROOM_TONE, SFX, CRITICAL_SFX, ARCHIVE_AUDIO) con loudness targets, control de True Peak, detección de clipping y matching de room tone.
- **REQ-020 — J-Cut / L-Cut Intelligence:** Transiciones de audio adelantadas/retrasadas guiadas por narrativa (KEEP AUDIO, BRIDGE AUDIO, HARD CUT, ROOM TONE BRIDGE).
- **REQ-021 — Music Intelligence:** Análisis musical por BPM, tonalidad, energía, crescendo, drops y sincronización de cortes y acentos narrativos.

### 8.4. Ritmo y Emoción
- **REQ-007 — Editorial Rhythm Engine:** Curva de ritmo continua modulando palabras/min, cortes/min, densidad visual y sonora (LOW $\to$ MEDIUM $\to$ HIGH $\to$ PEAK $\to$ RELEASE).
- **REQ-022 — Emotional Arc Engine:** Curva de emoción(t) (CALM, CURIOUS, TENSE, JOYFUL, SAD, FEAR, HOPE, TRIUMPH, REFLECTION) y detección de contradicciones emocionales (ej. tragedia con música alegre).
- **REQ-023 — Information Density Engine:** Detección y prevención de sobrecarga cognitiva (conceptos/segundo), sugiriendo pausas o simplificación de subtítulos.

### 8.5. Documental, Periodismo y Evidencia
- **REQ-008 — Documentary Narrative Engine:** Estructura narrativa documental en 10 beats (HOOK $\to$ CONTEXT $\to$ QUESTION $\to$ EVIDENCE $\to$ TESTIMONY $\to$ CONFLICT $\to$ ESCALATION $\to$ REVELATION $\to$ RESOLUTION $\to$ REFLECTION).
- **REQ-009 — Evidence Graph:** Grafo de afirmaciones (`Claim`) asociadas con fuentes, hablante, documentos, citas, archivo y nivel de certeza/confianza.
- **REQ-010 — Fact Checking Layer:** Detección de entidades numéricas, fechas, nombres y porcentajes marcando VERIFIED, UNVERIFIED, CONTRADICTED o MISSING_SOURCE sin inventar datos.
- **REQ-016 — Archive Intelligence:** Metadatos históricos de archivo (año, fuente, licencia) con tratamientos visuales diferenciados (Ken Burns, date stamps).

### 8.6. Entrevistas y Hablantes
- **REQ-011 — Multi-Camera Director:** Conmutación inteligente de ángulos (CAM A, B, C, Wide, Reaction) respetando el eje de 180° y prohibiendo cortes en declaraciones emocionales clave.
- **REQ-012 — Speaker Intelligence:** Identidad estable de hablantes (voz, rostro, rol narrativo: Interviewer, Guest, Narrator, Expert, Witness).

### 8.7. B-Roll y Metáforas Visuales
- **REQ-013 — Semantic B-Roll Director 2.0:** Coincidencia por concepto y emoción con diversidad de planos y penalización de clichés.
- **REQ-014 — B-Roll Repetition Intelligence:** Detección y penalización estricta de planos, ubicaciones o composiciones repetidas.
- **REQ-015 — Visual Metaphor Engine:** Sugerencia y clasificación explícita de metáforas (DIRECT EVIDENCE vs ILLUSTRATIVE vs METAPHORICAL).

### 8.8. Gráficos y Visualización de Datos
- **REQ-024 — Graphics Intelligence:** Títulos, lower thirds, mapas, timelines y diagramas integrados en el Editorial IR.
- **REQ-025 — Data Visualization Engine:** Conversión declarativa de CSV/JSON a barras, líneas, timelines y tarjetas estadísticas animadas.

### 8.9. Multi-Versión, Reframing y Trailers
- **REQ-026 — Multi-Version Engine:** Generación de Master 16:9, YouTube, Shorts, Reels, TikTok y Trailers con decisiones de montaje independientes derivadas del mismo grafo.
- **REQ-027 — Smart Reframing:** Sustitución inteligente de planos generales por primeros planos en vertical 9:16 en lugar de crops destructivos.
- **REQ-028 — Trailer Generator:** Extracción de mejores frases, revelaciones y ganchos para teasers y trailers de 15s, 30s, 60s y 90s.
- **REQ-029 — Social Hook Intelligence:** Scoring de los primeros 3 a 6 segundos para retención en redes sociales.

### 8.10. Control Editorial, Explicabilidad y Arquitectura IR
- **REQ-030 — Editorial QA:** Linter audiovisual integral produciendo scores (0–100) y clasificando hallazgos en BLOCKING, WARNING y SUGGESTION.
- **REQ-031 — Human-in-the-Loop:** Modos de autoridad AUTO, SUGGEST y LOCKED con registro inmutable de decisiones.
- **REQ-032 — Editorial Explainability:** Cada corte y selección expone su causa, regla editorial, confianza y alternativas evaluadas.
- **REQ-033 — Confidence-Aware Editing:** Umbrales configurables (ej. $>0.90 \to \text{AUTO}$, $0.70\text{--}0.90 \to \text{SUGGEST}$, $<0.70 \to \text{HUMAN\_REVIEW}$).
- **REQ-034 — Reversible Editorial IR:** La Representación Intermedia Editorial es la única fuente de verdad, totalmente desacoplada de los renderizadores.
- **REQ-035 — Compiler Passes:** Pipeline de transformación de pases deterministas ($IR \to IR$).
- **REQ-036 — Backend Independence:** Soporte de compilación a After Effects JSX, OpenTimelineIO (OTIO), FCPXML y FFmpeg.

### 8.11. Verificación, Regresión y Producción
- **REQ-037 — Render Verification:** Inspección visual de renders detectando frames negros, congelamientos, clipping o subtítulos cortados.
- **REQ-038 — Golden Master Regression:** Comparación determinista contra fixtures y hashes esperados.
- **REQ-039 — Performance Budget:** Presupuestos de tiempo de CPU y memoria por pase del compilador.
- **REQ-040 — Production Manifest 2.0:** Registro de producción digital con linaje y procedencia de cada asset y fotograma.

### 8.12. Comprensión Global del Proyecto y Escenas
- **REQ-041 — Project Understanding Engine:** Construcción del `ProjectKnowledgeGraph` (Personas, Lugares, Eventos, Objetos, Declaraciones, Fuentes, Escenas, Planos, Audio) antes de editar.
- **REQ-042 — Scene Reconstruction:** Agrupación semántica de planos en escenas por continuidad espacial, temporal, lumínica y acústica.
- **REQ-043 — Temporal Intelligence:** Distinción ontológica entre tiempo real, flashbacks, flash-forwards, archivo histórico, montajes, time-lapses y reconstrucciones dramatizadas.
- **REQ-050 — Scene Importance Ranking:** Puntuación de relevancia por escena (`SceneScore` multidimensional) para derivar versiones resumidas sin alterar la jerarquía dramática.

### 8.13. Causalidad Narrativa, Revelación y Psicología de la Atención
- **REQ-044 — Narrative Causality Graph:** Modelado de relaciones causales (Evento A causa Evento B) impidiendo inversiones cronológicas accidentales que alteren el significado.
- **REQ-045 — Information Reveal Management:** Control de spoilers, setups y payoffs, evitando que un B-Roll o gráfico anticipe visualmente una revelación antes de su beat narrativo.
- **REQ-046 — Audience Attention Model:** Curva heurística de atención `ATTENTION(t)` para detectar colapsos o sobrecargas de atención.
- **REQ-047 — Cognitive Load Engine:** Cálculo de saturación multimodal (voz + gráficos + datos + subtítulos + música) para espaciar elementos cuando se detecte sobrecarga cognitiva.
- **REQ-048 — Editorial Contrast:** Alternancia obligatoria de tensiones (LOW $\to$ MEDIUM $\to$ HIGH $\to$ PEAK $\to$ RELEASE) evitando la fatiga de picos continuos.
- **REQ-049 — Pacing Curve Composer:** Modelado de perfiles de ritmo continuo `pacingCurve(t)` parametrizados por cada `EditorialProfile`.

### 8.14. Poda Inteligente, Desduplicación y Selección de Tomas
- **REQ-051 — Intelligent Trimming:** Reducción proporcional y semántica de duraciones (ej. 45 min RAW $\to$ 15 min Master $\to$ 60s Trailer) preservando causalidad y emoción.
- **REQ-052 — Semantic Redundancy Engine:** Detección y poda de argumentos o explicaciones duplicadas entre narrador y entrevistados, conservando la toma más potente.
- **REQ-053 — Best Take Selection:** Puntuación comparativa de tomas alternativas (claridad, entonación, mirada, audio, estabilidad) conservando los descartes en reserva.
- **REQ-054 — Performance Intelligence:** Detección de vacilaciones, errores verbales y caídas de energía, distinguiendo entre imperfección humana auténtica y error técnico.
- **REQ-055 — Natural Performance Preservation:** Prohibición expresa de sobre-editar la voz; preservación de respiraciones, risas y pausas según la tolerancia del perfil.

### 8.15. Continuidad Visual Avanzada y Gramática de Cámara
- **REQ-056 — Face & Gaze Continuity:** Rastreo de la dirección de mirada y orientación craneal para evitar saltos desconcertantes entre planos contiguos.
- **REQ-057 — Object & Prop Continuity:** Verificación de consistencia en objetos en mano, vestuario y atrezzo entre planos consecutivos de la misma escena.
- **REQ-058 — Lighting Continuity:** Monitoreo de exposición, dirección de sombras, contraste y temperatura para evitar saltos lumínicos antinaturales.
- **REQ-059 — Camera Movement Grammar:** Taxonomía de movimientos (STATIC, PAN, TILT, DOLLY, HANDHELD, GIMBAL, DRONE, WHIP) y prevención de colisiones cinemáticas fatigosas.
- **REQ-060 — Transition Intelligence:** Transiciones con justificación semántica (HARD_CUT, MATCH_CUT, J_CUT, L_CUT, DISSOLVE, FADE, TIME_TRANSITION).
- **REQ-061 — Match Cut Engine:** Detección de coincidencias formales (forma, color, vector de movimiento, sonido) para enlaces visuales cinematográficos.

### 8.16. Paisaje Sonoro y Acústica Avanzada
- **REQ-062 — Sound Bridge Intelligence:** Utilización de sonidos diegéticos o ambientales de la siguiente escena como puente acústico previo al corte.
- **REQ-063 — Room Tone Continuity:** `RoomToneProfile` por localización para rellenar silencios y eliminar caídas a cero digital entre tomas.
- **REQ-064 — Dialogue Repair Intelligence:** Diagnóstico declarativo de clipping, oclusivas (*plosives*), zumbidos y eco con plan de reparación no destructivo.
- **REQ-065 — Voice Consistency:** Consistencia de volumen, balance tonal y dinámica para un mismo locutor a lo largo de toda la línea temporal.
- **REQ-066 — Music Narrative Alignment:** Sincronización de introducciones, crescendos, caídas (*drops*) e impactos musicales con los hitos de la historia.
- **REQ-067 — Dynamic Soundscape:** Estratificación acústica en tres planos (Primer plano / Medio plano / Fondo) evitando la saturación de frecuencias.
- **REQ-068 — Silence as a First-Class Asset:** El silencio como entidad de montaje explícita (`SilenceRegion`) con propósito, duración y carga emocional.
- **REQ-069 — Editorial Punctuation:** Modelo de puntuación sintáctica (corte seco = punto, pausa = punto y coma, montaje = párrafo, revelación = exclamación).

### 8.17. Dirección, Estilo y Continuidad Episódica
- **REQ-070 — Director's Intent Layer:** Traducción de intenciones abstractas (ej. *"hacer que esta escena se sienta tensa e incómoda"*) a parámetros de montaje objetivos.
- **REQ-071 — Style Bible:** Declaración formal de tipografías, paletas de color, transiciones, framing y lower-thirds compartidos por toda una producción.
- **REQ-072 — Series Continuity:** Coherencia de personajes, gráficos, música y reglas a lo largo de múltiples episodios o entregas seriadas.
- **REQ-073 — Character Continuity:** Identidad persistente de personas recurrentes para coherencia en rótulos y atribuciones.
- **REQ-074 — Location Continuity:** Identidad geográfica y visual persistente para cada localización, enlazada con coordenadas y overlays.
- **REQ-075 — Editorial Memory:** Almacenamiento persistente de correcciones y preferencias del editor para convertirlas en reglas automáticas futuras.

### 8.18. Jerarquía de Reglas, Optimización y Simulación
- **REQ-076 — Universal Rule Precedence:** Jerarquía inquebrantable de resolución de conflictos:
  $$\text{SAFETY} \succ \text{LEGAL/FACTUAL} \succ \text{EDITOR LOCK} \succ \text{NARRATIVE} \succ \text{CONTINUITY} \succ \text{AUDIO} \succ \text{VISUAL} \succ \text{STYLE} \succ \text{OPTIMIZATION}$$
- **REQ-077 — Constraint Solver:** Resolutor formal de restricciones temporales (explora trims, extensiones, B-Roll alternativo, freezes o voice-stretch).
- **REQ-078 — Multi-Objective Optimization:** Función de pérdida editorial ponderada por el perfil para maximizar calidad y minimizar defectos.
- **REQ-079 — Pareto Editorial Optimization:** Presentación de soluciones Pareto-óptimas alternativas (ej. Versión con mayor rigor factual vs Versión con mayor dinamismo emocional).
- **REQ-080 — Editorial Simulation:** Simulación previa instantánea del plan de montaje (conteo de cortes, gráficos, picos y avisos) antes de renderizar.
- **REQ-081 — Human Review Queue:** Cola ordenada de decisiones con baja confianza ($<0.70$) para resolución ágil por el editor humano.
- **REQ-082 — Editorial Diff:** Cuantificación exacta del impacto (narrativo, de ritmo y de duración) ante cualquier modificación manual del editor.
- **REQ-083 — Version Diff:** Comparativa estructural detallada entre el Master y sus versiones derivadas (Social, Trailer, etc.).

### 8.19. Integridad de Activos, Legal y Entrega
- **REQ-084 — Undoable Compilation:** Compilación puramente funcional y no destructiva; los archivos brutos permanecen inmutables.
- **REQ-085 — Non-Destructive Asset Graph:** Grafo de transformaciones rastreable desde el activo original hasta la salida final.
- **REQ-086 — Asset Provenance:** Trazabilidad forense completa de cada fotograma (cámara de origen, timecode, clasificador y confianza).
- **REQ-087 — Copyright & License Awareness:** Bloqueo en QA ante activos con licencias desconocidas o expiradas según el perfil de distribución.
- **REQ-088 — Watermark & Attribution Engine:** Generación automática de créditos, atribuciones de archivo y avisos legales en pantalla.
- **REQ-089 — Credits Compiler:** Compilación automática de títulos de crédito (iniciales, lower thirds, archivo y créditos finales) a partir del manifiesto.
- **REQ-090 — Delivery Mastering:** Validación de especificaciones técnicas según el canal de entrega (YouTube, Broadcast EBU R128, Social 9:16, DCP Prep).

### 8.20. Visión Final
- **REQ-091 — Editorial Operating System:** Capacidad de traducir una visión humana de alto nivel (*"Quiero un documental de 18 minutos sobre esta investigación, sobrio, cinematográfico, basado en evidencias y con clímax emocional"*) en un plan de compilación formal ejecutado a través de la Editorial IR hacia cualquier backend de la industria.

---

## 9. Los 5 Pilares Arquitectónicos Máximos

1. **Editorial IR (Representación Intermedia Editorial):**  
   El núcleo que separa la inteligencia editorial de la sintaxis del software de render. El motor edita sobre el grafo editorial y luego compila al target deseado.
2. **Evidence + Fact Layer:**  
   Capacidad de vincular afirmaciones con fuentes y archivos, abriendo el campo documental, periodístico y científico con rigor inatacable.
3. **Shot Grammar + Visual Continuity:**  
   Evolución de cortar silencios a dirigir secuencias respetando el eje de $180^\circ$, la dirección de pantalla y la progresión armónica de planos.
4. **Editorial QA + Explainability:**  
   Linter audiovisual con explicabilidad causal de cada decisión, permitiendo inspeccionar y auditar el por qué detrás de cada corte.
5. **Multi-Version Editorial Compiler:**  
   Un solo master derivado hacia 16:9, 9:16 y trailers mediante re-edición y sustitución semántica de planos, no un simple recorte automático.


