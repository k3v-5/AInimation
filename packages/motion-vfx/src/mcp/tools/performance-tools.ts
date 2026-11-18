import {
  PerformanceSegment,
  TakeCandidate,
  SemanticRedundancyEngine,
  BestTakeSelector,
  NaturalPerformancePreservation,
  IntelligentTrimmingEngine,
} from "../../editorial/performance/index.js";

/**
 * RF-056: MCP Tools for Intelligent Performance & Semantic Trimming Engine
 */

export async function editorial_detect_redundancy(params: { segments: PerformanceSegment[] }) {
  const redundancy = SemanticRedundancyEngine.analyze(params.segments);
  return { redundancy };
}

export async function editorial_select_best_take(params: { takeGroupId: string; takes: TakeCandidate[] }) {
  const selection = BestTakeSelector.select(params.takeGroupId, params.takes);
  return { selection };
}

export async function editorial_analyze_performance(params: { segment: PerformanceSegment }) {
  const decisions = NaturalPerformancePreservation.evaluate(params.segment);
  return { decisions };
}

export async function editorial_generate_trim_plan(params: {
  segments: PerformanceSegment[];
  takeGroups?: Record<string, TakeCandidate[]>;
  sourceDurationSeconds?: number;
  profile?: string;
  narrativeDependencies?: Record<string, string[]>;
}) {
  const report = IntelligentTrimmingEngine.process(params);
  return { report };
}

export async function editorial_get_trim_report(params: {
  segments: PerformanceSegment[];
  sourceDurationSeconds?: number;
}) {
  const report = IntelligentTrimmingEngine.process(params);
  return { report };
}
