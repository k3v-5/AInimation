# 🔄 Especificación de Transacciones y Rollback Criptográfico

**Estándar:** `Autonomous After Effects MCP — ACID Transactions & Rollback`  
**Referencia:** `REQ-009`, `REQ-010`, `REQ-012`, `REQ-013`, `REQ-014`  

---

## 1. Ciclo de Vida de una Transacción

Toda mutación compleja o conjunto de operaciones se encapsula dentro de una transacción formal identificada por `transaction_id`:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. BEGIN TRANSACTION (transaction_id, expected_version)     │
│    • Congela un snapshot inmutable de la IR (HEAD)          │
│    • Registra Hash_before = SHA256(ProjectIR)               │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ 2. VALIDATE & DRY-RUN                                       │
│    • Verifica restricciones semánticas y límites de recursos │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ 3. APPLY IN-MEMORY PATCHES                                  │
│    • Aplica ChangeSets a la IR proyectada                   │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ 4. COMPILE & EXECUTE (AE LIVE BRIDGE)                       │
│    • Genera ExtendScript AST e inyecta en After Effects     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │ ¿Exitoso y QA Pass?         │
                └──┬────────────────────────┬─┘
              SÍ   │                        │ NO / Error
                   ▼                        ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐
│ 5. COMMIT TRANSACTION        │ │ 5. ROLLBACK TRANSACTION      │
│ • Avanza versión a V+1       │ │ • Restaura snapshot HEAD     │
│ • Emite Audit Log persistido │ │ • Garantiza Hash == Hash_prev│
│ • Retorna resultado exitoso  │ │ • Cancela operaciones en AE  │
└──────────────────────────────┘ └──────────────────────────────┘
```

---

## 2. Invariante de Rollback Estricto (REQ-013)

Si una transacción falla o es abortada en cualquier punto de su ejecución:
$$\text{ProjectIR}_{\text{post\_rollback}} \equiv \text{ProjectIR}_{\text{pre\_transaction}}$$
$$\text{SHA256}(\text{ProjectIR}_{\text{post\_rollback}}) \equiv \text{SHA256}(\text{ProjectIR}_{\text{pre\_transaction}})$$

Bajo ninguna circunstancia el motor dejará mutaciones parciales o huérfanas en el estado canónico.
