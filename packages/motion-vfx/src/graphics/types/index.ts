import { Color } from "../../core/types.js";
import { Vec2 } from "../../masks/types/index.js";
import { Transform } from "../../transform/Transform.js";

export type GeometryType =
  | "rectangle"
  | "rounded-rectangle"
  | "ellipse"
  | "line"
  | "polygon"
  | "arrow"
  | "path";

export type FillType = "solid" | "linear-gradient" | "radial-gradient";
export type StrokeJoin = "miter" | "round" | "bevel";
export type StrokeCap = "butt" | "round" | "square";

export type AnchorPosition =
  | "top-left"
  | "top-center"
  | "top-right"
  | "center-left"
  | "center"
  | "center-right"
  | "bottom-left"
  | "bottom-center"
  | "bottom-right";

export type SemanticCategory =
  | "attention"
  | "information"
  | "warning"
  | "comparison"
  | "statistic"
  | "instruction"
  | "reaction"
  | "emphasis";

export interface RectangleGeometry {
  type: "rectangle";
  width: number;
  height: number;
}

export interface RoundedRectangleGeometry {
  type: "rounded-rectangle";
  width: number;
  height: number;
  radius: number;
}

export interface EllipseGeometry {
  type: "ellipse";
  width: number;
  height: number;
}

export interface LineGeometry {
  type: "line";
  start: Vec2;
  end: Vec2;
}

export interface ArrowGeometry {
  type: "arrow";
  start: Vec2;
  end: Vec2;
  headLength: number;
  headWidth: number;
  shaftWidth: number;
}

export interface PolygonGeometry {
  type: "polygon";
  points: Vec2[];
}

export type Geometry =
  | RectangleGeometry
  | RoundedRectangleGeometry
  | EllipseGeometry
  | LineGeometry
  | ArrowGeometry
  | PolygonGeometry;

export interface DashPattern {
  segments: number[]; // ej. [10, 5]
  offset: number;
}

export interface Stroke {
  color: Color;
  width: number;
  opacity: number;
  join?: StrokeJoin;
  cap?: StrokeCap;
  dash?: DashPattern;
}

export interface Fill {
  type: FillType;
  color?: Color;
  gradientStops?: Array<{ offset: number; color: Color }>;
}

export interface GraphicStyle {
  fill?: Fill;
  stroke?: Stroke;
  opacity: number;
}

export interface TrimPaths {
  start: number; // [0, 1]
  end: number; // [0, 1]
  offset: number; // en grados o vueltas [0, 1]
}

export interface StackLayoutOptions {
  direction: "horizontal" | "vertical";
  gap: number;
  alignment: "start" | "center" | "end";
}

export interface SafeAreaInsets {
  top: number;
  bottom: number;
  left: number;
  right: number;
}

export interface GraphicElement {
  id: string;
  name?: string;
  geometry: Geometry;
  style: GraphicStyle;
  transform: Transform;
  trimPaths?: TrimPaths;
}

export type CounterFormat = "integer" | "currency" | "compact" | "percentage";

export interface ChartData {
  type: "bar" | "line" | "pie";
  values: number[];
  labels?: string[];
  colors?: Color[];
}

export interface GraphicPreset {
  id: string;
  name: string;
  category: SemanticCategory;
  description: string;
  parameters: Record<string, any>;
  createElements: (params: Record<string, any>) => GraphicElement[];
}
