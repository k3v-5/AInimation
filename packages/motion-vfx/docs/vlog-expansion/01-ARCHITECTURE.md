# Arquitectura del Vlog Intelligence Engine

**Documento:** `01-ARCHITECTURE.md`  
**Versión:** `1.0.0`  
**Sistema base:** Motor audiovisual v3.4.0  
**Estado:** DRAFT  
**Implementación autorizada:** NO hasta aprobación  
**Dependencia:** `00-MASTER-SPECIFICATION.md`  

---

## 1. Propósito

Este documento define la arquitectura interna de la expansión Vlog Multilingüe.

Su finalidad es establecer:
- componentes.
- responsabilidades.
- límites.
- dependencias.
- flujo de datos.
- fronteras entre subsistemas.
- dirección permitida de dependencias.
- mecanismos de comunicación.
- puntos de extensión.
- políticas de desacoplamiento.
- reglas de integración con el motor v3.4.0.

Este documento no define todavía las estructuras completas de datos. Éstas serán establecidas en `02-DATA-CONTRACTS.md`.

---

## 2. Principio arquitectónico

El sistema se construirá como una arquitectura por capas:

```
┌──────────────────────────────────────────────────────────────┐
│                    PRESENTATION / CONTROL                    │
│                         MCP / CLI / DSL                      │
├──────────────────────────────────────────────────────────────┤
│                    ORCHESTRATION LAYER                       │
│                    VlogPipelineOrchestrator                  │
├──────────────────────────────────────────────────────────────┤
│                    EDITORIAL INTELLIGENCE                    │
│                                                              │
│  JumpCut │ PunchIn │ B-Roll Matcher │ Localization │ Pacing │
├──────────────────────────────────────────────────────────────┤
│                    ANALYSIS LAYER                            │
│                                                              │
│ VAD │ Whisper │ Shot Detection │ Vision │ Audio │ Metadata  │
├──────────────────────────────────────────────────────────────┤
│                    DOMAIN MODEL                              │
│                                                              │
│ Timeline │ Media │ Speech │ Shots │ EditPlan │ Localization │
├──────────────────────────────────────────────────────────────┤
│                    EXISTING CORE v3.4.0                      │
│                                                              │
│ Matrix │ Property │ Timeline │ Audio │ Reframe │ Styles │ AE │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Regla de dependencia

Las dependencias deberán fluir únicamente hacia abajo.

Permitido:
$$\text{Orchestrator} \longrightarrow \text{Editorial} \longrightarrow \text{Analysis} \longrightarrow \text{Domain} \longrightarrow \text{Core}$$

No permitido:
$$\text{Core} \longrightarrow \text{Vlog Intelligence}$$
$$\text{Whisper} \longrightarrow \text{After Effects}$$
$$\text{B-Roll Matcher} \longrightarrow \text{MCP}$$

Los componentes inferiores no deberán conocer los mecanismos de control superiores.

---

## 4. Capas

### 4.1. Control Layer
Responsable de recibir comandos externos.

Componentes:
- `MCP Server`
- `CLI`
- `DSL Adapter`

Responsabilidades:
- validar comandos.
- construir solicitudes.
- invocar el orquestador.
- devolver resultados.
- devolver errores estructurados.

No deberá contener lógica editorial.

---

## 5. Orchestration Layer

Componente principal:
- `VlogPipelineOrchestrator`

Responsabilidades:
- iniciar ejecuciones.
- resolver dependencias.
- coordinar etapas.
- gestionar cache.
- controlar configuración.
- registrar ejecución.
- manejar fallos.
- producir estado de pipeline.

No deberá implementar algoritmos de edición.

Ejemplo:
```
Orchestrator
     │
     ├── SpeechAnalysis
     ├── FootageAnalysis
     ├── EditorialPlanning
     ├── Localization
     ├── Pacing
     ├── Overlays
     └── Export
