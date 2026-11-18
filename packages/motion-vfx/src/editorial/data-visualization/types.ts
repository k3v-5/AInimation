import {
  DataVisualizationError,
  DataVisualizationValidationError,
  DatasetValidationError,
  VisualizationCompilationError,
  SafeZoneViolationError,
  ScaleCalculationError,
} from "./errors.js";

export {
  DataVisualizationError,
  DataVisualizationValidationError,
  DatasetValidationError,
  VisualizationCompilationError,
  SafeZoneViolationError,
  ScaleCalculationError,
};

/**
 * REQ-025: Contratos TypeScript para Data Visualization Engine.
 */

// ---------------------------------------------------------------------------
// 1. DATASET
// ---------------------------------------------------------------------------

export type DataColumnType = "STRING" | "NUMBER" | "DATE" | "BOOLEAN";

export interface DataColumn {
  key: string;
  label: string;
  type: DataColumnType;
  unit?: string;
}

export type DataValue = string | number | boolean | null;

export type DataRow = Record<string, DataValue>;

export interface DataSet {
  id: string;
  title?: string;
  description?: string;
  columns: DataColumn[];
  rows: DataRow[];
  metadata?: Record<string, string | number | boolean>;
}

// ---------------------------------------------------------------------------
// 2. CONFIGURACIÓN Y ESTILOS
// ---------------------------------------------------------------------------

export type VisualizationType =
  | "ANIMATED_BAR_CHART"
  | "TREND_LINE"
  | "BIG_STAT_CARD"
  | "CHRONOLOGY_TIMELINE";

export type AspectRatio = "16:9" | "9:16" | "1:1";

export type SafeZoneUnit = "PX" | "PERCENT";

export interface SafeZoneConfig {
  top: number;
  right: number;
  bottom: number;
  left: number;
  unit?: SafeZoneUnit;
}

export interface VisualizationStyle {
  backgroundColor: string;
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  textColor: string;
  fontFamily: string;
  fontWeight: number;
  titleFontSize: number;
  labelFontSize: number;
  valueFontSize: number;
  tracking: number;
  gridOpacity: number;
  borderWidth: number;
}

