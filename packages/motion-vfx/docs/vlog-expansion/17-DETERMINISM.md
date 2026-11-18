# 🎲 DETERMINISMO Y REPRODUCIBILIDAD ABSOLUTA
## VLOG INTELLIGENCE ENGINE (v3.5.x)
**Documento:** `docs/vlog-expansion/17-DETERMINISM.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Establecer las garantías matemáticas, algoritmos de generación pseudoaleatoria con semilla fija (*PRNG*), reglas de ordenación y protocolos de verificación que aseguran que cualquier ejecución del Vlog Intelligence Engine sea **100% reproducible bit a bit**, eliminando cualquier fuente de estocasticidad o variación temporal.

## 2. Alcance
- Prohibición de `Math.random()`, fechas dinámicas (`Date.now()`) no aisladas o iteraciones sobre sets no ordenados.
- Semillas deterministas configurables (`deterministicSeed: 42`).
- Ordenación canónica de colecciones antes de procesarlas.
- Cálculo de hash criptográfico SHA-256 sobre el resultado serializado.

## 3. No Alcance
- No cubre variaciones inherentes a hardware GPU en modelos neuronales externos no controlados por el motor (se mitigan mediante fijación de seeds en binarios locales).

## 4. Entradas
- Datos de entrada + `deterministicSeed: number`.

## 5. Salidas
- `EditPlan` con hash de verificación SHA-256 idéntico en cada ejecución.

## 6. Interfaces
```typescript
export interface DeterministicContext {
  readonly seed: number;
  readonly prng: () => number;
}
```

## 7. Configuración
- `deterministicSeed: 42` por defecto en todas las configuraciones.

## 8. Algoritmo
- Generador congruencial lineal (*Mulberry32* o *PCG*) inicializado con la semilla para cualquier selección estocástica determinista.
- Ordenación alfabética estricta de claves en objetos JSON antes de computar hashes.

## 9. Reglas de Negocio
- **RN-DET01:** $\text{Run}_1(I, S) \equiv \text{Run}_N(I, S)$ para cualquier $N$.

## 10. Invariantes
- **INV-DET01:** $\text{SHA256}(\text{Run}_1) == \text{SHA256}(\text{Run}_{100})$.

## 11. Casos Normales
- 100 ejecuciones sucesivas del pipeline de jump cut sobre el fixture golden producen exactamente el mismo hash SHA-256.

## 12. Casos Límite
- Sistemas operativos distintos (Windows vs Linux): Los flotantes se redondean a 3 decimales para evitar diferencias de redondeo de punto flotante en FPU.

## 13. Errores
- `NonDeterministicExecutionError`: Si un test detecta discrepancias en 2 corridas consecutivas.

## 14. Recuperación
- Diagnóstico mediante diff de objetos serializados.

## 15. Determinismo
- Principio rector de todo el documento.

## 16. Rendimiento
- Sobrecarga de generación PRNG $< 1\mu\text{s}$.

## 17. Dependencias
- `crypto` de Node.js nativo.

## 18. Compatibilidad
- Idéntico comportamiento en todas las plataformas soportadas.

## 19. Seguridad
- No se utilizan números pseudoaleatorios para propósitos criptográficos; solo para reproducibilidad audiovisual.

## 20. Tests
- Tests en `src/tests/automation/vlog/determinism/DeterminismSuite.test.ts`.

## 21. Fixtures
- Golden inputs con hashes precalculados.

## 22. Golden Tests
- 100 iteraciones sucesivas en bucle de integración.

## 23. Integración
- Aplicado en todos los generadores y planners.

## 24. Definition of Done
- 100 corridas consecutivas idénticas verificadas.
