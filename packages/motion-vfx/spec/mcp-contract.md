# 🔌 Especificación del Contrato MCP (Model Context Protocol)

**Estándar:** `Autonomous After Effects MCP — Protocol & Tools Contract`  
**Referencia:** `REQ-015`, `REQ-016`, `REQ-017`, `REQ-018`  

---

## 1. Familias de Herramientas Declarativas

El servidor MCP expone exclusivamente herramientas fuertemente tipadas agrupadas en 6 categorías:

### 1. Discovery (`ae_discovery_*`)
- `get_capabilities()`: Retorna matriz de soporte de hardware, GPU, After Effects y códecs.
- `get_engine_info()`: Versión del motor, esquemas soportados y límites de recursos.
- `get_schema_version()`: Retorna el versionado semántico de la IR.

### 2. Inspection (`ae_inspect_*`)
- `inspect_project(fields, pagination)`: Consulta el estado proyectado del proyecto sin desbordar el contexto del agente.
- `inspect_composition(compId)`: Retorna metadatos, capas y pistas de una composición.
- `inspect_layer(layerId)`: Retorna propiedades y keyframes de una capa específica.
- `inspect_qa()`: Retorna el informe más reciente de la suite de calidad visual.

### 3. Planning (`ae_plan_*`)
- `create_plan(brief)`: Transforma un requerimiento creativo en un grafo acíclico dirigido (DAG) de producción.
- `validate_plan(plan)`: Comprueba restricciones, recursos y validez sintáctica/semántica.
- `dry_run(plan)`: Simula la ejecución completa con `dry_run: true` sin mutar After Effects ni la IR.

### 4. Mutation (`ae_mutate_*`)
- `create_composition()`, `create_layer()`, `modify_layer()`, `set_property()`, `add_keyframe()`, `apply_effect()`.
- Todas las mutaciones requieren un `operation_id` y `expected_version` para garantizar idempotencia y versionado optimista.

### 5. High-Level Intelligence (`ae_intelligence_*`)
- `analyze_media()`: Inspección acústica y de metadatos.
- `sync_to_beats()`: Detección de transientes y alineación rítmica.
- `auto_reframe()`: Encuadre 16:9 a 9:16 guiado por puntos focales.
- `generate_captions()`: Transcripción y subtitulado viral palabra por palabra.
- `create_cover()`: Generación de portada 9:16 con título 3D.

### 6. Production (`ae_production_*`)
- `begin_transaction()`, `commit_transaction()`, `rollback_transaction()`.
- `run_qa()`, `fix_qa_issues()`, `render_preview()`, `export_omni()`.