```

---

## 6. Analysis Layer

Esta capa convierte material bruto en metadata estructurada.

Componentes iniciales:
- `MediaAnalyzer`
- `AudioAnalyzer`
- `VADAnalyzer`
- `TranscriptAnalyzer`
- `ShotAnalyzer`
- `FaceAnalyzer`
- `SemanticAnalyzer`
- `GeoMetadataAnalyzer`

La capa de análisis:
- **NO edita.**
- **NO elimina clips.**
- **NO genera EditPlans finales.**
- **NO genera JSX.**
- **NO controla After Effects.**

Su salida es exclusivamente metadata.

---

## 7. Media Analysis

`MediaAnalyzer` deberá obtener:
- `duration`
- `frameRate`
- `width`
- `height`
- `codec`
- `audioStreams`
- `videoStreams`
- `sampleRate`
- `channels`

También deberá validar que el medio pueda ser procesado. No deberá modificar el archivo fuente.

---

## 8. Audio Analysis

`AudioAnalyzer` proporcionará información como:
- `RMS`
- `peak`
- `energy`
- `silence candidates`
- `speech candidates`

Su responsabilidad termina en producir análisis. No debe decidir por sí mismo *"este silencio debe eliminarse"*. La decisión pertenece a la capa editorial.

---

## 9. VAD

`VADAnalyzer` identifica:
- `SPEECH`
- `NON_SPEECH`
- `UNKNOWN`

Debe producir intervalos temporales. No debe realizar edición.

---

## 10. Transcript Analysis

El sistema existente `LocalWhisperTranscriptionBridge` será reutilizado cuando sea compatible.

Su responsabilidad:
$$\text{Audio} \longrightarrow \text{Transcript} \longrightarrow \text{Word Timing}$$

El resultado deberá ser independiente del idioma. No deberá decidir cortes.

---

## 11. Shot Analysis

`ShotAnalyzer` identifica unidades visuales.

Conceptualmente:
```
SOURCE
│
├── Shot 001
├── Shot 002
├── Shot 003
└── Shot 004
```

Cada shot tendrá metadata. No decidirá si debe aparecer en el montaje.

---

## 12. Face Analysis

El `FaceAnalyzer` será opcional.

Proporcionará:
- `face bounding boxes`
- `confidence`
- `focus candidates`

No realizará punch-ins. La decisión:
$$\text{face detected} \longrightarrow \text{candidate focus point} \longrightarrow \text{PunchInDetector}$$
pertenece a Editorial Intelligence.

---

## 13. Semantic Analysis

Esta capa podrá asociar metadata semántica:
- `restaurant`, `food`, `street`, `hotel`, `airport`, `beach`, `museum`, `city`, `person`, `vehicle`, etc.

La semántica deberá ser representada como metadata y no como instrucciones de edición.

---

## 14. Editorial Intelligence Layer

Ésta es la capa central de la expansión.

Componentes:
- `VlogJumpCutEngine`
- `DynamicPunchIn`
- `VlogFootageClassifier`
- `SemanticBRollMatcher`
- `VlogEditorialPlanner`
- `MultilingualVoiceoverEngine`
- `LocalizationPlanner`
- `VlogAdaptivePacingEngine`
- `VlogTravelOverlays`

Esta capa consume análisis y produce decisiones editoriales.

---

## 15. Regla Analysis vs Editorial

La frontera es estricta:
$$\text{ANALYSIS (¿Qué existe?)} \longrightarrow \text{EDITORIAL (¿Qué hacemos con ello?)}$$

Ejemplo:
- **VAD:** `silence 2.0 -> 2.4`
- **Editorial:** `REMOVE`

*Nunca:*
- ~~VAD: `REMOVE 2.0 -> 2.4`~~

---

## 16. VlogJumpCutEngine

Responsabilidad:
- recibir candidatos de silencio.
- aplicar reglas editoriales.
- proteger palabras.
- construir cortes.
- generar segmentos de salida.
- declarar crossfades.

No debe:
- analizar rostros.
- traducir.
- generar TTS.
- clasificar B-Roll.
- generar JSX.

---

## 17. DynamicPunchIn

Responsabilidad:
- recibir candidatos de énfasis.
- calcular eventos de punch-in.
- seleccionar focus point.
- generar animación declarativa.

No debe:
- detectar caras directamente.
- editar directamente After Effects.
- modificar el source media.

Puede consumir resultados del `FaceAnalyzer`.

---

## 18. VlogFootageClassifier

Responsabilidad:
$$\text{RAW SHOTS} \longrightarrow \text{A-ROLL} \;|\; \text{B-ROLL} \;|\; \text{TIMELAPSE} \;|\; \text{ACTION} \;|\; \text{UNKNOWN}$$

Podrá utilizar:
- audio.
- movimiento.
- transcript.
- detección facial.
- metadata visual.

No debe crear el montaje final.

---

## 19. SemanticBRollMatcher

Responsabilidad:
$$\text{Speech Segment} \longrightarrow \text{Semantic representation} \longrightarrow \text{Candidate Shots} \longrightarrow \text{Ranking} \longrightarrow \text{B-Roll selection}$$

Debe devolver candidatos y/o selección editorial según el contrato definitivo. No debe renderizar.

---

## 20. VlogEditorialPlanner

Este componente será el integrador de decisiones editoriales.

Recibirá:
- `Speech`
- `Shots`
- `Jump Cuts`
- `Punch Ins`
- `B-Roll matches`
- `Transitions`

y producirá:
$$\text{EditPlan}$$

Será el primer punto donde se construya una visión editorial completa.

---

## 21. Localization Layer

Componentes:
- `TranslationAdapter`
- `TTSProvider`
- `VoiceTimingAnalyzer`
- `LocalizationPlanner`

Responsabilidad:
$$\text{Master Language} \longrightarrow \text{Localized Content} \longrightarrow \text{Localized Audio} \longrightarrow \text{Localized Timing}$$

No debe modificar directamente el montaje maestro.

---

## 22. TTS Provider Abstraction

No se acoplará el sistema a un motor concreto.

Interfaz conceptual:
```typescript
interface TTSProvider {
  synthesize(): Promise<AudioTrack>;
  getMetadata(): ProviderMetadata;
  capabilities(): ProviderCapabilities;
}
```

Los motores locales serán adaptadores:
$$\text{TTS Engine} \longrightarrow \text{Provider Adapter} \longrightarrow \text{MultilingualVoiceoverEngine}$$

---

## 23. Adaptive Pacing

`VlogAdaptivePacingEngine` recibe:
- `Master EditPlan`
- `Localized Timing`
- `Shot Metadata`

y produce:
$$\text{Localized EditPlan}$$

Su función es reconciliar:
$$\text{VOICE DURATION} \quad \updownarrow \quad \text{VISUAL DURATION}$$

No deberá modificar arbitrariamente la semántica del montaje.

---

## 24. Travel Overlay Layer

`VlogTravelOverlays` generará objetos declarativos:
- `GeoBadge`
- `RouteMap`
- `Polaroid`
- `Timestamp`
- `LocationCard`

No generará JSX directamente. La arquitectura será:
$$\text{Overlay Specification} \longrightarrow \text{Graphics Plan} \longrightarrow \text{AE Exporter} \longrightarrow \text{JSX}$$

---

## 25. Export Layer

Componentes:
- `EditPlanSerializer`
- `AfterEffectsExporter`
- `MetadataExporter`
- `MCPResultSerializer`

Responsabilidades:
- transformar `EditPlan` en formatos externos.
- generar JSX.
- validar export.
- preservar timestamps.
- preservar IDs.
- preservar metadata.

No deberá tomar decisiones editoriales.

---

## 26. After Effects Adapter

La arquitectura deberá aislar After Effects:
$$\text{EditPlan} \longrightarrow \text{AE Adapter} \longrightarrow \text{ExtendScript / JSX}$$

Ningún módulo editorial deberá importar directamente APIs específicas de After Effects.

---

## 27. MCP Layer

MCP será un mecanismo de control:
$$\text{MCP Request} \longrightarrow \text{Validation} \longrightarrow \text{Orchestrator} \longrightarrow \text{Domain} \longrightarrow \text{Result} \longrightarrow \text{MCP Response}$$

No deberá contener lógica de negocio duplicada.

---

## 28. DSL Layer

El DSL deberá representar intenciones.

Ejemplo conceptual:
```typescript
vlog.jumpCut(...)
vlog.punchIn(...)
vlog.classify(...)
vlog.localize(...)
vlog.pace(...)
vlog.overlay(...)
```

El DSL se transformará en comandos internos. No deberá implementar los algoritmos.

---

## 29. Comunicación entre módulos

Los módulos no deberán comunicarse mediante variables globales.

Preferido:
$$\text{Input Contract} \longrightarrow \text{Pure / Deterministic Function} \longrightarrow \text{Output Contract}$$

Para procesos largos:
`PipelineContext` o contratos explícitos equivalentes.

La elección definitiva será documentada en `02-DATA-CONTRACTS.md`.

---

## 30. Estado

Se distinguirá entre:
- **Immutable Input:** Material original y análisis originales.
- **Derived State:** Resultados calculados.
- **Execution State:** Estado temporal del pipeline.
- **Output:** `EditPlan` y artefactos generados.

No deberá modificarse destructivamente el material original.

---

## 31. Inmutabilidad

Los objetos de dominio deberán tratarse como inmutables siempre que sea compatible con la arquitectura existente.

Especialmente:
- `MediaReference`
- `Transcript`
- `ShotManifest`
- `AudioAnalysis`
- `EditPlan`
- `LocalizationPlan`

Las transformaciones deberán producir nuevos objetos.

---

## 32. Cache Architecture

Los análisis costosos podrán cachearse:
$$\text{RAW MEDIA} \longrightarrow \text{CONTENT HASH} \longrightarrow \text{CACHE KEY} \longrightarrow \text{Analysis Cache}$$

El cache key deberá considerar:
- `source identity`
- `analysis version`
- `configuration`
- `provider version`

Una modificación relevante deberá invalidar el resultado.

---

## 33. Parallelización

Las tareas independientes podrán ejecutarse en paralelo:
```
             Media
               │
       ┌───────┼────────┐
       ▼       ▼        ▼
      VAD    Shot    Metadata
       │       │        │
       └───────┼────────┘
               ▼
           Editorial
