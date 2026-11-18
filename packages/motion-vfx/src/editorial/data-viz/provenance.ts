import {
  VisualizationProvenance,
  VisualizationEvidenceBinding,
  Dataset,
} from "./contracts.js";

/**
 * REQ-025 §25 & §26: Provenance & Evidence Verification Helpers
 */

export class ProvenanceTracker {
  public static readonly COMPILER_VERSION = "v4.0.0-editorial-master";

  public static createProvenance(
    datasetId: string,
    profileId: string = "TIME_EDITORIAL",
    sourceRefs: string[] = [],
    transformations: string[] = []
  ): VisualizationProvenance {
    return {
      datasetId,
      sourceRefs,
      transformations,
      compilerVersion: this.COMPILER_VERSION,
      profileId,
    };
  }

  public static validateEvidence(
    dataset: Dataset,
    options: { requireEvidence?: boolean } = {}
  ): { valid: boolean; error?: string } {
    const requiresEvidence = options.requireEvidence ?? (dataset.source?.type === "EVIDENCE");

    if (requiresEvidence) {
      if (!dataset.source || (!dataset.source.citationId && !dataset.source.uri)) {
        return {
          valid: false,
          error: `[BLOCKING] El dataset '${dataset.id}' declara requerir respaldo factual pero no contiene citationId ni URI de evidencia.`,
        };
      }
    }

    return { valid: true };
  }

  public static bindEvidence(
    visualizationId: string,
    dataset: Dataset
  ): VisualizationEvidenceBinding {
    const sourceRefs: string[] = [];
    if (dataset.source?.citationId) sourceRefs.push(dataset.source.citationId);
    if (dataset.source?.uri) sourceRefs.push(dataset.source.uri);

    for (const val of dataset.values) {
      if (val.sourceRef && !sourceRefs.includes(val.sourceRef)) {
        sourceRefs.push(val.sourceRef);
      }
    }

    return {
      visualizationId,
      datasetId: dataset.id,
      sourceRefs,
    };
  }
}
