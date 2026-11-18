# MASTER IMPLEMENTATION & ACCEPTANCE SPECIFICATION

**Proyecto:** Motor Audiovisual Programático  
**Base:** v3.4.0  
**Expansión:** Vlog / Documentary / Multilingual Production Suite  
**Estado:** ESPECIFICACIÓN MAESTRA DE CIERRE  
**Propósito:** Convertir los documentos técnicos existentes en una única autoridad de implementación.  

---

## 1. Autoridad de este documento

Los documentos técnicos anteriores del proyecto constituyen la especificación de requisitos.

Este documento establece:
- cómo deben interpretarse conjuntamente;
- qué debe implementarse;
- en qué orden;
- qué restricciones son obligatorias;
- cómo validar la implementación;
- cuándo puede considerarse terminado el proyecto.

No sustituye los requisitos funcionales previamente definidos.

En caso de contradicción entre documentos, la IA implementadora NO debe decidir silenciosamente.

Debe:
1. detectar la contradicción;
2. identificar los documentos afectados;
3. explicar el conflicto;
4. detener únicamente la parte afectada;
5. solicitar resolución antes de introducir comportamiento nuevo.

---

## 2. Regla principal de implementación

La implementación deberá cumplir simultáneamente:
$$\text{REQUISITOS EXISTENTES} + \text{EXPANSIÓN VLOG} + \text{MULTILINGÜE} + \text{COMPATIBILIDAD v3.4.0} + \text{100\% TESTS VERDES}$$

No se permite sacrificar funcionalidades existentes para implementar funcionalidades nuevas.

---

## 3. Estado inicial obligatorio

Antes de modificar código:
```bash
npm install
npm test
```
o el comando equivalente definido por el proyecto.

Debe registrarse:
- existing test count
- passing tests
- failing tests
- coverage
- build status
- lint status
- typecheck status

El baseline deberá conservarse.

---

## 4. Baseline de regresión

El estado inicial esperado es:
$$712 / 712 \text{ tests passing}, \quad 0 \text{ failures}$$

Si el repositorio real contiene una cantidad diferente de tests, la IA deberá registrar la cantidad real y utilizarla como baseline.

No deberá modificar tests existentes únicamente para hacerlos pasar.

---

## 5. Objetivo final

La implementación terminada deberá proporcionar:
$$\text{Vlog Editing} + \text{A-Roll/B-Roll Intelligence} + \text{Jump Cuts} + \text{Dynamic Punch-In} + \text{Multilingual Localization}$$
$$+ \text{Offline TTS} + \text{Adaptive Pacing} + \text{Multilingual Subtitles} + \text{Travel Overlays} + \text{Smart Audio}$$
$$+ \text{Existing Style Engines} + \text{Multi-Aspect Reframing} + \text{After Effects JSX} + \text{MCP} + \text{CLI}$$
$$+ \text{Caching} + \text{Recovery} + \text{Validation}$$

---

## 6. Restricción de costo

El sistema deberá funcionar en modo:
$$\text{OFFLINE} = \text{TRUE}$$
sin requerir APIs comerciales de terceros.

No se deberá introducir como dependencia obligatoria:
- OpenAI API
- Google Cloud
- Azure Cloud
- ElevenLabs
- Amazon Polly
u otros servicios equivalentes.

---

## 7. Principio Offline-First

Toda capacidad que pueda ejecutarse localmente deberá hacerlo localmente.

Las dependencias externas, si alguna resulta opcional, deberán ser:
$$\text{OPTIONAL}$$
y nunca requisito para el funcionamiento base.

---

## 8. Compatibilidad hacia atrás

Las funcionalidades v3.4.0 deberán conservarse.

Especialmente:
- Matrix2D
- Hierarchy
- Property<T>
- Timeline
- Time Remapping
- Style Presets
- Typography
- Subtitles
- Audio
- SFX
- Color
- Reframing
- Whisper
- Viral Detector
- JSX Export
- MCP

---

## 9. Arquitectura final

