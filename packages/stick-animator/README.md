# `@ianimation/stick-animator` (`stykanimate-mcp`)

Motor headless **2D de figuras articuladas (*stick figures*) con Cinemática Inversa (IK)** y servidor Model Context Protocol (`stykanimate-mcp`) basado en StykAnimate, compatible con formatos `.styk`, `.stkz`, `.stykmov`, Pivot Animator (`.piv`, `.stk`) y exportadores HTML5/MP4.

> Migrado íntegro de `E:\Disco F\Dev\StictAnimator` (**100% de archivos fuente intactos**, 0 corrupción).

---

## Estructura del Paquete

- [`stykanimate-mcp/`](stykanimate-mcp/): Servidor MCP en Node.js (`>=20`) + códec Python para `.piv`/`.stk`.
  - Documentación optimizada para LLM: [`stykanimate-mcp/llms.txt`](stykanimate-mcp/llms.txt)
  - Entrypoint MCP: [`stykanimate-mcp/src/index.js`](stykanimate-mcp/src/index.js)
- [`cli/`](cli/): 7 scripts de generación y renderización offline (`create-animation-cli.js`, `export-html.js`, `render_mp4.py`, `run-live-test.js`, etc.).
- [`examples/`](examples/): Proyectos de ejemplo listos para abrir e inspeccionar (`cyber_samurai.styk`, `mono_animado.styk`, `stickman_pose.styk`).

---

## 26 Herramientas MCP Verificadas

| Categoría | Herramientas | Cantidad |
| :--- | :--- | :---: |
| **Capacidad** | `capabilities` | 1 |
| **Proyecto** | `project_open`, `project_close`, `project_describe`, `project_validate`, `project_save`, `project_timeline`, `project_seek` | 7 |
| **Figuras** | `figure_list`, `figure_describe`, `figure_add`, `figure_duplicate`, `figure_delete`, `figure_transform` | 6 |
| **Poses e IK** | `pose_evaluate`, `pose_set`, `pose_ik_set`, `pose_set_ik`, `pose_reset` | 5 |
| **Capas y Estilo** | `layer_list`, `layer_edit`, `style_set` | 3 |
| **Timeline** | `keyframe_edit`, `keyframe_timing` | 2 |
| **Historial** | `history_undo`, `history_redo` | 2 |

---

## Ejecución y Tests

```powershell
# Arrancar servidor MCP stdio
node packages\stick-animator\stykanimate-mcp\src\index.js

# Ejecutar suite de pruebas unitarias
node --test packages\stick-animator\stykanimate-mcp\test\*.test.mjs
```