```

No se deberá paralelizar una etapa que dependa de datos aún no disponibles.

---

## 34. Pipeline Context

La ejecución completa deberá tener un contexto identificable:

```typescript
interface PipelineContext {
  executionId: string;
  projectId: string;
  sourceId: string;
  engineVersion: string;
  configurationVersion: string;
  deterministicSeed: number;
}
```

El contrato definitivo será establecido posteriormente.

---

## 35. Error Boundaries

Cada capa deberá definir su frontera de errores:
$$\text{Provider Error} \longrightarrow \text{Adapter Error} \longrightarrow \text{Domain Error} \longrightarrow \text{Pipeline Error} \longrightarrow \text{External Response}$$

Los errores internos no deberán filtrarse sin transformación cuando expongan detalles innecesarios.

---

## 36. Fallback Architecture

Los fallbacks deberán vivir en el nivel apropiado:
$$\text{FaceAnalyzer unavailable} \longrightarrow \text{FocusPoint default } (0.5, 0.5)$$

Pero:
$$\text{TTS provider unavailable} \longrightarrow \text{NO inventar audio (Error Explícito)}$$

El sistema deberá distinguir entre fallback seguro y requisito imposible.

---

## 37. Extensibilidad

Los siguientes componentes deberán ser intercambiables mediante interfaces:
- `TTSProvider`
- `TranslationProvider`
- `SpeechAnalyzer`
- `FaceAnalyzer`
- `SemanticAnalyzer`
- `ShotAnalyzer`
- `StorageProvider`
- `CacheProvider`
- `Exporter`

La implementación concreta podrá variar sin modificar la lógica editorial.

---

## 38. Prohibición de acoplamiento

No permitido:
$$\text{VlogJumpCutEngine} \longrightarrow \text{Piper}$$

Preferido:
$$\text{MultilingualVoiceoverEngine} \longrightarrow \text{TTSProvider} \longrightarrow \text{PiperAdapter}$$

No permitido:
$$\text{PunchIn} \longrightarrow \text{AfterEffects JSX}$$

Preferido:
$$\text{PunchIn} \longrightarrow \text{EditPlan} \longrightarrow \text{AEExporter}$$

---

## 39. Flujo maestro

La ejecución completa será conceptualmente:

```
                    RAW MEDIA
                        │
                        ▼
                ┌──────────────┐
                │ Media Analyze│
                └──────┬───────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
      Audio          Shots          Metadata
        │              │              │
        ▼              ▼              ▼
       VAD          Classifier      Semantic
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                Editorial Planner
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
        Jump Cuts   Punch-ins   B-Roll
            │          │          │
            └──────────┼──────────┘
                       ▼
                    EditPlan
                       │
                       ▼
                 Localization
                       │
                       ▼
                Adaptive Pacing
                       │
                       ▼
                Travel Overlays
                       │
                       ▼
                 Final EditPlan
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
             JSX      MCP      JSON
