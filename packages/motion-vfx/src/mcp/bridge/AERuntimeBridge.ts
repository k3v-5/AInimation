import { AELiveBridgeProtocol, JSONRPCRequest, JSONRPCResponse } from "../../exporters/ae/bridge/AELiveBridgeProtocol.js";
import { StateReconciler, ExpectedLayerState, ActualLayerState, ReconciliationReport } from "../reconciliation/StateReconciler.js";
import { MCPStructuredError } from "../types/index.js";
import { MCPErrorCatalog } from "../errors/MCPErrorCatalog.js";

export type BridgeState =
  | "DISCONNECTED"
  | "CONNECTING"
  | "CONNECTED"
  | "BUSY"
  | "RENDERING"
  | "ERROR"
  | "RECOVERING";

export interface BridgeConfig {
  heartbeatIntervalMs: number; // default: 2500ms
  heartbeatTimeoutMs: number; // default: 10000ms
  commandTimeoutMs: number; // default: 30000ms
  maxReconnectAttempts: number; // default: 3
}

/**
 * Gestor del Runtime de Adobe After Effects con Heartbeat, Tolerancia a Fallos y Reconciliación (Fase 4 / REQ-017, REQ-018, REQ-020).
 * Maneja caídas de After Effects, interrupciones de IPC y recuperación transaccional automática.
 */
export class AERuntimeBridge {
  private state: BridgeState = "DISCONNECTED";
  private config: BridgeConfig;
  private lastHeartbeatTimestamp = 0;
  private reconnectAttempts = 0;

  // Mock de transporte IPC inyectable para pruebas de red y desconexión
  private transportSender: ((payload: string) => Promise<string>) | null = null;

  constructor(config?: Partial<BridgeConfig>) {
    this.config = {
      heartbeatIntervalMs: config?.heartbeatIntervalMs ?? 2500,
      heartbeatTimeoutMs: config?.heartbeatTimeoutMs ?? 10000,
      commandTimeoutMs: config?.commandTimeoutMs ?? 30000,
      maxReconnectAttempts: config?.maxReconnectAttempts ?? 3,
    };
  }

  public getState(): BridgeState {
    return this.state;
  }

  /**
   * Inyecta el emisor de transporte IPC (socket, named pipe o mock).
   */
  public setTransportSender(sender: (payload: string) => Promise<string>): void {
    this.transportSender = sender;
  }

  /**
   * Conecta con la instancia de After Effects y valida el handshake inicial.
   */
  public async connect(): Promise<{ success: boolean; state: BridgeState; error?: MCPStructuredError }> {
    this.state = "CONNECTING";
    try {
      if (!this.transportSender) {
        // Modo local simulado exitoso
        this.state = "CONNECTED";
        this.lastHeartbeatTimestamp = Date.now();
        this.reconnectAttempts = 0;
        return { success: true, state: this.state };
      }

      const req = AELiveBridgeProtocol.createRequest("query_comp", { ping: true }, "handshake_01");
      const respStr = await this.sendWithTimeout(JSON.stringify(req), this.config.commandTimeoutMs);
      const resp = AELiveBridgeProtocol.parseResponse(respStr);

      if (resp.error) {
        throw new Error(resp.error.message);
      }

      this.state = "CONNECTED";
      this.lastHeartbeatTimestamp = Date.now();
      this.reconnectAttempts = 0;
      return { success: true, state: this.state };
    } catch (err) {
      this.state = "ERROR";
      return {
        success: false,
        state: this.state,
        error: MCPErrorCatalog.create(
          "AE_DISCONNECTED",
          `Failed to connect to After Effects: ${err instanceof Error ? err.message : String(err)}`
        ),
      };
    }
  }

  /**
   * Envía un comando ExtendScript o de consulta a After Effects garantizando timeouts estrictos.
   */
  public async sendCommand<T = unknown>(
    request: JSONRPCRequest
  ): Promise<{ response?: JSONRPCResponse<T>; error?: MCPStructuredError }> {
    if (this.state !== "CONNECTED" && this.state !== "BUSY") {
      return {
        error: MCPErrorCatalog.create(
          "AE_DISCONNECTED",
          `Cannot send command '${request.method}': Bridge is in state '${this.state}'.`
        ),
      };
    }

    const previousState = this.state;
    this.state = "BUSY";

    try {
      if (!this.transportSender) {
        // Respuesta mock por defecto
        this.state = previousState;
        return {
          response: {
            jsonrpc: "2.0",
            id: request.id,
            result: { status: "simulated_success", method: request.method } as unknown as T,
          },
        };
      }

      const rawResp = await this.sendWithTimeout(
        JSON.stringify(request),
        this.config.commandTimeoutMs
      );
      const parsed = AELiveBridgeProtocol.parseResponse<T>(rawResp);

      this.state = "CONNECTED";
      this.lastHeartbeatTimestamp = Date.now();
      return { response: parsed };
    } catch (err) {
      this.state = "ERROR";
      return {
        error: MCPErrorCatalog.create(
          "AE_TIMEOUT",
          `Command execution timed out or AE crashed: ${err instanceof Error ? err.message : String(err)}`
        ),
      };
    }
  }

  /**
   * Ejecuta el ciclo de Heartbeat activo para comprobar si After Effects sigue respondiendo.
   */
  public async checkHeartbeat(): Promise<boolean> {
    const now = Date.now();
    if (this.state === "CONNECTED" && now - this.lastHeartbeatTimestamp > this.config.heartbeatTimeoutMs) {
      this.state = "DISCONNECTED";
      return false;
    }
    return this.state === "CONNECTED";
  }

  /**
   * Reconcilia el estado de capas en After Effects con la IR Canónica.
   */
  public async reconcileLayers(
    expected: ExpectedLayerState[],
    actualFetcher?: () => Promise<ActualLayerState[]>
  ): Promise<ReconciliationReport> {
    let actualLayers: ActualLayerState[] = [];

    if (actualFetcher) {
      actualLayers = await actualFetcher();
    } else {
      // Mock automático alineado si no hay fetcher
      actualLayers = expected.map((e, idx) => ({
        index: idx + 1,
        name: e.name,
        inPoint: e.inPoint,
        outPoint: e.outPoint,
        position: e.position,
      }));
    }

    return StateReconciler.reconcile(expected, actualLayers);
  }

  /**
   * Intenta recuperar una conexión perdida y continuar.
   */
  public async recoverConnection(): Promise<boolean> {
    this.state = "RECOVERING";
    for (let attempt = 1; attempt <= this.config.maxReconnectAttempts; attempt++) {
      const conn = await this.connect();
      if (conn.success) {
        return true;
      }
    }
    this.state = "DISCONNECTED";
    return false;
  }

  public disconnect(): void {
    this.state = "DISCONNECTED";
  }

  private sendWithTimeout(payload: string, timeoutMs: number): Promise<string> {
    if (!this.transportSender) return Promise.resolve('{"jsonrpc":"2.0","id":1,"result":"ok"}');

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`IPC request timed out after ${timeoutMs}ms`));
      }, timeoutMs);

      this.transportSender!(payload)
        .then((res) => {
          clearTimeout(timer);
          resolve(res);
        })
        .catch((err) => {
          clearTimeout(timer);
          reject(err);
        });
    });
  }
}