La arquitectura deberá separarse conceptualmente en:
- CORE
- TIMELINE
- MEDIA
- ANALYSIS
- TRANSCRIPTION
- NARRATIVE
- VLOG EDITING
- B-ROLL
- LOCALIZATION
- TTS
- PACING
- SUBTITLES
- OVERLAYS
- AUDIO
- STYLES
- REFRAMING
- EXPORT
- ORCHESTRATION
- ARTIFACTS
- CACHE
- VALIDATION
- MCP
- CLI

---

## 10. Regla de dependencia

Las dependencias deberán fluir desde capas de bajo nivel hacia capas de alto nivel.

No se permiten dependencias circulares.

Ejemplo:
$$\text{CORE} \longrightarrow \text{MEDIA} \longrightarrow \text{ANALYSIS} \longrightarrow \text{EDITING} \longrightarrow \text{LOCALIZATION} \longrightarrow \text{ORCHESTRATION}$$

El Core nunca deberá depender del Orchestrator.

---

## 11. Nuevos módulos obligatorios

La expansión deberá implementar como mínimo:
- `VlogJumpCutEngine`
- `DynamicPunchIn`
- `VlogFootageClassifier`
- `BRollMatcher`
- `MultilingualVoiceoverEngine`
- `LocalizationEngine`
- `VlogAdaptivePacingEngine`
- `MultilingualSubtitleEngine`
- `VlogTravelOverlays`
- `VlogProductionOrchestrator`

---

## 12. VlogJumpCutEngine

Debe:
- detectar silencios;
- eliminar silencios configurables;
- mantener continuidad semántica;
- generar micro-crossfades;
- preservar sincronización;
- evitar cortar palabras;
- generar eventos de edición reproducibles.

Default:
$$\text{silenceThreshold} = 0.25\text{ s}, \quad \text{microCrossfade} = 10\text{ ms}$$
Los valores deberán ser configurables.

---

## 13. DynamicPunchIn

Debe soportar:
$$100\% \longrightarrow 115\% \longrightarrow 100\%$$
y permitir:
- énfasis;
- cambio de tema;
- beat narrativo;
- evento viral;
- override manual.

Debe respetar límites de encuadre.

---

## 14. VlogFootageClassifier

Debe clasificar:
- `A_ROLL`
- `B_ROLL`
- `TIMELAPSE`
- `ACTION`
- `UNKNOWN`

Cada resultado deberá incluir confianza:
$$0 \le \text{confidence} \le 1$$
No se permitirá presentar una clasificación incierta como certeza absoluta.

---

## 15. B-Roll Matcher

El matcher deberá considerar como mínimo:
- semantic relevance
- visual relevance
- duration compatibility
- quality
- novelty
- previous usage

Resultado:
$$\text{score} \in [0, 100]$$
No deberá introducir B-Roll irrelevante únicamente para llenar espacios.

---

## 16. Transcripción

Se reutilizará la infraestructura Whisper local existente.

Debe conservar:
- segment timing
- word timing
- confidence
- language

---

## 17. Narrative Analysis

Deberá derivarse una representación estructurada de:
- hooks
- topics
- chapters
- entities
- emphasis
- pauses
- narrative beats

Los beats mínimos:
- `HOOK`
- `SETUP`
- `CONTEXT`
- `DEVELOPMENT`
- `CLIMAX`
- `REFLECTION`
- `CTA`
- `OUTRO`

---

## 18. Localización

La arquitectura deberá permitir:
$$\text{source language} \longrightarrow \text{target language(s)}$$
sin duplicar la lógica de edición.

---

## 19. Idiomas objetivo

Debe soportarse como mínimo:
- `es-MX`
- `es-ES`
- `en-US`
- `en-GB`
- `pt-BR`
- `fr-FR`
- `de-DE`

La arquitectura deberá permitir agregar otros idiomas sin reescribir el Orchestrator.

---

## 20. TTS

El sistema deberá soportar motores TTS locales.

