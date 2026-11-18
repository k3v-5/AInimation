# 🔌 MODEL CONTEXT PROTOCOL (MCP) INTEGRATION
## ESPECIFICACIÓN TÉCNICA DEL MÓDULO (v3.5.x)
**Documento:** `docs/vlog-expansion/14-MCP-INTEGRATION.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Exponer las capacidades de la capa Vlog Intelligence en el servidor Model Context Protocol (MCP) mediante herramientas estructuradas JSON-RPC (`vlog_generate_jump_cut_plan`, `vlog_classify_footage`, `vlog_match_broll`, `vlog_localize_speech`, `vlog_compile_master`), permitiendo que cualquier agente de IA opere el montaje completo con llamadas atómicas e inmutables.

## 2. Alcance
- Definición de esquemas Zod para argumentos de cada herramienta MCP.
- Registro en `McpRegistry` del servidor existente sin romper las 34 herramientas de v3.4.0.
- Retorno de respuestas JSON estructuradas con diagnósticos claros.

## 3. No Alcance
- No reemplaza las herramientas MCP existentes de v3.4.0 (`create_project`, `apply_viral_caption_style`, etc.).
- No requiere autenticación cloud de terceros.

## 4. Entradas
- Llamadas JSON-RPC tipadas con argumentos estructurados acordes a los esquemas Zod de cada tool.

## 5. Salidas
- Objetos JSON de respuesta con contenido `content: [{ type: "text", text: JSON.stringify(...) }]`.

## 6. Interfaces
```typescript
export interface VlogJumpCutMCPArgs {
  readonly videoPath: string;
  readonly transcriptText?: string;
  readonly totalDurationSec?: number;
  readonly silenceThresholdSec?: number;
  readonly normalScale?: number;
  readonly punchInScale?: number;
}
```

## 7. Configuración
- Configuración centralizada heredada de `DEFAULT_VLOG_JUMP_CUT_CONFIG`.

## 8. Algoritmo
1. Validar argumentos con Zod Schema.
2. Invocar el motor correspondiente (`VlogJumpCutEngine`, `FootageClassifier`, etc.).
3. Serializar resultado a JSON estructurado y retornar payload MCP.

## 9. Reglas de Negocio
- **RN-MCP01 (Cero Ruptura):** La adición de herramientas vlog debe ser aditiva y no modificar las herramientas previas de v3.4.0.

## 10. Invariantes
- **INV-MCP01:** Toda herramienta MCP retorna `{ content: [...] }` válido según el SDK oficial de MCP.

## 11. Casos Normales
- Un agente IA invoca `vlog_generate_jump_cut_plan` y recibe el desglose de cortes y punch-ins en formato JSON.

## 12. Casos Límite
- Argumentos inválidos: Retorna `isError: true` con mensaje de validación descriptivo.

## 13. Errores
- `McpValidationError`: Error de validación en parámetros.

## 14. Recuperación
- Captura de excepciones con bloque `try/catch` centralizado en cada handler MCP.

## 15. Determinismo
- Mismos argumentos producen la misma respuesta JSON exacta.

## 16. Rendimiento
- Despacho de la herramienta en $< 5\text{ms}$ (tiempo de ejecución del motor aparte).

## 17. Dependencias
- `@modelcontextprotocol/sdk`, `zod`.

## 18. Compatibilidad
- Compatible con clientes MCP (Claude Desktop, IDEs, Antigravity, Custom Agents).

## 19. Seguridad
- Validación estricta de parámetros para prevenir comandos de shell arbitrarios.

## 20. Tests
- Tests de integración en `src/tests/automation/vlog/mcp/MCPVlogTools.test.ts`.

## 21. Fixtures
- Payloads JSON de ejemplo para cada tool.

## 22. Golden Tests
- Verificación de esquema JSON-RPC.

## 23. Integración
- Registrado en `src/mcp/registry.ts`.

## 24. Definition of Done
- Herramientas MCP registradas y testeadas con 100% de éxito.
