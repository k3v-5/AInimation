# 📊 MATRIZ DE TRAZABILIDAD DE REQUISITOS
## VLOG INTELLIGENCE ENGINE (v3.5.x)
**Documento:** `docs/vlog-expansion/25-REQUIREMENTS-TRACEABILITY.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Matriz de Trazabilidad End-to-End

| ID Requisito | Descripción Funcional | Doc Ref | Módulo / Código | Archivo de Test | Estado |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **VLOG-JC-001** | Eliminar silencios con duración estrictamente $> 250\text{ms}$ | `05` | `VlogJumpCutEngine.ts` | `boundaries.test.ts` | ⬜ Pendiente |
| **VLOG-JC-002** | Conservar silencios con duración $\le 250\text{ms}$ ($249\text{ms}$, $250\text{ms}$) | `05` | `VlogJumpCutEngine.ts` | `boundaries.test.ts` | ⬜ Pendiente |
| **VLOG-JC-003** | Protección fonética de palabras habladas con margen de $40\text{ms}$ pre/post | `05` | `VlogJumpCutEngine.ts` | `VlogJumpCutEngine.test.ts` | ⬜ Pendiente |
| **VLOG-JC-004** | Micro-crossfades acústicos de $10\text{ms}$ con protección adaptativa | `03`, `05` | `VlogJumpCutEngine.ts` | `boundaries.test.ts` | ⬜ Pendiente |
| **VLOG-JC-005** | Continuidad temporal estricta en la línea de salida ($\text{outStart}_{i+1} == \text{outEnd}_i$) | `03`, `05` | `VlogJumpCutEngine.ts` | `property-based.test.ts` | ⬜ Pendiente |
| **PUNCH-001** | Modulación dinámica de escala visual ($100\% \to 115\% \to 100\%$) | `06` | `DynamicPunchIn.ts` | `DynamicPunchIn.test.ts` | ⬜ Pendiente |
| **PUNCH-002** | Disparo de punch-in por pico de energía acústica $\text{RMS} \ge 0.70$ | `06` | `DynamicPunchIn.ts` | `DynamicPunchIn.test.ts` | ⬜ Pendiente |
| **PUNCH-003** | Disparo de punch-in por palabras de énfasis o preguntas (`?`, `!`) | `06` | `DynamicPunchIn.ts` | `DynamicPunchIn.test.ts` | ⬜ Pendiente |
| **PUNCH-004** | Cooldown obligatorio de $2.50\text{s}$ entre punch-ins consecutivos | `06` | `DynamicPunchIn.ts` | `DynamicPunchIn.test.ts` | ⬜ Pendiente |
| **PUNCH-005** | Abstracción de `FocusPoint` normalizado $[0.0, 1.0]$ | `06` | `DynamicPunchIn.ts` | `property-based.test.ts` | ⬜ Pendiente |
| **BROLL-001** | Clasificación de metraje en A-Roll, B-Roll, Timelapse y Acción | `07` | `FootageClassifier.ts` | `FootageClassifier.test.ts` | ⬜ Pendiente |
| **BROLL-002** | Generación de catálogo estructurado `ShotManifest.json` inmutable | `07` | `FootageClassifier.ts` | `FootageClassifier.test.ts` | ⬜ Pendiente |
| **BROLL-003** | Emparejamiento semántico transcript $\leftrightarrow$ B-roll por tags y afinidad | `08` | `SemanticBrollMatcher.ts` | `SemanticBrollMatcher.test.ts` | ⬜ Pendiente |
| **TTS-001** | Abstracción desacoplada de proveedor de voz `TTSProvider` | `09` | `TTSProvider.ts` | `MultilingualTTS.test.ts` | ⬜ Pendiente |
| **TTS-002** | Síntesis neuronal local en ES, EN, PT, FR, DE a $0 coste de APIs | `09` | `PiperTTSProvider.ts` | `MultilingualTTS.test.ts` | ⬜ Pendiente |
| **PACE-001** | Resolución de contratos temporales y adaptación de ritmo por idioma | `11` | `AdaptivePacingEngine.ts` | `AdaptivePacingEngine.test.ts` | ⬜ Pendiente |
| **PACE-002** | Acotación estricta de dilatación de voz en $[0.95\text{x}, 1.05\text{x}]$ | `11` | `AdaptivePacingEngine.ts` | `AdaptivePacingEngine.test.ts` | ⬜ Pendiente |
| **OVERLAY-001** | Primitivas declarativas: `GeoBadge`, `RouteMap`, `PolaroidFreeze` | `12` | `TravelOverlays.ts` | `TravelOverlays.test.ts` | ⬜ Pendiente |
| **AE-001** | Compilación ExtendScript JSX universal (bilingüe Español/Inglés) | `13` | `AEVlogCompiler.ts` | `AEIntegration.test.ts` | ⬜ Pendiente |
| **MCP-001** | Exposición de herramientas de vlog en el servidor MCP JSON-RPC | `14` | `mcp/registry.ts` | `MCPVlogTools.test.ts` | ⬜ Pendiente |
| **DET-001** | Determinismo absoluto: 100 corridas consecutivas idénticas | `17` | Transversal | `DeterminismSuite.test.ts` | ⬜ Pendiente |
| **REG-001** | Cero regresiones sobre los 712 tests existentes de v3.4.0 | `18` | Transversal | `npm run conformance` | ⬜ Pendiente |
