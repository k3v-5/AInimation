# Control de Versiones, Ramificación y Grafo de Revisiones (Fase 18)

## 1. Identificadores de Revisión Criptográficos (`RevisionId`)

Cada revisión posee un identificador inmutable y determinista generado por:
$$\text{revisionId} = \text{"rev\_"} + \text{SHA256}(\text{projectId} + \text{parentRevisionId} + \text{canonicalProjectHash} + \text{operationHash})[0..16]$$

## 2. Grafo Acíclico Dirigido (`RevisionGraph`)

El historial de un proyecto no es lineal, sino un DAG que soporta ramificaciones concurrentes:
- `getRoot()`: obtiene la revisión génesis.
- `getHead()`: obtiene la revisión más reciente en la rama activa.
- `getChildren(revId)`: ramas que derivan de una revisión dada.
- `getAncestors(revId)` / `getDescendants(revId)`: cálculo topológico de linaje.
- `isAncestor(a, b)`: comprueba si la revisión `a` es antepasada de `b`.

## 3. Diff, Patch y Reversibilidad

- **`RevisionDiff`:**
  Compara dos revisiones y emite cambios estructurados con operaciones `add`, `remove`, `replace` y `move`.

- **`RevisionPatch`:**
  Cumple la ley de reversibilidad matemática estricta:
  $$\text{reversePatch}(\text{applyPatch}(P, \Delta), \Delta) \equiv P$$

- **Operaciones No Destructivas:**
  - `restoreRevision(targetId)`: crea una nueva revisión en HEAD con el contenido de la revisión histórica seleccionada.
  - `undoRevision(targetId)`: crea una nueva revisión aplicando el parche inverso de la revisión seleccionada.

## 4. Fusión de Ramas (`RevisionMerge`)

- Fusión 3-way entre `base`, `left` y `right`.
- Si las modificaciones inciden en propiedades disjuntas (ej. audio vs texto), se fusionan automáticamente sin intervención humana.
- Si ambas ramas alteran la misma propiedad con valores divergentes, se emite un objeto `RevisionConflict` explícito sin resoluciones silenciosas.
