# Transacciones Atómicas (Fase 18)

## Protocolo Transaccional
$$\text{BEGIN} \to \text{clone defensivo} \to \text{mutate} \to \text{validate} \to \text{compute hash} \to \text{persist} \to \text{COMMIT}$$

Si cualquier paso falla o lanza excepción:
$$\text{ROLLBACK} \to \text{estado previo intacto}$$

Garantiza que ninguna operación deje un proyecto parcialmente escrito o corrupto.
