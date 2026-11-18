# Protocolos de Recuperación ante Fallos y Crashes (Fase 18)

## 1. Recuperación a Nivel de Almacenamiento

- **Integridad de Escrituras Atómicas:**
  `FileProjectStore` escribe en `target.json.tmp.${timestamp}` y realiza `fsync` antes de llamar a `fs.rename`.
  Si el sistema operativo o proceso colapsa durante la escritura, el archivo destino original permanece íntegro y sin corrupción.

- **Detección de Proyectos Corruptos:**
  Al abrir un proyecto, se validan los esquemas Zod (`ProjectFileSchema`, `RevisionSchema`) y el hash SHA-256 canónico. Ante anomalías se lanza `CorruptedProjectError`.

## 2. Recuperación a Nivel de Workflows

- Tras cada paso completado con éxito, se persiste un `WorkflowCheckpoint`.
- En caso de interrupción forzosa (kill de proceso, excepción no recuperable), el agente o sistema puede invocar `resumeWorkflow`:
  1. Carga el último `WorkflowCheckpoint` confirmado.
  2. Restaura las variables de contexto e ID de revisión.
  3. Ejecuta exclusivamente los pasos pendientes del grafo DAG.
