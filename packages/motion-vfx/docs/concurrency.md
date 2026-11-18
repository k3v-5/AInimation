# Modelo de Concurrencia Optimista y Fusión de Ramas (Fase 18)

## 1. Concurrencia Optimista por Revisión Base

Para evitar condiciones de carrera entre múltiples agentes o procesos:
1. Toda mutación enviada por una sesión debe declarar su `expectedRevisionId`.
2. Al recibir la mutación, el motor consulta la revisión HEAD actual en el almacén.
3. Si $\text{currentHead} \neq \text{expectedRevisionId}$, la operación es rechazada de inmediato arrojando un error tipado `RevisionConflictError`.

## 2. Estrategia de Ramificación y Reintento

Cuando una sesión sufre un conflicto de concurrencia:
- El agente puede abrir una rama independiente (`createRevision` con `parentRevisionId` específico).
- Ambas ramas pueden ser analizadas e integradas posteriormente mediante `RevisionMerge.merge(base, left, right)`.
- Si las modificaciones son ortogonales, el merge es automático; de lo contrario, el agente recibe los conflictos exactos para formular una propuesta de resolución.
