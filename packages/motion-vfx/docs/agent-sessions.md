# Sesiones de Agente de IA y Memoria Operacional (Fase 18)

## 1. Concepto de `AgentSession`

Una sesión de agente encapsula la interacción de un modelo de lenguaje o subagente con un proyecto específico:
- `sessionId`: identificador de sesión.
- `agentId`: identidad del agente (ej. `agent-director`, `agent-editor`).
- `projectId`: proyecto objetivo.
- `expectedRevisionId`: revisión base esperada para validación de concurrencia optimista.
- `policy`: conjunto de reglas (`AgentPolicy`) que limitan las acciones permitidas y previenen operaciones destructivas indebidas.
- `memory`: registro auditable de observaciones (`AgentObservation`) y decisiones tomadas (`AgentDecision`).

## 2. Flujo de Trabajo Observar-Mutar

```typescript
const session = new AgentSession({
  sessionId: "session_01",
  agentId: "agent-editor",
  projectId: "proj_demo",
  initialRevisionId: "rev_001",
  store,
  revisionManager,
});

// 1. Observar estado actual
const obs = await session.observe();

// 2. Aplicar mutación atómica bajo concurrencia optimista
const newRev = await session.mutate({
  action: { actionId: "act_1", type: "modify_layer", targetId: "layer_title", parameters: { text: "Nuevo Título" } },
  rationale: "Optimización de engagement inicial",
  expectedOutcome: "Incrementar retención en los primeros 3 segundos",
  mutation: (draft) => {
    draft.elements[0].text = "Nuevo Título";
    return draft;
  },
});
```