El motor deberá abstraerse mediante interfaz.

Ejemplo:
```typescript
interface TTSProvider {
  synthesize(request: TTSRequest): Promise<TTSResult>;
}
```
El Orchestrator nunca deberá depender directamente de una implementación concreta.

---

## 21. TTS Failure Isolation

Si falla `en-US` no deberá corromper `es-MX`, `pt-BR`, `fr-FR` o `de-DE`, salvo que la configuración indique `ALL_LANGUAGES_REQUIRED`.

---

## 22. Adaptive Pacing

Debe adaptar:
- B-Roll duration
- scene duration
- transition timing
- voice timing
- subtitle timing
según el idioma.

Time-stretch por defecto:
$$[0.95\text{x}, 1.05\text{x}]$$
No superar este rango automáticamente.

---

## 23. Prioridad de sincronización

Orden obligatorio:
1. ajustar duración visual
2. utilizar pausas disponibles
3. ajustar transición
4. aplicar micro time-stretch
5. generar warning/error

Nunca deformar agresivamente la voz como primera solución.

---

## 24. Timeline multilingüe

Cada idioma deberá tener una timeline independiente (`timeline_es-MX`, `timeline_en-US`, etc.).

---

## 25. Aislamiento de idiomas

Modificar una pista lingüística no deberá modificar las demás. Debe existir aislamiento para:
- voice
- subtitles
- localized text
- localized metadata
- language-specific timing

---

## 26. Recursos compartidos

Podrán compartirse: B-Roll, images, maps, SFX, logos y backgrounds cuando no dependan del idioma.

---

## 27. Subtítulos

Deben generarse a partir del timing de la voz correspondiente.

Modos mínimos:
- `STANDARD`
- `WORD_BY_WORD`
- `KARAOKE`
- `EMPHASIS`

Deben conservarse las capacidades de subtítulos existentes.

---

## 28. Safe Zones

Todo texto generado deberá respetar las safe zones existentes para:
$$16:9, \quad 9:16, \quad 1:1, \quad 4:5, \quad 21:9$$

---

## 29. Travel Overlays

Debe soportar:
- Geo-Badges
- Location Cards
- Time Cards
- Mini Maps
- Route Animation
- Polaroid Freeze Frame

Los datos podrán proceder de: GPS, metadata, narrative entities o manual project data.

---

## 30. Audio

La mezcla deberá conservar la jerarquía:
$$\text{VOICE} > \text{CRITICAL SFX} > \text{MUSIC} > \text{AMBIENCE}$$

Debe existir:
- RMS analysis
- ducking
- SFX synchronization
- language-specific voice tracks

---

## 31. Style System

La expansión deberá reutilizar el sistema de estilos existente. No crear un sistema paralelo.

Los estilos deberán poder aplicarse a: `project`, `scene`, `language` y `element`.

---

## 32. Reframing

Debe reutilizarse el sistema existente de:
- active speaker
- deadzone
- pan-and-scan
- multi-aspect
- split-screen
- safe zones

El Punch-In deberá integrarse con este sistema. No crear un segundo sistema incompatible de framing.

---

## 33. After Effects

El exportador deberá seguir utilizando ExtendScript / JSX y los Match Names compatibles existentes. Debe funcionar independientemente del idioma de la interfaz de After Effects.

---

## 34. Estructura de proyecto

La nueva funcionalidad deberá organizarse según la estructura existente respetando la separación por dominio. La IA deberá adaptar esta estructura al repositorio real en lugar de duplicar módulos existentes.

---

## 35. Orchestrator

Será responsable únicamente de coordinar.

Pipeline:
$$\text{VALIDATE} \to \text{INGEST} \to \text{ANALYZE} \to \text{CLASSIFY} \to \text{TRANSCRIBE} \to \text{NARRATIVE} \to \text{SOURCE TIMELINE}$$
$$\to \text{JUMP CUT} \to \text{B-ROLL} \to \text{LANGUAGE PLAN} \to \text{TTS} \to \text{PACING} \to \text{SUBTITLES} \to \text{OVERLAYS}$$
$$\to \text{STYLE} \to \text{AUDIO} \to \text{TIMELINES} \to \text{JSX} \to \text{VALIDATE} \to \text{PACKAGE}$$