```

---

## 40. Regla de una sola dirección

El flujo no podrá retroceder modificando silenciosamente etapas anteriores.

Ejemplo prohibido:
$$\text{Pacing} \longrightarrow \text{modifica Transcript}$$

Correcto:
$$\text{Transcript} \longrightarrow \text{Pacing} \longrightarrow \text{Localized EditPlan}$$

Si una etapa necesita modificar una decisión anterior, deberá producir una nueva versión derivada y trazable.

---

## 41. Versionado de resultados

Los resultados derivados deberán identificar:
- `sourceVersion`
- `analysisVersion`
- `algorithmVersion`
- `configurationVersion`
- `schemaVersion`

Esto permitirá comparar dos ejecuciones.

---

## 42. Arquitectura de plugins

Los proveedores externos/locales deberán actuar como plugins/adapters:
```
             Domain Interface
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
 PiperAdapter   WhisperAdapter  OtherAdapter
```

El dominio no deberá conocer detalles internos del proveedor.

---

## 43. Política de recursos

Los módulos podrán declarar:
- `CPU`
- `GPU`
- `RAM`
- `Disk`

requeridos o recomendados. El orquestador podrá utilizar esta información para decidir ejecución secuencial/paralela. Los valores concretos se definirán en `20-PERFORMANCE.md`.

---

## 44. Arquitectura de archivos temporales

Los artefactos intermedios deberán estar separados de:
- `source/`
- `output/`
- `cache/`
- `temp/`
- `logs/`

Nunca se deberá modificar el source original como almacenamiento temporal.

---

## 45. Reanudación de pipelines

La arquitectura deberá permitir continuar una ejecución interrumpida cuando los resultados previos sigan siendo válidos.

Ejemplo:
- `Media Analysis` ✓
- `Speech Analysis` ✓
- `Shot Analysis` ✓
- `Editorial Planning` ✗

Al reanudar:
$$\text{reuse analysis} \longrightarrow \text{Editorial Planning}$$

No recalcular innecesariamente.

---

## 46. Idempotencia

Una operación repetida con los mismos inputs deberá producir el mismo resultado. Especialmente:
- `analysis`
- `classification`
- `planning`
- `localization timing`
- `overlay generation`
- `export`

---

## 47. Testing arquitectónico

Se deberán implementar pruebas que garanticen:
- dirección de dependencias.
- ausencia de imports prohibidos.
- determinismo.
- contratos válidos.
- serialización.
- compatibilidad.
- idempotencia.
- correcta propagación de errores.

---

## 48. Definition of Done del documento

Este documento estará aprobado cuando:

- [ ] Todas las capas están definidas
- [ ] Todos los componentes están asignados
- [ ] Cada componente tiene responsabilidad única
- [ ] Las dependencias están definidas
- [ ] Las dependencias prohibidas están definidas
- [ ] Analysis y Editorial están separados
- [ ] Editorial y Export están separados
- [ ] MCP y DSL no contienen lógica duplicada
- [ ] After Effects está aislado
- [ ] Providers están abstraídos
- [ ] Cache está definida conceptualmente
- [ ] Determinismo está contemplado
- [ ] Idempotencia está contemplada
- [ ] Fallbacks están contemplados
- [ ] Errores tienen fronteras
- [ ] Versionado está contemplado
- [ ] Reanudación está contemplada
- [ ] No existen responsabilidades ambiguas

---

## 49. Estado del documento

**Documento:** `01-ARCHITECTURE.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

La implementación no deberá comenzar hasta que este documento y sus documentos dependientes estén aprobados.
