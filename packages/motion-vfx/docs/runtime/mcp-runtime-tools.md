# Catálogo de Herramientas y Recursos MCP del Runtime (Fase 18)

## 🛠️ Herramientas MCP
1. `create_project`: Crea un nuevo proyecto persistido y genera `rev_000001`.
2. `open_project`: Carga, valida y abre una sesión de proyecto.
3. `save_project`: Guarda con control de concurrencia optimista.
4. `close_project`: Cierra una sesión liberando locks.
5. `get_project_status`: Obtiene status, HEAD y health report.
6. `list_project_revisions`: Lista el historial completo de revisiones.
7. `diff_project_revisions`: Emite un diff semántico y estructural entre dos revisiones.
8. `restore_project_revision`: Restaura una revisión histórica de forma no destructiva.
9. `validate_project`: Ejecuta validación multi-capa sin mutar el proyecto.
10. `cancel_operation`: Cancela operaciones en curso mediante `CancellationToken`.

## 🌐 Recursos MCP
- `runtime://health`
- `runtime://projects`
- `capabilities://runtime`
- `project://{projectId}`
- `project://{projectId}/revisions`
- `project://{projectId}/diagnostics`
