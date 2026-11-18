# 🔌 Especificación del Puente en Tiempo Real con After Effects (AE Live Bridge)

**Estándar:** `Autonomous After Effects MCP — Live Bridge & IPC Protocol`  
**Referencia:** `REQ-019`, `REQ-020`, `REQ-021`, `REQ-022`  

---

## 1. Protocolo de Comunicación JSON-RPC 2.0

La comunicación entre el motor y Adobe After Effects se realiza mediante un canal IPC bidireccional estructurado bajo el estándar JSON-RPC 2.0.

### Esquema de Mensajes:
```json
{
  "jsonrpc": "2.0",
  "id": "req_101",
  "method": "query_comp",
  "params": {
    "compName": "MAIN_TIMELINE"
  }
}
```

---

## 2. Máquina de Estados del Puente IPC

```
┌─────────────────────────────────────────────────────────────┐
│                       DISCONNECTED                          │
└──────────────┬──────────────────────────────▲───────────────┘
               │ connect()                    │ Timeout / Crash
               ▼                              │
┌─────────────────────────────────────────────┴───────────────┐
│                        CONNECTING                           │
└──────────────┬──────────────────────────────────────────────┘
               │ Handshake OK
               ▼
┌─────────────────────────────────────────────────────────────┐
│                         CONNECTED                           │
│ • Heartbeat activo cada 2.5s                                │
└──────────────┬──────────────────────────────▲───────────────┘
               │ send_command()               │ Execution Done
               ▼                              │
┌─────────────────────────────────────────────┴───────────────┐
│                        BUSY / EXEC                          │
│ • Ejecutando ExtendScript AST                               │
└──────────────┬──────────────────────────────▲───────────────┘
               │ render_queue.render()        │ Render Finished
               ▼                              │
┌─────────────────────────────────────────────┴───────────────┐
│                         RENDERING                           │
│ • Reportando progreso 0% -> 100%                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Detección de Caídas y Heartbeat

El puente envía un ping periódico cada $2.5\text{ s}$. Si no recibe respuesta en un umbral de $10.0\text{ s}$:
1. Marca el estado como `DISCONNECTED`.
2. Aborta cualquier transacción abierta para prevenir estados corruptos.
3. Intenta una reconexión controlada y reconciliación de estado.
