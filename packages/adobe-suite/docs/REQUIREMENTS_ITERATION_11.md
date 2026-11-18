# Iteration 11: Asset Versioning and Hash-Based Cache Invalidation (Asset Graph)

## Objetivo
Implementar un sistema de versionado dinámico (Asset Graph) que detecte modificaciones manuales o externas en archivos físicos (e.g., si el usuario edita un PSD a mano) comparando hashes (SHA-256). Si un archivo fuente diverge, el motor DAG debe invalidar el caché de todos los nodos descendientes (propagación dirty) y re-renderizar/re-procesar solo las partes del flujo de trabajo afectadas.

## Acceptance Criteria (Criterios de Aceptación)

*   **AC-35: File Hashing & Storage:**
    *   Cada vez que `ArtifactManager` registra un artefacto (o un provider exporta uno), el motor debe calcular el SHA-256 del archivo físico y guardarlo en la columna `hash` de la tabla `assets`.
*   **AC-36: Asset Dependency Tracking (Asset Graph):**
    *   La base de datos (SQLite) debe tener una tabla `asset_dependencies` que relacione archivos (fuente -> destino).
    *   Durante la resolución de contexto del DAG (`${node.output}`), el motor debe detectar qué archivo físico sirvió como entrada para otra operación y registrar esta dependencia usando el `ProjectManager`.
*   **AC-37: Hash-Based Cache Invalidation (Dirty Flag Propagation):**
    *   Al ejecutar un nodo cacheado, el motor ya no debe confiar solo en `fs.existsSync`.
    *   Debe comparar el hash actual del archivo físico en disco con el último hash guardado en SQLite.
    *   Si los hashes difieren (Dirty State), el nodo *no* debe ser saltado (`SKIPPED`), sino que debe re-ejecutarse (`EXECUTING`).
    *   Además, esta invalidación debe propagarse hacia adelante: si un nodo padre re-ejecuta (o está dirty), sus nodos dependientes no pueden saltarse su ejecución aunque sus propios archivos de salida existan físicamente, forzando un re-render (p.ej. de After Effects si el PSD de Character Animator cambió).
