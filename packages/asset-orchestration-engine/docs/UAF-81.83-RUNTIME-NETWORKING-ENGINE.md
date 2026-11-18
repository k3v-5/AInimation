# UAF-81.83 — UNIVERSAL RUNTIME NETWORKING, ENTITY REPLICATION, STATE SYNCHRONIZATION & MULTIPLAYER ENGINE

**Estado:** Fase Normativa en Ejecución  
**Dependencias:**  
- UAF-81.73 Runtime World Model  
- UAF-81.74 Runtime Physics  
- UAF-81.75 Runtime Rendering  
- UAF-81.77 Runtime Input  
- UAF-81.79 Runtime Gameplay  
- UAF-81.80 Runtime Animation  
- UAF-81.81 World Partitioning / Spatial Streaming  
- UAF-81.82 Runtime AI  
- Event Bus determinista, Replay Engine, Checkpoint/Recovery, Asset Registry y sistema SHA-256 de estado canónico.

---

# 1. OBJETIVO DEL SUBSISTEMA

UAF-81.83 implementa la capa universal de redes, replicación de entidades y sincronización de estado de la Universal Asset Factory (UAF). Proporciona arquitectura cliente-servidor autoritativa con:
- Servidor dedicado, servidor de escucha y cliente completamente ejecutables en modo headless.
- Identificadores de red estables (`NetworkEntityId`, `ConnectionId`, `ClientId`) desacoplados de punteros de memoria.
- Modelo de autoridad estricto (`SERVER_AUTHORITY`, `CLIENT_PREDICTED`, `SHARED`, `NONE`) donde el cliente nunca fija directamente salud, daño, inventario o resultados de combate.
- Replicación eficiente con snapshots inmutables, compresión delta contra baselines confirmadas (`ACK`) e invalidación de baselines ante desincronización.
- Canales Confiables Ordenados (`ReliableOrdered`) con control de flujo por ventana de ACK de 32 bits y retransmisión por tick, y Canales No-Confiables Secuenciados (`UnreliableSequenced`) tolerantes a pérdida con aritmética modular de secuencias.
- Gestión de relevancia espacial integrada con las celdas de particionado de UAF-81.81 (`InterestProfile`), estados de dormancia (`ACTIVE` / `DORMANT`) y despertado condicional.
- Búfer de inputs de cliente, predicción del lado del cliente, reconciliación automática tras snapshot autoritativo y resincronización completa ante desincronizaciones severas.
- Búfer histórico anular (`HistoryBuffer`), compensación de lag (`Lag Compensation`) para validación retrospectiva de impactos (`Hit Validation`) y motor de rollback determinista en servidor.
- Ejecución autoritativa en servidor de física (UAF-81.74) e IA (UAF-81.82), replicando solo estados de mayor nivel y parámetros de animación (UAF-81.80).
- Seguridad robusta tratando todo input externo como `UNTRUSTED`, validando límites numéricos y rechazando terminantemente `NaN` o `Infinity`.
- Puntos de control (checkpoints) y replays deterministas con cálculo canónico SHA-256 de `state_hash` excluyendo identificadores de socket y tiempos de reloj de pared.

---

# 2. PRINCIPIO FUNDAMENTAL DE AUTORIDAD

```text
                        SERVER (AUTHORITY)
                                 │
                  ┌──────────────┼──────────────┐
                  ▼              ▼              ▼
               Physics        Gameplay          AI
                  │              │              │
                  └──────────────┼──────────────┘
                                 │
                            World State
                                 │
                            Replication
                      ┌──────────┴──────────┐
                      ▼                     ▼
              CLIENT A (Proxy)      CLIENT B (Proxy)
              - Local Prediction    - Local Prediction
              - Reconciliation      - Reconciliation
```

**Regla de Oro**: Ninguna propiedad autoritativa de juego (salud, inventario, victoria, daño, cooldowns) podrá ser mutada directamente por un cliente. El cliente únicamente emite intenciones (`InputCommand` y llamadas RPC); el servidor valida, simula y publica la verdad autoritativa.

---

# 3. IDENTIDADES DE RED

1. **`NetworkEntityId(namespace: int, value: int)`**: Tupla inmutable y totalmente ordenada que identifica a una entidad en la red sin depender de direcciones de memoria ni IDs efímeros de base de datos.
2. **`ConnectionId(value: str)`**: Identificador único de la conexión física/lógica durante la sesión activa.
3. **`ClientId(value: str)`**: Identificador persistente del jugador/cliente, estable frente a desconexiones temporales y reconexiones.

