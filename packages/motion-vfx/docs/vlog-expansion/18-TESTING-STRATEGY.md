# 🧪 ESTRATEGIA DE PRUEBAS DE 7 CAPAS
## VLOG INTELLIGENCE ENGINE (v3.5.x)
**Documento:** `docs/vlog-expansion/18-TESTING-STRATEGY.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Definir la metodología, pirámide de pruebas, políticas de no regresión y frameworks de validación formal que garantizan la integridad matemática y funcional del sistema en cada fase de desarrollo.

## 2. Alcance
- Pirámide de 7 capas:
  1. Unit Tests (Pruebas unitarias de función pura).
  2. Integration Tests (Flujos inter-módulo).
  3. Boundary Tests (Pruebas de límites temporales estrictos).
  4. Invariant Tests (Verificación matemática de contratos).
  5. Property-Based Tests (`fast-check` generativo con 100+ iteraciones).
  6. Golden Tests (Snapshots SHA-256 verificados).
  7. Regression Tests (Blindaje de los 712 tests existentes de v3.4.0).

## 3. No Alcance
- No se admiten aserciones débiles (`toBeDefined()`, `toBeTruthy()`); todas las comprobaciones deben verificar valores numéricos exactos o snapshots completos.

## 4. Entradas
- Suites de pruebas automatizadas ejecutadas mediante `node --test` y `npm run conformance`.

## 5. Salidas
- Reporte formal de conformidad emitido en `reports/production-certification.json`.

## 6. Interfaces
- Directivas del test runner estándar de Node.js (`describe`, `it`, `assert`).

## 7. Configuración
- Configuración de tolerancia flotante $\epsilon \le 10^{-10}$.

## 8. Algoritmo
- Ejecución secuencial de tests con verificación de build previa (`npm run build && npm test`).

## 9. Reglas de Negocio
- **RN-TEST01 (Prohibido Mutar Tests para Enmascarar Fallos):** Los tests representan la especificación formal inmutable.
- **RN-TEST02 (Cero Skips / Cero Mocks que Oculten Errores):** Todo test debe ejecutarse activamente.

## 10. Invariantes
- **INV-TEST01:** 100% pass rate obligatorio para cualquier commit a `main`.

## 11. Casos Normales
- Ejecución de `npm run conformance` con todos los gates certificados en verde.

## 12. Casos Límite
- Detección de regresiones de 1 milisegundo en timestamps: El test falla inmediatamente.

## 13. Errores
- Fallo de aserción con diff estructurado.

## 14. Recuperación
- Diagnóstico mediante logs de traza.

## 15. Determinismo
- Las suites de tests son deterministas y no dependen de la hora ni de la red.

## 16. Rendimiento
- Ejecución de la suite completa en $< 10\text{ segundos}$.

## 17. Dependencias
- `node:test`, `node:assert/strict`, `fast-check`.

## 18. Compatibilidad
- Ejecución idéntica en PowerShell (Windows), Bash (Linux/macOS).

## 19. Seguridad
- Aislamiento de directorios temporales de test con limpieza automática `rmSync`.

## 20. Tests
- La propia suite de pruebas.

## 21. Fixtures
- Carpeta `fixtures/` con inputs dorados.

## 22. Golden Tests
- Verificación de hash SHA-256 sobre archivos generados.

## 23. Integración
- Pipeline de integración continua (`scripts/run-conformance.mjs`).

## 24. Definition of Done
- 0 tests fallidos, 0 skips, 0 regresiones sobre v3.4.0.
