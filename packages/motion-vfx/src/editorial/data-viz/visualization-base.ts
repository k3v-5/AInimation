import {
  BaseVisualizationNode,
  VisualizationType,
  AxisDisclosure,
  DataPointAnnotation,
  TimelineEvent,
  VisualizationProposal,
} from "./contracts.js";

export interface VisualizationStimulus {
  type: string;
  coefficient: number;
}

export interface BarGeometryItem {
  id: string;
  category: string;
  label: string;
  value: number;
  normalizedValue: number;
  x: number;
  y: number;
  width: number;
  height: number;
  isNegative: boolean;
  color: string;
}

export interface BarChartNode extends BaseVisualizationNode {
  type: "BAR_CHART";
  orientation: "VERTICAL" | "HORIZONTAL";
  baseline: { x1: number; y1: number; x2: number; y2: number };
  bars: BarGeometryItem[];
  axisDisclosure?: AxisDisclosure;
  showGrid: boolean;
  showLabels: boolean;
  showValues: boolean;
}

export interface TrendLineNode extends BaseVisualizationNode {
  type: "TREND_LINE";
  points: Array<{
    id: string;
    label: string;
    value: number;
    normalizedValue: number;
    normalizedTime: number;
    x: number;
    y: number;
  }>;
  svgPath: string;
  extrema: DataPointAnnotation[];
  showGrid: boolean;
  showPoints: boolean;
  showArea: boolean;
}

export interface BigStatNode extends BaseVisualizationNode {
  type: "BIG_STAT";
  numericValue: number;
  formattedValue: string;
  unit?: string;
  primaryLabel: string;
  subtitle?: string;
  sourceText?: string;
}

export interface TimelineNode extends BaseVisualizationNode {
  type: "CHRONOLOGY";
  orientation: "HORIZONTAL" | "VERTICAL";
  axis: { x1: number; y1: number; x2: number; y2: number };
  events: Array<{
    event: TimelineEvent;
    normalizedProgress: number;
    x: number;
    y: number;
  }>;
}

export type EditorialVisualizationNode =
  | BarChartNode
  | TrendLineNode
  | BigStatNode
  | TimelineNode;
