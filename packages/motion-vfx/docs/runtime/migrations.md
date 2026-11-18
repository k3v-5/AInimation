# Sistema de Migraciones de Esquemas (Fase 18)

## Pipeline de Migraciones
- Cadenas secuenciales: $0.1.0 \to 0.2.0 \to 1.8.0$.
- **Idempotencia:** `migrate(migrate(p)) === migrate(p)`.
- **Atomicidad:** Si una etapa intermedia falla, no se muta el proyecto original.
- **Detección de incompatibilidad:** Esquemas desconocidos o futuros disparan `UnsupportedProjectVersionError`.
