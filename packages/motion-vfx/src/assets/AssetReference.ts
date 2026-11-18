import { AssetType } from "./types.js";

/**
 * Referencia liviana utilizada por los elementos para vincularse a un activo del registro.
 */
export interface AssetReference {
  readonly id: string;
  readonly type: AssetType;
}