---

## 36. Phase Contracts

Cada fase deberá tener `validate()`, `execute()`, `hashInput()` y `hashOutput()` con contratos fuertemente tipados.

---

## 37. Artifact System

Cada fase deberá producir artefactos identificados con `id`, `type`, `phase`, `checksum`, `engineVersion` y `dependencies`.

---

## 38. Cache

Caché persistente basada en hashes que se invalida ante cambios en entradas, configuración, versiones o dependencias.

---

## 39. Idempotencia

$$\text{Mismo input} + \text{Misma config} + \text{Misma versión de motor} + \text{Mismo seed} \implies \text{Idéntico resultado lógico}$$

---

## 40. Seed

Todas las operaciones pseudoaleatorias deberán aceptar seed explícito. No utilizar `Date.now()` como seed implícito para resultados audiovisuales.

---

## 41. Atomicidad

Nunca escribir directamente sobre el proyecto final. Usar `work/<runId>/` y realizar commit únicamente después de validar.

---

## 42. Recovery

Ante interrupciones: preservar artefactos válidos, identificar la fase incompleta y reanudar desde el último estado válido.

---

## 43. Retry

Reintento automático para errores recuperables ($\text{maxAttempts} = 3$). Errores de configuración o input no se reintentan automáticamente.

---

## 44. Cancellation

Cancelación limpia: detener fases futuras, notificar procesos activos, persistir estado, preservar artefactos válidos y limpiar temporales.

---

## 45. CLI

Interfaz equivalente a `npm run vlog:produce` con soporte conceptual para `--manifest`, `--languages`, `--style`, `--dry-run`, `--preview`, `--validate-only` y `--resume`.

---

## 46. MCP

Integración MCP para `create production`, `get status`, `cancel`, `resume` y `get logs` reutilizando la infraestructura MCP existente.

---

## 47. No duplicación

Antes de crear una clase nueva, la IA deberá comprobar si existe una implementación equivalente. No crear segundos motores paralelos si ya existe funcionalidad compatible.

---

## 48. Refactoring permitido

Se permite refactorizar código existente cuando sea necesario para integración, conservando la compatibilidad de comportamiento (`behavioral compatibility`).

---

## 49. Tests obligatorios

Cada módulo nuevo contará con unit tests, integration tests, edge-case tests y failure tests.

---

## 50. Property-Based Testing

Las operaciones matemáticas y transformaciones deterministas deberán mantener el estándar PBT existente con `fast-check`.

---

## 51. E2E mínimo

Fixture de 30–60 segundos con A-Roll, B-Roll, silencios, punch-in, 2 ubicaciones, 2 idiomas, subtítulos, TTS, música, SFX, Geo-Badge, mapa, Polaroid y exportación JSX.

---

## 52. E2E multilingüe completo

Prueba integral en los 5 idiomas oficiales (`es-MX`, `en-US`, `pt-BR`, `fr-FR`, `de-DE`).

---

## 53. Failure Injection

Pruebas de inyección de fallos: medios ausentes, audios corruptos, caídas de Whisper/TTS, disco lleno, timeouts, cancelaciones y fallos de validación.

---

## 54. Determinism Test

Ejecutar dos veces el mismo proyecto y comparar hashes de timeline, subtítulos, overlays, audio, JSX y manifiesto.

---

## 55. Language Isolation Test

Modificar exclusivamente la voz en inglés no deberá alterar los artefactos de español, portugués, francés ni alemán.

---

## 56. Regression Test

$$\text{Nuevos tests} = \text{GREEN}, \quad \text{Tests existentes (712)} = \text{GREEN}$$

---

## 57. Prohibición de romper tests

