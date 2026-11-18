# Especificación Maestra de Expansión Vlog Multilingüe

**Documento:** `00-MASTER-SPECIFICATION.md`  
**Versión:** `1.0.0`  
**Plataforma base:** Motor audiovisual v3.4.0  
**Estado:** Especificación técnica  
**Clasificación:** Fuente Única de Verdad (SSOT)  

---

## 1. Propósito

Este documento define los requisitos arquitectónicos, funcionales, técnicos, temporales, de integración, calidad y validación para la expansión del motor audiovisual hacia la automatización de producción de:

- Vlogs de viaje.
- Vlogs de estilo de vida.
- Documentales ligeros.
- Contenido A-Roll/B-Roll.
- Versiones localizadas en múltiples idiomas.
- Contenido long-form y sus posteriores derivados sociales.

La expansión deberá integrarse sobre el motor existente sin alterar el comportamiento previamente validado de la versión v3.4.0.

---

## 2. Principio fundamental

La expansión deberá considerarse una capa de inteligencia editorial situada sobre el núcleo existente de edición, timeline, audio, tipografía, reencuadre, estilos y exportación.

La arquitectura resultante deberá mantener esta separación:

```
                    MOTOR v3.4.0
                         │
        ┌────────────────┴────────────────┐
        │                                 │
   Core Editing                    Existing Automation
        │                                 │
        └────────────────┬────────────────┘
                         │
                         ▼
              VLOG INTELLIGENCE LAYER
                         │
        ┌────────────────┼────────────────┐
        │                │                │
     Speech          Footage          Editorial
   Intelligence     Intelligence      Planning
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
                  Localization
                         │
                         ▼
                 Adaptive Pacing
                         │
                         ▼
                 Travel Graphics
                         │
                         ▼
                  AE / MCP / DSL
```

---

## 3. Objetivos

### 3.1. Objetivo principal
Permitir que el motor transforme material audiovisual bruto en un plan de edición de vlog estructurado y posteriormente exportable a After Effects, reduciendo al mínimo la intervención humana.

### 3.2. Objetivos secundarios
El sistema deberá ser capaz de:
- Detectar y eliminar silencios editoriales.
- Preservar palabras y unidades lingüísticas.
- Generar jump cuts.
- Aplicar punch-ins dinámicos.
- Clasificar material A-Roll/B-Roll.
- Asociar B-Roll con contenido hablado.
- Generar locuciones locales en múltiples idiomas.
- Adaptar el montaje a diferentes duraciones lingüísticas.
- Generar gráficos de viaje.
- Mantener sincronización audiovisual.
- Generar un plan de edición determinista.
- Exportar el resultado a After Effects.
- Operar sin APIs cloud obligatorias.
- Mantener la suite existente de tests completamente verde.

---

## 4. No objetivos

La expansión NO tendrá como responsabilidad inicial:
- Publicar directamente en YouTube.
- Publicar directamente en TikTok.
- Gestionar cuentas de redes sociales.
- Comprar recursos multimedia.
- Generar material de vídeo sintético.
- Sustituir completamente un sistema NLE.
- Renderizar vídeo dentro del motor de planificación.
- Reemplazar After Effects.
- Utilizar servicios cloud obligatorios.
- Tomar decisiones legales sobre material protegido.
- Realizar reconocimiento biométrico persistente de personas.

Estas capacidades podrán estudiarse en futuras versiones y deberán contar con especificaciones independientes.

---

## 5. Alcance funcional

La expansión estará compuesta por los siguientes subsistemas:

- **VLOG-01** Speech Analysis
- **VLOG-02** Jump Cut Engine
- **VLOG-03** Dynamic Punch-In
- **VLOG-04** Footage Classifier
- **VLOG-05** Semantic B-Roll Matcher
- **VLOG-06** Multilingual TTS
- **VLOG-07** Localization Pipeline
- **VLOG-08** Adaptive Pacing
- **VLOG-09** Travel Overlays
- **VLOG-10** After Effects Integration
- **VLOG-11** MCP Integration
- **VLOG-12** DSL Integration
- **VLOG-13** Validation / Testing

---

## 6. Principios arquitectónicos obligatorios

### 6.1. Determinismo
Con:
$$\text{misma entrada} + \text{misma configuración} + \text{misma versión} + \text{misma semilla}$$
el resultado deberá ser idéntico.

