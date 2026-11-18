# Especificación Técnica: Fase 18 — Production Runtime, Project Persistence, Validation & Deterministic Execution

**Versión:** `v1.8.0`  
**Estado:** ESPECIFICACIÓN TÉCNICA MAESTRA  
**Módulos Afectados:** `src/runtime/`, `src/schemas/`, `src/errors/`, `src/mcp/`  

---

## 0. Propósito y Alcance

La **Fase 18** convierte el motor audiovisual construido en las Fases 1–17 en una plataforma de producción persistente, transaccional, recuperable, validable y observable para agentes LLM durante sesiones de edición prolongadas.

### 0.1. Principio Rector:
> **El proyecto persistido es una representación serializada y versionada de la IR canónica. No existe un segundo modelo de proyecto.**  
> El runtime puede mantener cachés, índices y metadatos derivados, pero nunca puede convertirlos en la fuente de verdad.

---

## 1. Modelo de Datos y Estructuras Fundamentales

### 1.1. Project Envelope
Todo proyecto persistido reside en un contenedor estructurado `ProjectEnvelope`:

```typescript
export interface ProjectMetadata {
  name: string;
  description?: string;
  author?: string;
  tags?: string[];
  custom?: Record<string, unknown>;
}

export interface ProjectEnvelope<T = unknown> {
  schemaVersion: string;   // Ej. "1.8.0"
  engineVersion: string;   // Ej. "1.8.0"
  projectId: string;       // Identificador único del proyecto
  revisionId: string;      // Identificador de la revisión activa (ej. "rev_000001")
  createdAt: string;       // ISO 8601 (metadata operacional, excluida del contentHash)
  updatedAt: string;       // ISO 8601 (metadata operacional, excluida del contentHash)
  contentHash: string;     // SHA-256 de la serialización canónica de project
  project: T;              // IR Canónica serializada
  metadata: ProjectMetadata;
  migrations?: {
    originalSchemaVersion: string;
    migratedAt: string;
    steps: string[];
  };
}
```

### 1.2. Determinismo y Hashing Canónico
$$\text{canonicalizeProject}(P) = \text{DeterministicJSONString}(P)$$
$$\text{hashProject}(P) = \text{SHA-256}(\text{canonicalizeProject}(P))$$

Reglas de serialización canónica:
1. Ordenamiento lexicográfico recursivo de claves de objetos.
2. Preservación estricta del orden de arrays con significado posicional (capas, keyframes, eventos).
3. Normalización de números flotantes: $-0 \to +0$, verificación de números finitos (`!isFinite(n) \to` Error).
4. UTF-8 estricto, saltos de línea `\n`, sin BOM.
5. Exclusión absoluta de timestamps y datos de entorno (PID, hostname, timezone) dentro de la IR y del cálculo de `contentHash`.

---

## 2. Almacenamiento y Repositorio Desacoplado

### 2.1. Abstracción `StorageAdapter`
```typescript
export interface StorageAdapter {
  read(key: string): Promise<Uint8Array | null>;
  write(key: string, data: Uint8Array): Promise<void>;
  delete(key: string): Promise<void>;
  exists(key: string): Promise<boolean>;
  list(prefix?: string): Promise<string[]>;
}
```

- **`FileSystemStorageAdapter`**: Persistencia en disco local con sanitización estricta de rutas contra Path Traversal.
- **`MemoryStorageAdapter`**: Almacenamiento volátil ultra-rápido para pruebas y micro-evaluaciones.

### 2.2. Escrituras Atómicas y Tolerancia a Fallos
El guardado de proyectos sigue el protocolo seguro:
$$\text{project.tmp} \xrightarrow{\text{write \& flush}} \text{validate checksum} \xrightarrow{\text{atomic rename}} \text{project.json}$$

Si el proceso finaliza prematuramente, `project.json` anterior permanece $100\%$ íntegro.

---

## 3. Transacciones, Inmutabilidad y Concurrencia Optimista

### 3.1. Pipeline Transaccional
$$\text{BEGIN} \to \text{clone defensivo} \to \text{mutate} \to \text{validate} \to \text{compute hash} \to \text{persist} \to \text{COMMIT}$$
Ante cualquier excepción o fallo de validación:
$$\text{ROLLBACK} \to \text{estado previo intacto}$$

### 3.2. Concurrencia Optimista
Cada operación mutante requiere `baseRevisionId`. Si el estado actual es `rev_000007` y una mutación especifica `rev_000005`, la operación es rechazada con `RevisionConflictError`.

### 3.3. Restauración No Destructiva
Restaurar la revisión `rev_000001` cuando la actual es `rev_000003` genera una nueva revisión `rev_000004` con el contenido restaurado, preservando todo el árbol de revisiones.

---

## 4. Validación Multi-Capa y Salud del Runtime

El validador ejecuta 6 capas en orden estricto:
1. **Schema Validation**: Cumplimiento de esquema Zod y tipos primitivos.
2. **Resource Limits (`RuntimeLimits`)**: Límites contra proyectos patológicos (número de capas, keyframes, palabras de caption, profundidad de anidamiento).
3. **Referential Integrity**: Verificación de IDs de capas padre, assets referenciados y pistas existentes.
4. **Temporal Integrity**: Comprobación de duraciones, intervalos válidos $[t_{\text{start}}, t_{\text{end}})$ y framerates.
5. **Determinism Verification**: Verificación de repetibilidad $\text{Evaluate}(P, t)_1 \equiv \text{Evaluate}(P, t)_2$.
6. **IR Compatibility**: Compatibilidad semántica con motores de render y exportación.

---

## 5. Herramientas y Recursos MCP (Fase 18)

### Herramientas MCP:
1. `create_project`: Crea un nuevo proyecto y genera `rev_000001`.
2. `open_project`: Carga, valida y abre una sesión activa.
3. `save_project`: Persiste con control de concurrencia optimista.
4. `close_project`: Cierra la sesión activa liberando recursos y locks.
5. `get_project_status`: Consulta el estado, revisión actual, dirty state y health report.
6. `list_project_revisions`: Lista el historial completo de revisiones.
7. `diff_project_revisions`: Compara dos revisiones emitiendo un diff estructural y semántico.
8. `restore_project_revision`: Restaura una revisión previa generando una nueva revisión.
9. `validate_project`: Ejecuta validación multi-capa completa sin mutar el proyecto.
10. `cancel_operation`: Cancela de forma segura una operación asíncrona en curso mediante `CancellationToken`.

### Recursos MCP:
- `runtime://health`
- `runtime://projects`
- `project://{projectId}`
- `project://{projectId}/revisions`
- `project://{projectId}/diagnostics`
- `capabilities://runtime`
