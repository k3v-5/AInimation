# Recuperación y Tolerancia a Fallos (Fase 18)

## Protocolo de Escrituras Atómicas
$$\text{project.json.tmp.<id>} \xrightarrow{\text{write \& flush}} \text{validate checksum} \xrightarrow{\text{atomic rename}} \text{project.json}$$

## Protocolo de Recovery
1. Si `project.json` es válido, los archivos `.tmp` huérfanos se limpian.
2. Si `project.json` está dañado pero existe un `.tmp` válido con checksum íntegro, se promueve automáticamente a HEAD.
3. Se registra el estado de operaciones en `JournalEntry` para auditoría y resolución de operaciones interrumpidas.
