# 🏷️ ESTRATEGIA DE VERSIONADO Y MIGRACIÓN
## VLOG INTELLIGENCE ENGINE (v3.5.x)
**Documento:** `docs/vlog-expansion/23-VERSIONING.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Establecer las políticas de versionado semántico (SemVer 2.0.0), compatibilidad hacia atrás y estrategias de migración de esquemas de datos (`ShotManifest`, `VlogEditPlan`) para permitir la evolución continua del motor sin romper flujos de trabajo existentes.

## 2. Alcance
- Asignación de números de versión a cada entrega de la capa vlog (`v3.5.0` a `v3.5.4`).
- Versionado de esquemas JSON (`schemaVersion: "1.0.0"`).
- Políticas de deprecación formal con preaviso de 2 versiones menores.

## 3. No Alcance
- No afecta el versionado de dependencias externas.

## 4. Entradas
- Cambios de código y esquemas.

## 5. Salidas
- Versión formal del paquete y etiquetas Git.

## 6. Interfaces
```typescript
export interface SchemaMigrationStrategy<TInput, TOutput> {
  readonly fromVersion: string;
  readonly toVersion: string;
  migrate(input: TInput): TOutput;
}
```

## 7. Configuración
- Versión actual de la capa: `3.5.0-alpha`.

## 8. Algoritmo
- Si se detecta un `ShotManifest` con versión menor anterior, ejecutar migrador hacia la versión actual antes de consumirlo.

## 9. Reglas de Negocio
- **RN-VER01 (SemVer Estricto):** Todo cambio no retrocompatible exige incremento de versión mayor.

## 10. Invariantes
- **INV-VER01:** Todo esquema serializado contiene un campo `schemaVersion`.

## 11. Casos Normales
- Incremento de `v3.5.0` (Fase 1: Jump Cut) a `v3.5.1` (Fase 2: Classifier).

## 12. Casos Límite
- Apertura de un manifiesto antiguo: Migrado limpiamente en memoria.

## 13. Errores
- `UnsupportedSchemaVersionError`.

## 14. Recuperación
- Fallback con sugerencia de actualización.

## 15. Determinismo
- Las migraciones son deterministas y reversibles.

## 16. Rendimiento
- Migración de esquema en $< 1\text{ms}$.

## 17. Dependencias
- `semver` o comparación lexicográfica estructurada.

## 18. Compatibilidad
- Garantizada hacia atrás.

## 19. Seguridad
- Verificación previa de esquemas migrantes mediante Zod.

## 20. Tests
- Tests de migración en `src/tests/automation/vlog/versioning/SchemaMigration.test.ts`.

## 21. Fixtures
- Manifiestos de versiones históricas.

## 22. Golden Tests
- Verificación de paridad post-migración.

## 23. Integración
- Incrustado en cargadores de archivos JSON.

## 24. Definition of Done
- Políticas y migraciones de versión documentadas y probadas.
