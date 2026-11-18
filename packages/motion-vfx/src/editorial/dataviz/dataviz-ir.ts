import { DATAVIZ_ENGINE_VERSION, DATAVIZ_SCHEMA_VERSION } from "./constants.js";
import { DataVizHash } from "./dataviz-hash.js";
import {
  DataVizAnimation,
  DataVizElement,
  DataVizIR,
  DataVizLayout,
  DataVizScale,
  DataVizStyleProfile,
  NormalizedDataPoint,
  VisualizationType,
} from "./types.js";

export interface CreateIRParams {
  id: string;
  type: VisualizationType;
  composition: {
    width: number;
    height: number;
    fps: number;
    durationSeconds: number;
  };
  dataset: {
    id: string;
    points: NormalizedDataPoint[];
  };
  layout: DataVizLayout;
  scales?: DataVizScale[];
  elements: DataVizElement[];
  animations?: DataVizAnimation[];
  style: DataVizStyleProfile;
  title?: string;
  source?: string;
  editorialProfileId?: string;
}

/**
 * REQ-025 §10, §52: DataVizIR Factory & Canonical Assembler.
 */
export class DataVizIRBuilder {
  public static build(params: CreateIRParams): DataVizIR {
    // Deterministic key sorting of visual elements
    const elements = [...params.elements].sort((a, b) =>
      a.id.localeCompare(b.id, "en", { numeric: true })
    );

    const animations = [...(params.animations ?? [])].sort((a, b) =>
      a.id.localeCompare(b.id, "en", { numeric: true })
    );

    const scales = [...(params.scales ?? [])].sort((a, b) =>
      a.id.localeCompare(b.id, "en", { numeric: true })
    );

    const draftIR: Omit<DataVizIR, "checksumSha256"> = {
      schemaVersion: DATAVIZ_SCHEMA_VERSION,
      engineVersion: DATAVIZ_ENGINE_VERSION,
      id: params.id,
      type: params.type,
      composition: params.composition,
      dataset: params.dataset,
      layout: params.layout,
      scales,
      elements,
      animations,
      style: params.style,
      metadata: {
        title: params.title,
        source: params.source,
        generatedAtDeterministic: true,
        datasetId: params.dataset.id,
        visualizationType: params.type,
        editorialProfileId: params.editorialProfileId,
        engineVersion: DATAVIZ_ENGINE_VERSION,
      },
    };

    const checksumSha256 = DataVizHash.computeSha256(draftIR);

    return {
      ...draftIR,
      checksumSha256,
    };
  }
}