---

# 4. PROTOCOLO DE PAQUETES Y CANALES

```text
┌─────────────────────────────────────────────────────────────┐
│                       PACKET HEADER                         │
├─────────────────┬──────────────────┬────────────────────────┤
│ ProtocolVersion │ SessionId        │ ConnectionId           │
│ ChannelType     │ Sequence (uint32)│ AckSequence (uint32)   │
│ AckBits (uint32)│ ServerTick       │ PayloadSize            │
└─────────────────┴──────────────────┴────────────────────────┘
```

1. **Aritmética Modular de Secuencias**: Toda comparación de números de secuencia (`s1`, `s2`) se realiza mediante aritmética modular para manejar wrapping de enteros sin indeterminismo:
   `sequence_greater_than(s1, s2) <=> ((s1 > s2) and (s1 - s2 <= 0x7FFF)) or ((s1 < s2) and (s2 - s1 > 0x7FFF))`
2. **Ventana Deslizante de ACK**: El campo `ack_bits` de 32 bits permite confirmar los 32 paquetes previos al último recibido (`AckSequence`), permitiendo alta resiliencia ante pérdida y reordenamiento de paquetes.
3. **Canal Confiable**: Mantiene una cola de retransmisión y entrega en estricto orden secuencial sin duplicaciones.
4. **Canal No Confiable**: Descarta paquetes con secuencia menor o igual a la última confirmada, evitando procesar información obsoleta.

---

# 5. REPLICACIÓN, BASELINES Y COMPRESIÓN DELTA

1. **Snapshot Autoritativo**: En cada tick de red el servidor genera un `WorldSnapshot` conteniendo el estado de todas las entidades relevantes.
2. **Baseline Confirmada**: Cada conexión cliente mantiene un puntero a la última baseline que el cliente confirmó explícitamente haber recibido (`ACK`).
3. **Compresión Delta**: El servidor solo transmite las propiedades que cambiaron entre la baseline confirmada del cliente y el snapshot actual. Si no hay cambios, el delta es vacío.
4. **Invalidación de Baseline**: Si el cliente reporta pérdida irrecuperable, cambio de revisión de mundo o desincronización, la baseline se descarta forzando un snapshot base completo.

---

# 6. PREDICCIÓN, RECONCILIACIÓN Y ROLLBACK

1. **Client-Side Prediction**: El cliente ejecuta localmente su input (`InputCommand`), actualiza su posición predicha y almacena el input en un búfer no confirmado.
2. **Reconciliation**: Al recibir un snapshot autoritativo del servidor, el cliente compara su posición histórica predicha contra la verdad autoritativa. Si difieren más allá de un umbral de tolerancia:
   - Restaura el estado autoritativo recibido.
   - Re-ejecuta en orden todos los inputs que aún no han sido confirmados por el servidor.
   - Establece la nueva predicción resultante sin teletransportación brusca.
3. **Lag Compensation**: El servidor conserva un `HistoryBuffer` de las últimas $N$ posiciones de todas las entidades. Cuando un cliente solicita una acción con timestamp/tick retrospectivo (p.ej. disparo), el servidor rebobina temporalmente las colisiones al tick exacto del cliente para validar el impacto.
4. **Rollback en Servidor**: Permite resimular un intervalo de tiempo $[T_{\text{hist}}, T_{\text{curr}}]$ cuando se aceptan inputs tardíos pero válidos, asegurando que el estado final sea bit-exacto.

---

# 7. INTEGRACIÓN CON STREAMING Y GESTIÓN DE INTERÉS

- Cada conexión cliente define un `InterestProfile(position, radius, priority)`.
- El subsistema de relevancia cruza este perfil con las celdas espaciales de `runtime_streaming` (UAF-81.81). Las entidades en celdas no relevantes o fuera del radio de interés no son replicadas.
- **Dormancia**: Las entidades sin mutaciones o sin clientes en rango entran en estado `DORMANT`, eliminando la sobrecarga de serialización y transmisión hasta que una interacción o mutación despierte a la entidad.

---

# 8. SEGURIDAD Y TOLERANCIA A DESCONEXIÓN

- Toda carga útil entrante se valida antes de procesarse: esquemas, longitud máxima de payload, tasas de mensajes por tick y ausencia total de `NaN`/`Infinity`.
- Desconexión segura: La pérdida de un cliente nunca interrumpe el bucle de simulación del servidor; las entidades del cliente son eliminadas o transferidas a control por IA según la política de la sesión.
