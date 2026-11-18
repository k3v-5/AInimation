# 🧪 MATRIZ EXHAUSTIVA DE PRUEBAS
## VLOG INTELLIGENCE ENGINE (v3.5.x)
**Documento:** `docs/vlog-expansion/26-TEST-MATRIX.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Clasificación y Tipología de Pruebas

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MATRIZ GLOBAL DE TESTING (7 CAPAS)                   │
├─────────────────────────────────────────────────────────────────────────┤
│ 1. Unit Tests            │ Funciones puras, cálculo de crossfades, etc. │
│ 2. Boundary Tests        │ Silencios en 0ms, 249ms, 250ms, 251ms, etc.  │
│ 3. Integration Tests     │ Orquestación VAD + Transcript + JumpCut.     │
│ 4. Property-Based (PBT)  │ Invariantes matemáticos con fast-check (100x)│
│ 5. Golden Tests          │ Comparación de hash SHA-256 contra snapshot. │
│ 6. Determinism Tests     │ 100 corridas consecutivas idénticas.         │
│ 7. Regression Tests      │ 712 tests existentes de v3.4.0 inalterados.  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Matriz Detallada de Pruebas por Módulo

| Categoría | Archivo de Prueba | Escenario / Caso de Prueba | Método / Herramienta | Criterio de Aprobación |
| :--- | :--- | :--- | :--- | :--- |
| **Boundary** | `boundaries.test.ts` | Silencio de $0\text{ms}$ a $250\text{ms}$ | `node:test` + aserciones | Silencio conservado íntegramente |
| **Boundary** | `boundaries.test.ts` | Silencio de $251\text{ms}$ a $2000\text{ms}$ | `node:test` + aserciones | Silencio eliminado del timeline |
| **Boundary** | `boundaries.test.ts` | Silencio al inicio ($t=0$) y fin ($t=T$) | `node:test` + aserciones | Eliminación limpia sin desbordar $[0, T]$ |
| **Unit** | `DynamicPunchIn.test.ts` | Disparo de punch-in por energía RMS $\ge 0.70$ | `node:test` | Escala cambia a $1.15$ durante $[1.2\text{s}, 6.0\text{s}]$ |
| **Unit** | `DynamicPunchIn.test.ts` | Cooldown de $2.5\text{s}$ entre punch-ins | `node:test` | Bloquea punch-ins secundarios en la ventana |
| **Unit** | `VlogJumpCutEngine.test.ts` | Protección de palabras con colchón de $40\text{ms}$ | `node:test` | Ninguna palabra intersecta con corte de silencio |
| **Unit** | `VlogJumpCutEngine.test.ts` | Micro-crossfade de $10\text{ms}$ en cada empalme | `node:test` | Duración de fade $\le \text{segmentDuration}/2$ |
| **Property** | `property-based.test.ts` | 100 timelines aleatorios sintéticos | `fast-check` | $\text{outStart}_{i+1} \ge \text{outEnd}_i \land T_{\text{out}} \le T_{\text{src}}$ |
| **Golden** | `golden-fixture.test.ts` | Procesamiento de `golden-vlog-input.json` | SHA-256 Hash check | Hash idéntico al snapshot de referencia |
| **Determinism**| `determinism.test.ts` | 100 ejecuciones sucesivas del mismo input | Bucle de 100 iteraciones | `deepStrictEqual(Run[0], Run[99])` |
| **Regression** | `npm run conformance` | Ejecución de toda la suite histórica | Conformance runner | **712 / 712 tests existentes PASS** |
| **Performance**| `performance.test.ts` | Procesamiento de video de 1 hora (3600s) | `performance.now()` | Tiempo total $< 50\text{ms}$ |

---

## 3. Protocolo de Ejecución de la Matriz

1. **Pre-condición:** `npm run build` debe completar sin advertencias de compilación (`tsc`).
2. **Ejecución de Suites:**
   ```bash
   node --test build/tests/automation/vlog/**/*.test.js
   ```
3. **Ejecución de Conformidad Global:**
   ```bash
   npm run conformance
   ```
4. **Veredicto:** Solo si el 100% de los casos de esta matriz y las 712 pruebas existentes pasan en verde, se aprueba la entrega de la fase.
