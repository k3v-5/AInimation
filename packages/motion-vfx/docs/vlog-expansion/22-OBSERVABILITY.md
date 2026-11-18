# 👁️ OBSERVABILIDAD, LOGS ESTRUCTURADOS Y MÉTRICAS
## VLOG INTELLIGENCE ENGINE (v3.5.x)
**Documento:** `docs/vlog-expansion/22-OBSERVABILITY.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Definir el sistema de logging estructurado, telemetría local de métricas editoriales (tiempo ahorrado, ratio de compresión, número de punch-ins) y diagnóstico de ejecución sin dependencias de servicios externos ni envío de datos fuera de la máquina del usuario.

## 2. Alcance
- Emisión de logs estructurados en formato JSON Lines (`transcript.jsonl` / `vlog-telemetry.json`).
- Estadísticas agregadas en `JumpCutStatistics`: tiempo ahorrado, porcentaje de compresión y conteo de cortes.
- Diagnóstico de decisiones editoriales trazable por cada segmento.

## 3. No Alcance
- No incluye telemetría remota (no hay envío de datos a la nube).

## 4. Entradas
- Eventos del pipeline editorial.

## 5. Salidas
- Objetos estadísticos y logs de auditoría en disco local.

## 6. Interfaces
```typescript
export interface JumpCutStatistics {
  readonly originalDurationSec: number;
  readonly editedDurationSec: number;
  readonly savedTimeSec: number;
  readonly compressionRatioPct: number;
  readonly totalCuts: number;
  readonly totalPunchIns: number;
  readonly preservedWordsCount: number;
}
```

## 7. Configuración
- Niveles de log: `DEBUG`, `INFO`, `WARN`, `ERROR`.

## 8. Algoritmo
- Cálculo de métricas:
  $$\text{savedTimeSec} = \text{originalDurationSec} - \text{editedDurationSec}$$
  $$\text{compressionRatioPct} = \left( \frac{\text{savedTimeSec}}{\text{originalDurationSec}} \right) \times 100$$

## 9. Reglas de Negocio
- **RN-OBS01:** Toda ejecución exitosa debe emitir su objeto `JumpCutStatistics` completo.

## 10. Invariantes
- **INV-OBS01:** $0 \le \text{compressionRatioPct} \le 100$.

## 11. Casos Normales
- Grabación de 100s editada a 70s: Emite `savedTimeSec = 30.0` y `compressionRatioPct = 30.0%`.

## 12. Casos Límite
- 0 cortes realizados: `savedTimeSec = 0.0`, `compressionRatioPct = 0.0%`.

## 13. Errores
- Errores de escritura de log degradan a salida estándar sin abortar la edición.

## 14. Recuperación
- Captura de fallos de I/O en logs.

## 15. Determinismo
- Mismo montaje produce exactamente las mismas métricas estadísticas.

## 16. Rendimiento
- Cálculo de métricas en $< 0.1\text{ms}$.

## 17. Dependencias
- Ninguna externa.

## 18. Compatibilidad
- Logs en UTF-8 estándar.

## 19. Seguridad
- Los logs no almacenan contraseñas ni contenido de audio binario.

## 20. Tests
- Tests unitarios de métricas en `src/tests/automation/vlog/observability/ObservabilityMetrics.test.ts`.

## 21. Fixtures
- Estadísticas esperadas para los fixtures golden.

## 22. Golden Tests
- Verificación de campos en `statistics`.

## 23. Integración
- Incrustado en `VlogJumpCutResult`.

## 24. Definition of Done
- Métricas estadísticas calculadas y testeadas con 100% de precisión.