export interface CubicBezier {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export type EasingType =
  | "LINEAR"
  | "EASE_IN"
  | "EASE_OUT"
  | "EASE_IN_OUT"
  | "CUBIC_BEZIER";

export interface AnimationConfig {
  entranceDurationSeconds: number;
  exitDurationSeconds: number;
  easing: EasingType;
  staggerSeconds?: number;
  overshoot?: number;
  cubicBezier?: CubicBezier;
}

export interface AccessibilityConfig {
  description: string;
  announceValues?: boolean;
  decorative?: boolean;
}

export type NullValuePolicy = "REJECT" | "SKIP" | "ZERO";
export type ScaleType = "LINEAR" | "TIME" | "ORDINAL" | "LOG" | "SQRT" | "TEMPORAL" | "BAND";

// ---------------------------------------------------------------------------
// 3. SPECS (ESPECIFICACIONES DECLARATIVAS)
// ---------------------------------------------------------------------------

export interface BaseVisualizationSpec {
  id: string;
  type: VisualizationType;
  width: number;
  height: number;
  durationSeconds: number;
  startTimeSeconds: number;
  safeZone: SafeZoneConfig;
  style: VisualizationStyle;
  animation: AnimationConfig;
  accessibility?: AccessibilityConfig;
}

export interface BarChartSpec extends BaseVisualizationSpec {
  type: "ANIMATED_BAR_CHART";
  datasetId: string;
  categoryColumn: string;
  valueColumn: string;
  orientation: "VERTICAL" | "HORIZONTAL";
  maxBars?: number;
  sort: "ASCENDING" | "DESCENDING" | "SOURCE";
  showValues: boolean;
  showLabels: boolean;
  showAxis: boolean;
  showGrid: boolean;
  animateCounters: boolean;
  nullPolicy?: NullValuePolicy;
}

export interface TrendLineSpec extends BaseVisualizationSpec {
  type: "TREND_LINE";
  datasetId: string;
  xColumn: string;
  yColumn: string;
  showPoints: boolean;
  showLabels: boolean;
  showGrid: boolean;
  interpolation: "LINEAR" | "SMOOTH";
  highlightExtremes: boolean;
  nullPolicy?: NullValuePolicy;
}

export type NumberFormat =
  | "INTEGER"
  | "DECIMAL"
  | "PERCENTAGE"
  | "CURRENCY"
  | "CUSTOM";

export interface BigStatSpec extends BaseVisualizationSpec {
  type: "BIG_STAT_CARD";
  value: number | string;
  label: string;
  prefix?: string;
  suffix?: string;
  secondaryText?: string;
  accentLine: boolean;
  animateValue: boolean;
  decimals?: number;
  format?: NumberFormat;
}

export interface ChronologyTimelineSpec extends BaseVisualizationSpec {
  type: "CHRONOLOGY_TIMELINE";
  datasetId: string;
  dateColumn: string;
  titleColumn: string;
  descriptionColumn?: string;
  orientation: "HORIZONTAL" | "VERTICAL";
  showDates: boolean;
  showDescriptions: boolean;
  maxEvents?: number;
  nullPolicy?: NullValuePolicy;
}

export type VisualizationSpec =
  | BarChartSpec
  | TrendLineSpec
  | BigStatSpec
  | ChronologyTimelineSpec;

// ---------------------------------------------------------------------------
// 4. REPRESENTACIÓN INTERMEDIA (VISUALIZATION IR)
// ---------------------------------------------------------------------------

export interface Transform2D {
  position: { x: number; y: number };
  scale: { x: number; y: number };
  rotation: number;
  anchor: { x: number; y: number };
}

export interface RectGeometry {
  kind: "RECT";
  x: number;
  y: number;
  width: number;
  height: number;
  cornerRadius?: number;
  fillColor?: string;
  strokeColor?: string;
  strokeWidth?: number;
}

export interface CircleGeometry {
  kind: "CIRCLE";
  centerX: number;
  centerY: number;
  radius: number;
  fillColor?: string;
  strokeColor?: string;
  strokeWidth?: number;
}

export interface LineGeometry {
  kind: "LINE";
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  strokeColor: string;
  strokeWidth: number;
}

export interface PathCommand {
  type: "M" | "L" | "C" | "Z";
  points: number[];
}

export interface PathGeometry {
  kind: "PATH";
  commands: PathCommand[];
  strokeColor?: string;
  strokeWidth?: number;
  fillColor?: string;
}

export type GeometryIR =
  | RectGeometry
  | CircleGeometry
  | LineGeometry
  | PathGeometry;

export interface TextIR {
  content: string;
  fontFamily: string;
  fontSize: number;
  fontWeight: number;
  color: string;
  tracking: number;
  alignment: "LEFT" | "CENTER" | "RIGHT";
}

export interface Keyframe {
  timeSeconds: number;
  value: number | number[];
  easing: EasingType;
}

export interface KeyframedProperty {
  property: string;
  keyframes: Keyframe[];
}

export interface AnimationIR {
  properties: KeyframedProperty[];
}

export interface VisualizationLayer {
  id: string;
  type: "SHAPE" | "TEXT" | "PATH" | "GROUP" | "GUIDE" | string;
  name: string;
  zIndex: number;
  transform: Transform2D;
  opacity: number;
  geometry?: GeometryIR;
  text?: TextIR;
  animation?: AnimationIR;
  animations?: any[];
  metadata?: Record<string, any>;
  [key: string]: any;
}

export interface VisualizationMarker {
  timeSeconds: number;
  name: string;
  comment?: string;
}

// ---------------------------------------------------------------------------
// 5. MÉTRICAS Y RESULTADOS DE COMPILACIÓN
// ---------------------------------------------------------------------------

export interface VisualizationMetrics {
  layerCount: number;
  textLayerCount: number;
  shapeLayerCount: number;
  pathLayerCount: number;
  keyframeCount: number;
  dataPointCount: number;
  warningsCount: number;
  errorsCount: number;
  compileDurationMs?: number;
}

export interface VisualizationProposal {
  id: string;
  type: string;
  reason: string;
  confidence: number;
}

export interface VisualizationCompilationResult {
  success: boolean;
  ir?: VisualizationIR;
  errors: DataVisualizationError[];
  warnings: DataVisualizationError[];
  metrics?: VisualizationMetrics;
  proposals?: VisualizationProposal[];
  checksumSha256?: string;
}

// ---------------------------------------------------------------------------
// 6. MODELOS GEOMÉTRICOS INTERNOS
// ---------------------------------------------------------------------------

export interface BarGeometry {
  id: string;
  category: string;
  value: number;
  x: number;
  y: number;
  width: number;
  height: number;
  normalizedValue: number;
  bounds?: { x: number; y: number; width: number; height: number };
  labelPosition?: { x: number; y: number };
  valuePosition?: { x: number; y: number };
}

export interface TrendPoint {
  id: string;
  sourceX: number;
  sourceY: number;
  normalizedX: number;
  normalizedY: number;
  screenX: number;
  screenY: number;
}

export interface TrendPath {
  points: TrendPoint[];
  commands: PathCommand[];
}

// ---------------------------------------------------------------------------
// 7. COMPATIBILIDAD CON TIPOS PREVIOS (DataVisualization.test.ts)
// ---------------------------------------------------------------------------

export interface DataPoint {
  id: string;
  label: string;
  value: number;
  unit?: string;
  category?: string;
  timestamp?: number;
  timestampSeconds?: number;
  source?: string;
  citation?: string;
  metadata?: Record<string, any>;
  normalizedValue?: number;
}

export interface DatasetSource {
  type: "EVIDENCE" | "HISTORICAL" | "EXTERNAL_API" | "SYNTHETIC" | "USER" | "MANUAL" | "CSV" | "JSON";
  citationId?: string;
  uri?: string;
  checksumSha256?: string;
}

export interface EditorialDataset {
  id: string;
  title: string;
  unit?: string;
  points: DataPoint[];
  source?: DatasetSource;
  schemaVersion: string;
}

export interface VisualScale {
  min: number;
  max: number;
  pixelStart: number;
  pixelEnd: number;
  domain?: [number, number];
  range?: [number, number];
  type?: "LINEAR" | "LOGARITHMIC" | "EXPONENTIAL";
  clamped?: boolean;
}

export interface BarChartConfig {
  barWidth: number;
  barSpacing: number;
  orientation: "VERTICAL" | "HORIZONTAL";
  animationDurationSeconds: number;
  colorPalette: string[];
}

export interface KeyPoint {
  index: number;
  label: string;
  type: "MAXIMUM" | "MINIMUM" | "INFLECTION" | "TARGET";
}

export interface StrokeAnimation {
  drawDurationSeconds: number;
  easingCurve: [number, number, number, number];
  strokeWidth: number;
}

export interface DividerSpec {
  yPosition: number;
  color: string;
  thickness: number;
}

export interface BigStatCard {
  title: string;
  primaryValue: string;
  unit: string;
  comparisonDelta: string;
  direction: "UP" | "DOWN" | "NEUTRAL";
  footnote: string;
}

export interface TimelineEvent {
  id: string;
  date?: string;
  timestamp?: number;
  label: string;
  description?: string;
  category?: string;
  significance?: "LOW" | "MEDIUM" | "HIGH";
}

export interface LabelCollision {
  pointIndexA: number;
  pointIndexB: number;
  overlapDistance: number;
  resolvedYOffset: number;
}

// ---------------------------------------------------------------------------
// REQ-025 MAESTRO: Primitive DataPoint & VisualizationDataset
// ---------------------------------------------------------------------------

export interface VisualizationDataset {
  id: string;
  title?: string;
  description?: string;
  points: DataPoint[];
  source?: string;
  sourceUrl?: string;
  unit?: string;
  precision?: number;
  metadata?: Record<string, any>;
}

export interface ValidationIssue {
  code: string;
  severity: "ERROR" | "WARNING";
  path: string;
  message: string;
}

export interface ValidationResult {
  valid: boolean;
  issues: ValidationIssue[];
}

export interface VisualizationViewport {
  width: number;
  height: number;
  safeMarginTop: number;
  safeMarginRight: number;
  safeMarginBottom: number;
  safeMarginLeft: number;
}

export interface VisualizationTheme {
  backgroundColor: string;
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  textColor: string;
  mutedTextColor: string;
  gridColor: string;
  negativeColor: string;
  fontFamily: string;
  fontWeight: number;
}

export interface AnimatedBarChartConfig {
  orientation: "VERTICAL" | "HORIZONTAL";
  sort: "INPUT" | "ASCENDING" | "DESCENDING";
  showValues: boolean;
  showLabels: boolean;
  showGrid: boolean;
  animationDurationSeconds: number;
  staggerSeconds: number;
  easing: EasingType;
}

export interface TrendLineGraphConfig {
  showPoints: boolean;
  showLabels: boolean;
  showGrid: boolean;
  showAreaFill: boolean;
  animationDurationSeconds: number;
  lineWidth: number;
  pointRadius: number;
  smoothing: "NONE" | "CATMULL_ROM";
}

export interface BigStatCardConfig {
  value: number;
  label: string;
  unit?: string;
  prefix?: string;
  suffix?: string;
  animationDurationSeconds: number;
  showDivider: boolean;
}

export interface ChronologyTimelineConfig {
  orientation: "HORIZONTAL" | "VERTICAL";
  showDates: boolean;
  showLabels: boolean;
  showConnectors: boolean;
  animationDurationSeconds: number;
  markerStyle: "CIRCLE" | "DIAMOND" | "LINE";
}

export interface ChartPoint {
  x: number;
  y: number;
  sourceId: string;
}

export interface VisualizationCitation {
  source: string;
  citation?: string;
  url?: string;
  accessedAt?: string;
}

export interface VisualizationKeyframe {
  timeSeconds: number;
  value: number | string;
}

export interface VisualizationAnimation {
  id: string;
  elementId: string;
  property: string;
  keyframes: VisualizationKeyframe[];
  easing: EasingType;
}

export interface VisualizationMetadata {
  engineVersion?: string;
  compilerVersion?: string;
  requirementId?: "REQ-025" | string;
  generatedAt?: string;
  datasetId?: string;
  sourceDatasetId?: string;
  profileId?: string;
  sourceCount?: number;
  sourceRows?: number;
  deterministic?: boolean;
  [key: string]: any;
}

export interface VisualizationCognitiveMetadata {
  activeElements: number;
  textElements: number;
  numericElements: number;
  animationCount: number;
}

export type VisualizationErrorCode =
  | "EMPTY_DATASET"
  | "INVALID_VALUE"
  | "NON_FINITE_VALUE"
  | "DUPLICATE_ID"
  | "INVALID_TIMESTAMP"
  | "INVALID_VIEWPORT"
  | "INVALID_DURATION"
  | "LABEL_OVERFLOW"
  | "GEOMETRY_OVERFLOW"
  | "UNSUPPORTED_SCALE"
  | "UNSUPPORTED_CHART"
  | "INVALID_CONFIGURATION";

export interface VisualizationError {
  code: VisualizationErrorCode;
  message: string;
  path?: string;
  sourceId?: string;
}

export interface CollisionReport {
  hasCollisions: boolean;
  collisions: Array<{
    elementIdA: string;
    elementIdB: string;
    distance: number;
    recommendedOffset: { x: number; y: number };
  }>;
}

export interface VisualizationContext {
  editorialProfile?: string;
  viewport?: Partial<VisualizationViewport>;
  theme?: Partial<VisualizationTheme>;
  startTimeSeconds?: number;
  durationSeconds?: number;
}

export interface VisualizationRequest {
  type: "BAR_CHART" | "TREND_LINE" | "BIG_STAT" | "CHRONOLOGY_TIMELINE";
  config: unknown;
  context?: VisualizationContext;
}

export interface VisualizationElement {
  id: string;
  type: "RECT" | "LINE" | "PATH" | "TEXT" | "CIRCLE" | "GROUP" | "BAR" | "LABEL" | "CARD" | "EVENT" | "COUNTER" | "LINE_SEGMENT" | "KEY_POINT" | "TIMELINE_NODE" | string;
  x: number;
  y: number;
  width?: number;
  height?: number;
  rotation?: number;
  opacity?: number;
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  text?: string;
  parentId?: string;
  sourceId?: string;
  data?: any;
  bounds?: { x: number; y: number; width: number; height: number };
  [key: string]: any;
}

export interface VisualizationIR {
  id: string;
  type: "BAR_CHART" | "TREND_LINE" | "BIG_STAT" | "CHRONOLOGY_TIMELINE" | "BIG_STAT_CARD" | "CHRONOLOGY" | string;
  viewport: VisualizationViewport;
  theme: VisualizationTheme;
  elements: VisualizationElement[];
  animations: VisualizationAnimation[];
  metadata: VisualizationMetadata;
  cognitiveMetadata?: VisualizationCognitiveMetadata;
  pacingMetadata?: { visualDurationSeconds: number; animationDurationSeconds: number };
  editorialIntensity?: "LOW" | "MEDIUM" | "HIGH" | "PEAK";
  checksumSha256: string;
  // Backward compatibility:
  datasetId?: string;
  layers: VisualizationLayer[];
  metrics?: any;
  success?: boolean;
  ir?: VisualizationIR;
  errors?: any[];
  warnings?: any[];
  [key: string]: any;
}

export type DataVisualizationIR = VisualizationIR;
