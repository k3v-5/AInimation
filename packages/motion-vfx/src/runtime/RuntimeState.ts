import { RuntimeStateError } from "../errors/runtime-errors.js";

export type RuntimeLifecycleState = "INITIALIZING" | "READY" | "BUSY" | "SHUTTING_DOWN" | "CLOSED";

/**
 * Máquina de estados del ciclo de vida del Runtime de Producción (Fase 18).
 */
export class RuntimeStateMachine {
  private _state: RuntimeLifecycleState = "INITIALIZING";

  public get state(): RuntimeLifecycleState {
    return this._state;
  }

  public transitionTo(newState: RuntimeLifecycleState): void {
    if (this._state === "CLOSED") {
      throw new RuntimeStateError(this._state, newState, { message: "Runtime is permanently closed." });
    }
    this._state = newState;
  }

  public assertReadyOrBusy(): void {
    if (this._state !== "READY" && this._state !== "BUSY") {
      throw new RuntimeStateError(this._state, "READY | BUSY");
    }
  }
}