No se permite:
- eliminar tests existentes;
- desactivar suites;
- aumentar arbitrariamente timeouts;
- marcar tests como skip;
- debilitar aserciones;
- modificar valores esperados únicamente para hacer pasar la suite.

---

## 58. Type Safety

El proyecto deberá compilar sin errores de TypeScript (`npm run build` / `typecheck`) antes del cierre.

---

## 59. Lint

Ejecución del linter existente sin introducir nuevos errores o advertencias.

---

## 60. Build

Compilación completa del proyecto con resultado exitoso (`SUCCESS`).

---

## 61. Validation Gate

Paso obligatorio previo al cierre:
$$\text{TESTS} + \text{TYPECHECK} + \text{LINT} + \text{BUILD} + \text{E2E} + \text{DETERMINISM} \implies 100\% \text{ PASS}$$

---

## 62. Performance

Procesamiento escalable por bloques y streams evitando cargar videos completos en RAM.

---

## 63. Seguridad

Validación de paths y nombres de archivo contra Path Traversal (`../`) y ejecución segura de comandos.

---

## 64. Logging

Logs estructurados en formato JSON sin credenciales, tokens ni secretos privados.

---

## 65. Errores

Los errores indicarán fase, operación, runId, idioma, mediaId y artefacto afectado.

---

## 66. Observabilidad

Capacidad de auditar qué fase falló, por qué, qué artefacto produjo y si es recuperable.

---

## 67. Documentation of Code

Cada módulo nuevo documentará su propósito, entradas, salidas, invariantes y modos de fallo.

---

## 68. Implementation Order

Implementación estricta por milestones:
- **Milestone 0 — Baseline:** tests, build, lint, typecheck.
- **Milestone 1 — Contracts:** types, interfaces, schemas, configuration, errors, artifacts.
- **Milestone 2 — Media Intelligence:** footage classifier, media analysis, B-Roll matching.
- **Milestone 3 — Vlog Editing:** jump cuts, silence removal, micro-crossfades, dynamic punch-ins.
- **Milestone 4 — Localization:** language model, localization contracts, TTS abstraction, voice generation.
- **Milestone 5 — Adaptive Pacing:** segment alignment, visual adaptation, voice timing, language-specific timelines.
- **Milestone 6 — Visual Localization:** multilingual subtitles, travel overlays, maps, Geo-Badges, Polaroid.
- **Milestone 7 — Audio / Style / Export:** voice, music, SFX, ducking, styles, reframing, JSX.
- **Milestone 8 — Orchestration:** DAG, cache, artifacts, resume, retry, cancel, atomic commit, CLI, MCP.
- **Milestone 9 — Full Validation:** unit, integration, PBT, E2E, failure injection, determinism, language isolation, performance, regression.

---

## 69. Regla de avance

La IA no avanzará al siguiente milestone si el actual contiene tests fallidos, errores de tipos, bugs críticos conocidos o inconsistencias de contrato sin resolver.

---

## 70. Estado por milestone

Cada milestone concluirá con:
$$\text{IMPLEMENTED} + \text{TESTED} + \text{VALIDATED} + \text{DOCUMENTED}$$

---

## 71. Informe de cada milestone

Reporte formal de archivos creados, modificados, tests añadidos, tests pasados, estado de build y limitaciones conocidas.

---

## 72. No Fake Completion

Prohibido declarar funcionalidades completas si existen `TODO`, `FIXME`, stubs o placeholders en lógica requerida.

---

## 73. No Mock Production Logic

Los mocks se reservan exclusivamente para tests unitarios; prohibido simular motores de producción con mocks.

---

## 74. Feature Flags

Nuevas capacidades protegidas por flags hasta contar con valores de producción certificados.

---

## 75. Configuration Defaults

Toda configuración nueva documentará valor por defecto, validación, rango admisible y descripción.

---

## 76. Invalid Configuration

Configuraciones inválidas fallan de inmediato antes de iniciar cómputo pesado.

---

## 77. Versioning

Incremento formal de la versión del motor (`v3.5.0`) siguiendo la política semántica.