Esto incluye:
- segmentos.
- timestamps.
- scores.
- decisiones editoriales.
- orden de clips.
- IDs deterministas.
- JSON de salida.
- metadata.

### 6.2. Separación de responsabilidades
Los componentes deberán dividirse en:
$$\text{ANALYSIS} \longrightarrow \text{METADATA} \longrightarrow \text{DECISION} \longrightarrow \text{EDIT PLAN} \longrightarrow \text{EXPORT} \longrightarrow \text{RENDER}$$

- Un analizador NO deberá modificar directamente el timeline.
- Un exportador NO deberá tomar decisiones editoriales.
- Un renderer NO deberá interpretar requisitos semánticos.

### 6.3. Offline-first
Las funcionalidades principales deberán poder ejecutarse sin acceso a Internet.
No podrá existir una API cloud como dependencia obligatoria de:
- transcripción.
- clasificación.
- TTS.
- análisis temporal.
- generación de EditPlan.
- generación de JSX.

### 6.4. Coste recurrente
El diseño deberá perseguir:
$$\text{API recurrente obligatoria} = \$0$$

Podrán existir dependencias locales con consumo de CPU/GPU. Los costes computacionales deberán documentarse, pero no se considerarán costes de API.

### 6.5. No regresión
La implementación deberá preservar el comportamiento de v3.4.0. La suite existente deberá permanecer:
$$712 / 712 \text{ PASS (100\%)}$$
Cualquier regresión deberá bloquear la entrega.

---

## 7. Arquitectura de alto nivel

El pipeline maestro será:

```
RAW MEDIA
   │
   ▼
MEDIA INGESTION
   │
   ├── Video Metadata
   ├── Audio Metadata
   └── Frame Metadata
   │
   ▼
SPEECH ANALYSIS
   │
   ├── VAD
   ├── Transcript
   ├── Word Timing
   └── Energy
   │
   ▼
FOOTAGE ANALYSIS
   │
   ├── Shot Detection
   ├── A-Roll/B-Roll
   ├── Motion
   ├── Face/Focus
   └── Semantic Metadata
   │
   ▼
EDITORIAL PLANNER
   │
   ├── Silence Removal
   ├── Jump Cuts
   ├── Punch-ins
   ├── B-Roll Matching
   └── Transitions
   │
   ▼
LOCALIZATION
   │
   ├── Translation
   ├── Local TTS
   └── Timing
   │
   ▼
ADAPTIVE PACING
   │
   ├── Duration Reconciliation
   ├── B-Roll Reallocation
   └── Voice Timing Adjustment
   │
   ▼
TRAVEL GRAPHICS
   │
   ├── Geo Badge
   ├── Route Map
   ├── Polaroid
   └── Timestamp
   │
   ▼
EDIT PLAN
   │
   ├── AE JSX
   ├── MCP
   └── DSL
```

---

## 8. Unidad fundamental: EditPlan

La expansión deberá utilizar un modelo declarativo común denominado `EditPlan`.

Conceptualmente:

```typescript
interface EditPlan {
  version: string;
  source: MediaReference;
  duration: number;

  tracks: Track[];
  segments: EditSegment[];

  audio: AudioPlan;
  graphics: GraphicsPlan;
  localization?: LocalizationPlan;

  metadata: EditMetadata;
}
```

El `EditPlan` será la interfaz principal entre inteligencia editorial y exportación.

---

## 9. Fuente de verdad temporal

Toda la expansión utilizará la convención:
$$[t_{\text{start}}, t_{\text{end}})$$

Se deberá evitar cualquier semántica temporal alternativa dentro de los nuevos módulos. Los timestamps deberán representarse con una precisión suficiente para preservar la exactitud del motor existente. No se permitirá redondear prematuramente timestamps durante el procesamiento. El redondeo sólo podrá realizarse durante una etapa explícita de exportación/render.

---

## 10. Identidad de objetos

Todos los objetos relevantes deberán poseer IDs estables:
- `source`
- `shot`
- `speechSegment`
- `word`
- `editSegment`
- `punchIn`
- `overlay`
- `audioEvent`

Los IDs deberán ser:
- deterministas.
- reproducibles.
- únicos dentro de su namespace.

No se utilizarán UUID aleatorios si ello rompe el determinismo.

---

## 11. Configuración

Las reglas configurables deberán estar centralizadas. No se permitirán valores de negocio dispersos como magic numbers.

