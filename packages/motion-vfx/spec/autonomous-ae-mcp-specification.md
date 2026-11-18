# 📜 Especificación Maestra Normativa: Autonomous After Effects MCP

**Estándar:** `ISO/IEC Autonomous Audiovisual Production Protocol — v3.0-MASTER`  
**Autor:** DeepMind / Antigravity AI Engineering  
**Estado:** `NORMATIVE SPECIFICATION (MANDATORY)`  
**Última Actualización:** `2026-08-27`  

---

## 0. Objetivo y Alcance del Sistema

El sistema proporciona una interfaz de protocolo **MCP (Model Context Protocol)** y un **Compilador de Producción Audiovisual** para que agentes de Inteligencia Artificial puedan inspeccionar, planificar, mutar, validar, ejecutar, reconciliar, verificar y exportar proyectos complejos de Adobe After Effects de forma autónoma.

### 🔒 Invariantes Fundamentales:
1. **Determinismo Multinivel (Niveles A, B, C, D):** Reproducibilidad matemática de estados y líneas de tiempo.
2. **Idempotencia Transaccional:** Cada operación compleja posee un `operation_id` y se ejecuta bajo un sobre ACID (`BEGIN -> VALIDATE -> APPLY -> VERIFY -> COMMIT`).
3. **Reversibilidad Criptográfica:** Todo cambio fallido ejecuta un rollback estricto donde $\text{Hash}_{\text{before}} \equiv \text{Hash}_{\text{after\_rollback}}$.
4. **La IR es la Única Fuente de Verdad:** After Effects es un runtime de destino; la IA nunca interactúa con APIs gráficas ni emite JSX arbitrario sin pasar por el compilador formal.
5. **Operación 100% Offline:** Cero dependencias de APIs en la nube para análisis acústico, transcripción o evaluación de calidad.

```
                  ┌──────────────────────────────┐
                  │           AI AGENT           │
                  └──────────────┬───────────────┘
                                 │ Intent / Tool Calls
                                 ▼
                  ┌──────────────────────────────┐
                  │          MCP SERVER          │
                  └──────────────┬───────────────┘
                                 │ Canonical Commands
                                 ▼
                  ┌──────────────────────────────┐
                  │     CANONICAL PROJECT IR     │
                  │ (Single Source of Truth)     │
                  ├──────────────────────────────┤
                  │ • Validation  • Constraints  │
                  │ • Planning    • Evaluation   │
                  │ • QA Suite    • Auto-Repair  │
                  └──────────────┬───────────────┘
                                 │ AST Generation
                                 ▼
                  ┌──────────────────────────────┐
                  │         AE COMPILER          │
                  └──────────────┬───────────────┘
                                 │ JSON-RPC IPC / ExtendScript
                                 ▼
                  ┌──────────────────────────────┐
                  │        AE LIVE BRIDGE        │
                  └──────────────┬───────────────┘
                                 │ IPC Socket / CLI
                                 ▼
                  ┌──────────────────────────────┐
                  │     ADOBE AFTER EFFECTS      │
                  └──────────────┬───────────────┘
                                 │ Inspection / Bounds
                                 ▼
                  ┌──────────────────────────────┐
                  │  RECONCILIATION & QA ENGINE  │
                  └──────────────────────────────┘
```

---

## 1. Niveles de Determinismo (Definición Formal)

Para evitar la falacia de exigir *"determinismo binario byte-a-byte"* en códecs de video con aceleración por hardware (NVENC/CUDA), el sistema define **4 Niveles Formales de Determinismo**:

| Nivel | Nombre | Definición Matemática | Garantía de Certificación |
|---|---|---|---|
| **Nivel A** | **Determinismo Lógico** | $\text{IR}_1 \equiv \text{IR}_2 \implies \text{Hash}(\text{IR}_1) = \text{Hash}(\text{IR}_2) \land \text{Plan}(\text{IR}_1) \equiv \text{Plan}(\text{IR}_2)$ | **100% Obligatorio** (SHA-256) |
| **Nivel B** | **Determinismo Estructural** | Mismo grafo de capas, orden $Z$, tiempos de entrada/salida ($in/out$), valores de keyframes y matrices afines $2\text{D}/3\text{D}$. | **100% Obligatorio** ($\epsilon \le 10^{-10}$) |
| **Nivel C** | **Determinismo Perceptual** | Fotogramas renderizados idénticos bajo métricas perceptuales objetivas ($\text{SSIM} \ge 0.999$, $\Delta E_{00} \le 0.5$). | **100% Obligatorio en Render** |
| **Nivel D** | **Determinismo Binario** | Emisión de bytes idénticos en disco ($\text{Hash}(\text{File}_1) = \text{Hash}(\text{File}_2)$). | **Garantizado en JSX, JSON y WAV; Opcional en MP4** |

---

## 2. Los 6 Grupos de Herramientas MCP

El servidor MCP expone 6 familias de herramientas sin permitir operaciones peligrosas ni acceso arbitrario al shell:

1. **`Discovery`:** `get_capabilities()`, `get_engine_info()`, `get_ae_info()`, `get_schema_version()`.
2. **`Inspection`:** `inspect_project()`, `inspect_composition()`, `inspect_layer()`, `inspect_asset()`, `inspect_qa()`.
3. **`Planning`:** `create_plan()`, `validate_plan()`, `estimate_render()`, `dry_run()`.
4. **`Mutation`:** `create_composition()`, `create_layer()`, `modify_layer()`, `set_property()`, `add_keyframe()`, `apply_effect()`.
5. **`High-Level Intelligence`:** `analyze_media()`, `sync_to_beats()`, `auto_reframe()`, `generate_captions()`, `create_cover()`, `add_sfx()`.
6. **`Production`:** `begin_transaction()`, `commit_transaction()`, `rollback_transaction()`, `run_qa()`, `fix_qa_issues()`, `render_preview()`, `export_omni()`.

---

## 3. Puertas de Certificación (Certification Gates)

Para que el motor sea declarado **`LEVEL 5 — PRODUCTION CERTIFIED`**, debe superar las **10 Puertas de Conformidad**:

```
Gate 01: IR / Source of Truth        [PASS]
Gate 02: Determinism (Levels A, B, C)[PASS]
Gate 03: Idempotency & Versioning    [PASS]
Gate 04: Transactions & Rollback     [PASS]
Gate 05: MCP Contract & Tool Schema  [PASS]
Gate 06: AE Bridge & Reconciliation  [PASS]
Gate 07: Constraints Engine          [PASS]
Gate 08: QA & Auto-Repair            [PASS]
Gate 09: Security Sandbox & Offline  [PASS]
Gate 10: Golden E2E Project Pipeline [PASS]
```

Cualquier falla en una puerta crítica detiene la certificación y genera un reporte de no-conformidad estructurado.
