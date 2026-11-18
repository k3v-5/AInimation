# Iteration 13: Direct Native Integration via CEP/UXP Adapter

## Objetivo
Reducir la dependencia de los macros opacos de Python (`pyautogui`, UI Automation) que pueden ser interrumpidos si el usuario mueve el ratón o surge un pop-up del sistema. Para esto, sentaremos las bases de un `AdobeCEPAdapter` que exponga un servidor local. Las extensiones de Adobe (UXP o CEP) inyectadas en las aplicaciones podrán conectarse a este servidor para recibir comandos del DAG de forma nativa e invisible.

## Acceptance Criteria (Criterios de Aceptación)

*   **AC-42: Adobe CEP Server Stub:**
    *   Crear `AdobeCEPAdapter.ts` usando `express` o `http` puro para levantar un servidor REST/WebSocket local en el puerto 3001.
    *   Implementar `startServer()` y `sendCommand(command: string, payload: any): Promise<any>`.
*   **AC-43: Provider Hook & Fallback:**
    *   Modificar `CharacterAnimatorProvider` para que inicie el adaptador en el método `connect()`.
    *   En `executeCapability`, intentar usar `adobeCEPAdapter.sendCommand()` para capacidades como `puppet.lip_sync` y `render.export`.
    *   Implementar un fallback: Si la extensión CEP no está conectada o la llamada falla (e.g. timeout), el provider debe recurrir a la lógica antigua basada en OS Macros (`os_automation.py`).
*   **AC-44: Extensibilidad Arquitectónica:**
    *   El adaptador debe ser genérico y capaz de manejar respuestas asíncronas para que en iteraciones futuras (CEP Extensions físicas) el motor reciba eventos de progreso nativo en lugar de bloquear el thread.