Ejemplo:
```json
{
  "silenceThreshold": 0.25,
  "crossfadeDuration": 0.010,
  "punchInScale": 1.15
}
```

La configuración deberá poder serializarse. El `EditPlan` deberá registrar la configuración efectiva utilizada para producirlo, directa o indirectamente mediante una referencia de configuración/versionado.

---

## 12. Política de decisiones

Cada decisión automática importante deberá ser trazable.

Ejemplo:
```
Silence 14
duration = 0.42s
threshold = 0.25s
decision = REMOVE
reason = THRESHOLD
```

Esto permitirá debugging, auditoría, tests, explicación al usuario y comparación entre versiones.

---

## 13. Sistema de scoring

Cuando exista scoring, deberá:
- Tener rango documentado (ej. $\text{score} \in [0, 100]$ o $[0.0, 1.0]$).
- Tener significado definido.
- Tener pesos documentados.
- Ser determinista.
- Tener tests de límites.

No se permitirá un score sin contrato semántico.

---

## 14. Tolerancia a fallos

La ausencia de información opcional no deberá provocar automáticamente el fallo del pipeline.

Ejemplo:
$$\text{No face tracking} \longrightarrow \text{usar FocusPoint por defecto } (0.5, 0.5)$$

Pero los datos obligatorios inválidos deberán generar errores explícitos. El sistema distinguirá:
- `FATAL`
- `RECOVERABLE`
- `WARNING`
- `INFO`

---

## 15. Política de degradación

Cuando una capacidad avanzada no esté disponible, el sistema deberá utilizar una estrategia de fallback definida.

Ejemplo:
$$\text{Eye Tracking disponible} \longrightarrow \text{usar ojos}$$
$$\text{Eye Tracking no disponible} \longrightarrow \text{usar cara}$$
$$\text{Face Detection no disponible} \longrightarrow \text{usar centro del frame } (0.5, 0.5)$$

Los fallbacks deberán ser deterministas.

---

## 16. Idiomas objetivo iniciales

La expansión deberá contemplar inicialmente:
- `es-MX`
- `es-ES`
- `en-US`
- `en-GB`
- `pt-BR`
- `fr-FR`
- `de-DE`

La arquitectura deberá permitir agregar idiomas sin modificar el core editorial. Un idioma nuevo deberá implementarse mediante configuración/adaptadores cuando sea técnicamente posible.

---

## 17. Arquitectura de localización

El idioma deberá ser un atributo del contenido localizado, no una propiedad rígida del proyecto entero.

Conceptualmente:
```
Master Edit
   │
   ├── es-MX
   ├── es-ES
   ├── en-US
   ├── en-GB
   ├── pt-BR
   ├── fr-FR
   └── de-DE
```

Cada variante deberá conservar referencia al mismo contenido fuente cuando sea posible.

---

## 18. Política de audio

El sistema deberá mantener separados:
- `Original Voice`
- `Music`
- `SFX`
- `Localized Voice`
- `Ambient Audio`

Esto permitirá posteriormente activar/desactivar pistas por idioma. El ducking deberá operar sobre relaciones de pistas declaradas y no mediante modificaciones destructivas.

---

## 19. Política de vídeo

El montaje deberá distinguir:
- `A-ROLL`
- `B-ROLL`
- `TIMELAPSE`
- `ACTION`
- `GRAPHICS`
- `OVERLAY`

Cada tipo deberá poder ser identificado en metadata.

---

## 20. Compatibilidad con el motor existente

Los nuevos módulos deberán reutilizar, cuando sea apropiado:
- `Matrix2D`.
- `Property<T>`.
- `timeline` existente.
- interpolación Bezier.
- transiciones existentes.
- audio analysis existente.
- Whisper bridge existente.
- reframing existente.
- generadores JSX existentes.
- MCP existente.
- DSL existente.

No se deberá duplicar funcionalidad ya implementada.

---

## 21. Compatibilidad con After Effects

La expansión deberá continuar utilizando la estrategia existente de:
$$\text{Universal Match Names}$$
en lugar de depender exclusivamente de nombres localizados de interfaz. El JSX deberá ser compatible con instalaciones soportadas de After Effects en español e inglés.

---

## 22. MCP

Cada capacidad que deba ser controlable externamente deberá exponerse mediante herramientas MCP sólo después de que su contrato interno esté estabilizado.

Las herramientas MCP deberán:
- validar inputs.
- devolver resultados estructurados.
- devolver errores estructurados.
- respetar determinismo.
- no esconder fallos.
- ser versionables.

