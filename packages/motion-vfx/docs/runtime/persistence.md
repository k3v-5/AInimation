# Persistencia y Serialización Canónica (Fase 18)

## ProjectEnvelope
Todo proyecto persistido reside en un contenedor estructurado:
```typescript
interface ProjectEnvelope<T = unknown> {
  schemaVersion: string;
  engineVersion: string;
  projectId: string;
  revisionId: string;
  createdAt: string;       // Metadata operacional
  updatedAt: string;       // Metadata operacional
  contentHash: string;     // SHA-256 de canonicalizeProject(project)
  project: T;              // Canonical Project IR serializada
  metadata: ProjectMetadata;
  migrations?: MigrationMetadata;
}
```

## Serialización Canónica
- Claves de objetos ordenadas lexicográficamente de forma recursiva.
- Arrays preservan su orden exacto sin reordenamientos.
- Normalización de números: $-0 \to +0$, verificación de números finitos.
- UTF-8 estricto sin BOM.
- Exclusión total de timestamps y datos volátiles de la IR y del cálculo de `contentHash`.
