import { AssetLifecycleState, AssetMetadata, AssetSource, AssetType } from "./types.js";

/**
 * Representación abstracta de un recurso audiovisual en el Core (Fase 5A).
 */
export interface Asset {
  readonly id: string;
  readonly type: AssetType;
  name?: string;
  source: AssetSource;
  metadata?: AssetMetadata;
  status?: AssetLifecycleState;
}