---

## 23. DSL

Las capacidades deberán poder representarse declarativamente.

Ejemplo conceptual:
```typescript
vlog.jumpCut({
  silenceThreshold: 0.25
});

vlog.punchIn({
  scale: 1.15
});

vlog.localize({
  languages: ["es-MX", "en-US", "pt-BR"]
});
```

La sintaxis definitiva será definida en `15-DSL-INTEGRATION.md`.

---

## 24. Observabilidad

Cada ejecución deberá poder generar información de diagnóstico suficiente para responder:
- ¿Qué detectó?
- ¿Qué decidió?
- ¿Por qué lo decidió?
- ¿Qué configuración utilizó?
- ¿Qué versión utilizó?
- ¿Qué elementos modificó?
- ¿Qué falló?
- ¿Qué fallback utilizó?

Los logs deberán evitar información sensible innecesaria.

---

## 25. Reproducibilidad

Una ejecución deberá poder reconstruirse mediante un paquete de ejecución que incluya, como mínimo:
- `Engine Version`
- `Module Versions`
- `Configuration`
- `Input Manifest`
- `Analysis Metadata`
- `Deterministic Seed`
- `EditPlan Version`

Esto permitirá reproducir errores en cualquier máquina.

---

## 26. Rendimiento

La arquitectura deberá favorecer:
- procesamiento incremental.
- caching.
- reutilización de análisis.
- procesamiento paralelo cuando sea seguro.
- separación CPU/GPU.
- evitar recalcular información idéntica.

Los objetivos numéricos concretos de rendimiento se definirán en `20-PERFORMANCE.md`.

---

## 27. Cache

Los análisis costosos deberán poder almacenarse:
- Whisper transcript
- VAD
- shot detection
- face detection
- semantic embeddings
- TTS timing

La cache deberá invalidarse cuando cambien los inputs relevantes o la versión del algoritmo.

---

## 28. Seguridad

El sistema deberá tratar los archivos multimedia y metadata como entradas no confiables. Deberá validar:
- rutas.
- extensiones.
- tamaños.
- metadata.
- JSON.
- timestamps.
- dimensiones.
- valores numéricos.

No se deberá ejecutar contenido arbitrario recibido desde un archivo multimedia o metadata.

---

## 29. Calidad numérica

Los cálculos temporales y geométricos deberán respetar las tolerancias matemáticas existentes del motor. No se introducirán comparaciones inconsistentes entre módulos. Cuando sea necesaria una tolerancia:
$$\epsilon \le 1.0 \times 10^{-10}$$
deberá estar definida explícitamente.

---

## 30. Testing

Cada módulo deberá contar con:
- Unit Tests
- Boundary Tests
- Integration Tests
- Property-Based Tests
- Golden Tests
- Determinism Tests
- Failure Tests
- Regression Tests

Cuando corresponda también:
- Performance Tests
- End-to-End Tests

---

## 31. Regla de regresión global

Antes de comenzar cualquier implementación:
$$\text{Baseline: } 712 / 712 \text{ tests PASS}$$

Después de cada módulo:
$$\text{Existing: } 712 / 712 \text{ PASS} \quad + \quad \text{New: } 100\% \text{ PASS}$$

La cantidad exacta de tests nuevos será determinada por cada documento de módulo.

---

## 32. Prohibiciones de implementación

La IA programadora NO deberá:
- modificar tests existentes sólo para hacerlos pasar.
- eliminar tests.
- marcar tests como skipped.
- introducir TODO para requisitos obligatorios.
- introducir dependencias cloud sin aprobación documental.
- introducir valores mágicos.
- duplicar infraestructura existente.
- mezclar análisis con render.
- generar IDs aleatorios incompatibles con determinismo.
- ocultar errores.
- ignorar errores de entrada.
- modificar APIs existentes sin especificación de migración.

---

## 33. Versionado

La expansión deberá utilizar versionado semántico:
- `PATCH`: para correcciones sin cambio contractual.
- `MINOR`: para capacidades compatibles nuevas.
- `MAJOR`: para cambios incompatibles de contrato.

Los contratos de datos deberán tener además su propio versionado cuando sea necesario.

---

## 34. Trazabilidad

Cada requisito funcional deberá tener:
$$\text{Requirement ID} \longrightarrow \text{Specification} \longrightarrow \text{Implementation} \longrightarrow \text{Test} \longrightarrow \text{Validation}$$

