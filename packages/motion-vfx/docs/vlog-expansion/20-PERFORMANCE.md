# ⚡ PRESUPUESTOS DE RENDIMIENTO Y OPTIMIZACIÓN
## VLOG INTELLIGENCE ENGINE (v3.5.x)
**Documento:** `docs/vlog-expansion/20-PERFORMANCE.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Establecer los presupuestos cuantitativos de latencia máxima, consumo de memoria RAM y estrategias de caché para asegurar que la planificación editorial opere en milisegundos sin bloquear el hilo principal de Node.js.

## 2. Alcance
- Presupuestos de tiempo de CPU por submódulo.
- Límite máximo de memoria: $< 512\text{ MB}$ de Heap para proyectos de hasta 2 horas.
- Estrategia de caché para `ShotManifest.json` y perfiles de audio.

## 3. No Alcance
- No controla el tiempo de renderizado de After Effects (depende del motor C++ de Adobe y hardware GPU).

## 4. Entradas
- Metadatos de proyectos de gran escala (hasta 5,000 palabras y 500 clips).

## 5. Salidas
- Tiempos de ejecución dentro de los umbrales garantizados.

## 6. Interfaces
```typescript
export interface PerformanceBudget {
  readonly maxJumpCutPlanTimeMs: number;
  readonly maxBrollMatchTimeMs: number;
  readonly maxPacingResolutionTimeMs: number;
  readonly maxMemoryHeapMb: number;
}
```

## 7. Configuración
```typescript
export const DEFAULT_PERFORMANCE_BUDGET: PerformanceBudget = {
  maxJumpCutPlanTimeMs: 50.0,
  maxBrollMatchTimeMs: 30.0,
  maxPacingResolutionTimeMs: 25.0,
  maxMemoryHeapMb: 512.0,
};
```

## 8. Algoritmo
- Algoritmos lineales $\mathcal{O}(N)$ y de búsqueda binaria $\mathcal{O}(\log N)$ para matching de intervalos temporales.
- Evitar clonaciones profundas innecesarias en bucles críticos mediante estructuras inmutables compartidas.

## 9. Reglas de Negocio
- **RN-PERF01:** Ninguna operación pura de planificación en memoria puede exceder los $100\text{ms}$.

## 10. Invariantes
- **INV-PERF01:** La complejidad temporal de `VlogJumpCutEngine` es estrictamente $\mathcal{O}(N \log N)$ debido a la ordenación inicial y $\mathcal{O}(N)$ en la pasada de corte.

## 11. Casos Normales
- Procesamiento de video de 10 minutos con 300 silencios: Ejecutado en $< 15\text{ms}$.

## 12. Casos Límite
- Metraje extremo de 4 horas con 10,000 silencios: Ejecutado en $< 80\text{ms}$ con $< 120\text{ MB}$ de RAM.

## 13. Errores
- `PerformanceBudgetExceededError` (en suites de benchmark).

## 14. Recuperación
- Indexación previa mediante árboles de intervalos (*Interval Trees*) si $N > 10,000$.

## 15. Determinismo
- Las optimizaciones de rendimiento no afectan la salida determinista.

## 16. Rendimiento
- Núcleo temático de este documento.

## 17. Dependencias
- `process.hrtime` / `performance.now()`.

## 18. Compatibilidad
- Rendimiento uniforme en Windows, macOS y Linux.

## 19. Seguridad
- Prevención de ataques de denegación de servicio por expresiones regulares catastróficas (*ReDoS*).

## 20. Tests
- Tests de benchmark de rendimiento en `src/tests/automation/vlog/performance/VlogPerformanceBenchmark.test.ts`.

## 21. Fixtures
- Proyectos sintéticos masivos con 5,000 palabras y 1,000 silencios.

## 22. Golden Tests
- Tiempos de ejecución medidos y comparados contra presupuesto.

## 23. Integración
- Verificado en el runner de conformidad.

## 24. Definition of Done
- Benchmarks pasando holgadamente por debajo de los presupuestos máximos.