---

## 78. Migration

Estrategia de migración formal ante cualquier cambio de esquema preexistente.

---

## 79. Final Output

Estructura del paquete final:
```
output/
├── project/
├── audio/
├── subtitles/
├── jsx/
├── overlays/
├── metadata/
├── reports/
└── manifests/
```

---

## 80. Final Manifest

Manifiesto maestro con projectId, runId, engineVersion, configurationHash, productionHash, languages, artifacts y validation.

---

## 81. Definition of Done

El proyecto únicamente estará terminado cuando:
- [✓] Todos los contratos implementados
- [✓] Todos los módulos implementados
- [✓] Integración completa
- [✓] Offline operativo
- [✓] ES-MX, ES-ES, EN-US, EN-GB, PT-BR, FR-FR, DE-DE
- [✓] Jump cuts y Punch-ins
- [✓] A/B-Roll y B-Roll matching
- [✓] TTS y Localization
- [✓] Adaptive pacing y Subtitles
- [✓] Geo-Badges, Maps y Polaroid
- [✓] Audio, Styles y Reframing
- [✓] JSX, MCP y CLI
- [✓] Cache, Resume, Retry, Cancellation y Atomic output
- [✓] Determinism y Validation
- [✓] Unit tests, Integration tests, PBT y E2E
- [✓] Failure injection, Performance, Security y Regression
- [✓] Baseline tests siguen verdes (712/712)
- [✓] Nuevos tests verdes
- [✓] Typecheck verde
- [✓] Lint verde
- [✓] Build verde

---

## 82. Criterio absoluto de éxito

$$\text{EXISTING FUNCTIONALITY} + \text{NEW VLOG FUNCTIONALITY} + \text{MULTILINGUAL PRODUCTION}$$
$$+ \text{OFFLINE EXECUTION} + \text{AFTER EFFECTS EXPORT} + \text{MCP/CLI} + \text{FULL VALIDATION} = \text{PRODUCTION READY}$$

---

## 83. Orden final de trabajo de la IA

Instrucción operacional definitiva:
1. Auditar repositorio.
2. Ejecutar baseline.
3. Leer documentos técnicos existentes.
4. Construir matriz de requisitos.
5. Detectar contradicciones.
6. Reportar contradicciones antes de implementar.
7. Implementar contratos.
8. Implementar módulos por milestone.
9. Ejecutar tests después de cada cambio.
10. Integrar.
11. Ejecutar E2E.
12. Ejecutar regresión completa.
13. Corregir errores.
14. Repetir hasta 100% GREEN.
15. Ejecutar build/lint/typecheck.
16. Generar reporte final.
17. No declarar terminado hasta cumplir Definition of Done.

---

## 84. Regla final para la IA implementadora

- No improvisar.
- No simplificar requisitos sin autorización.
- No eliminar funcionalidad existente.
- No sustituir componentes reales por mocks.
- No introducir dependencias comerciales obligatorias.
- No romper compatibilidad con v3.4.0.
- No modificar tests para ocultar regresiones.
- No continuar silenciosamente ante contradicciones.
- No declarar terminado mientras exista una funcionalidad requerida sin implementar o un test obligatorio fallando.

El objetivo es producir una implementación real, integrada, reproducible, offline, testeada y lista para producción.

---

## 85. CIERRE

Este documento constituye el contrato maestro de implementación para la expansión Vlog / Documentary / Multilingual.

A partir de este punto:
$$\text{DOCUMENTACIÓN} \longrightarrow \text{STOP} \longrightarrow \text{IMPLEMENTACIÓN} \longrightarrow \text{TESTING} \longrightarrow \text{INTEGRACIÓN} \longrightarrow \text{VALIDACIÓN} \longrightarrow \text{PRODUCTION READY}$$

No se deberán crear nuevos documentos de requisitos salvo que durante la implementación aparezca una contradicción real, una dependencia técnica no especificada o una decisión arquitectónica que requiera aprobación.