No se considerará terminado un requisito que no pueda demostrar su implementación mediante tests. La matriz completa estará definida en `25-REQUIREMENTS-TRACEABILITY.md`.

---

## 35. Definition of Done global

La expansión sólo podrá considerarse completa cuando:

- [ ] Todos los documentos técnicos aprobados
- [ ] Todos los requisitos trazables
- [ ] Todos los módulos implementados
- [ ] Todos los contratos estabilizados
- [ ] 712 tests existentes PASS
- [ ] Nuevos tests 100% PASS
- [ ] Property tests PASS
- [ ] Golden tests PASS
- [ ] Determinism tests PASS
- [ ] Integration tests PASS
- [ ] E2E PASS
- [ ] Typecheck PASS
- [ ] Lint PASS
- [ ] Build PASS
- [ ] No APIs cloud obligatorias
- [ ] Documentación actualizada
- [ ] Changelog actualizado
- [ ] Versiones registradas
- [ ] Fallbacks documentados
- [ ] Errores documentados
- [ ] Performance validada
- [ ] Compatibilidad AE validada

---

## 36. Criterio de aceptación maestro

La expansión será aceptada únicamente si puede responder afirmativamente a las siguientes preguntas:

1. **Funcionalidad:** ¿El sistema puede producir un `EditPlan` válido para un vlog?
2. **Determinismo:** ¿La misma entrada produce el mismo resultado?
3. **Robustez:** ¿Los casos límite están definidos y testeados?
4. **Localización:** ¿Una misma producción puede generar variantes lingüísticas independientes?
5. **Offline:** ¿Las funciones críticas funcionan sin APIs cloud obligatorias?
6. **Integración:** ¿El resultado puede llegar al pipeline existente de After Effects?
7. **Regresión:** ¿La funcionalidad existente continúa funcionando exactamente como antes?
8. **Trazabilidad:** ¿Cada requisito puede rastrearse hasta su test?

Si alguna respuesta es negativa, la expansión no está terminada.

---

## 37. Documentos normativos derivados

Este documento delega el detalle técnico a los siguientes documentos:

- `01-ARCHITECTURE.md`
- `02-DATA-CONTRACTS.md`
- `03-TEMPORAL-MODEL.md`
- `04-AUDIO-SPEECH-PIPELINE.md`
- `05-VLOG-JUMP-CUT-ENGINE.md`
- `06-DYNAMIC-PUNCH-IN.md`
- `07-FOOTAGE-CLASSIFIER.md`
- `08-SEMANTIC-BROLL-MATCHER.md`
- `09-MULTILINGUAL-TTS.md`
- `10-LOCALIZATION-PIPELINE.md`
- `11-ADAPTIVE-PACING.md`
- `12-TRAVEL-OVERLAYS.md`
- `13-AFTER-EFFECTS-INTEGRATION.md`
- `14-MCP-INTEGRATION.md`
- `15-DSL-INTEGRATION.md`
- `16-ERROR-MODEL.md`
- `17-DETERMINISM.md`
- `18-TESTING-STRATEGY.md`
- `19-SECURITY-AND-SAFETY.md`
- `20-PERFORMANCE.md`
- `21-COMPATIBILITY.md`
- `22-OBSERVABILITY.md`
- `23-VERSIONING.md`
- `24-DEFINITION-OF-DONE.md`
- `25-REQUIREMENTS-TRACEABILITY.md`
- `26-TEST-MATRIX.md`

---

## 38. Estado del documento

**Documento:** `00-MASTER-SPECIFICATION.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

La implementación de cualquier módulo deberá comenzar únicamente cuando el documento correspondiente haya alcanzado el estado: `APPROVED`.

---

## 39. Regla final

Cuando exista una contradicción entre una implementación, una instrucción informal y esta especificación, deberá prevalecer la especificación aprobada.

Cuando exista una ambigüedad que no esté resuelta en la documentación, la IA no deberá inventar una decisión arquitectónica. Deberá:

$$\text{DETENER} \longrightarrow \text{IDENTIFICAR AMBIGÜEDAD} \longrightarrow \text{DOCUMENTARLA} \longrightarrow \text{RESOLVERLA} \longrightarrow \text{ACTUALIZAR SSOT} \longrightarrow \text{CONTINUAR}$$

> *La ausencia de una definición no constituye permiso para asumirla.*
