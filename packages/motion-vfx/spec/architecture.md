# 🏗️ Especificación de Arquitectura del Sistema

**Estándar:** `Autonomous After Effects MCP — Architecture Specification`  
**Referencia:** `REQ-001`, `REQ-004`, `REQ-015`, `REQ-022`  

---

## 1. Topología del Sistema y Separación de Responsabilidades

El sistema divide estrictamente el flujo de trabajo en 5 capas desacopladas e independientes:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. AI AGENT INTENT LAYER                                    │
│    Emite intenciones creativas, briefs y selecciones de     │
│    estilo mediante llamadas MCP estructuradas.              │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ 2. CANONICAL PROJECT IR & PLANNING LAYER                    │
│    La IR es la única fuente de verdad inmutable.            │
│    Aplica validación de esquemas Zod, resolución espacial, │
│    evaluación temporal t -> FrameState y optimización DAG.  │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ 3. CONSTRAINTS & QA ARBITRATION LAYER                       │
│    Verifica zonas seguras, colisiones OCR, detección de     │
│    fotogramas negros y convergencia de auto-reparación.     │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ 4. DETERMINISTIC COMPILER LAYER                             │
│    Genera código AST ExtendScript para After Effects,       │
│    Apple FCPXML o CMX 3600 EDL de forma 100% reproducible.  │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ 5. RUNTIME & STATE RECONCILIATION LAYER                     │
│    Ejecuta el código en Adobe After Effects vía IPC Socket, │
│    mide los límites reales de capas y reconcilia el estado. │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Invariantes de Seguridad Arquitectónica

1. **Prohibición de JSX Arbitrario:** La IA nunca tiene acceso a `eval()`, scripts JSX directos o comandos del sistema no autorizados. Todo comando pasa por validación de esquemas y es compilado por `AfterEffectsJSXCompiler`.
2. **Desacoplamiento de Runtime:** Si After Effects se bloquea o desconecta, el estado de la IR no sufre corrupción. La capa de transacciones aborta o revierte al último hash válido.
