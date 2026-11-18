import { Color, Time, Vector2 } from "../core/types.js";
import { EvaluatedTransform } from "../transform/types.js";

export type ElementType = "group" | "text" | "image" | "video" | "audio" | "shape";

export type TextAlign = "left" | "center" | "right";

export interface TextStyle {
  fontFamily: string;
  fontSize: number;
  fontWeight: number;
  color: Color;
  lineHeight: number;
  letterSpacing: number;
  textAlign: TextAlign;
}

export type ShapeType = "rectangle" | "ellipse" | "line";

export interface RectangleShapeData {
  width: number;
  height: number;
  cornerRadius?: number;
}

export interface EllipseShapeData {
  radiusX: number;
  radiusY: number;
}

export interface LineShapeData {
  endPoint: Vector2;
}

export type ShapeData = RectangleShapeData | EllipseShapeData | LineShapeData;

export interface ShapeStyle {
  fill?: Color;
  stroke?: Color;
  strokeWidth?: number;
}

export interface BaseElementOptions {
  id?: string;
  name?: string;
  startTime?: Time;
  duration?: Time;
  visible?: boolean;
  parentId?: string;
}

export interface BaseElementState {
  id: string;
  name: string;
  type: ElementType;
  active: boolean;
  localTime: Time;
  visible: boolean;
  transform?: EvaluatedTransform;
  effects?: import("../effects/types/index.js").EvaluatedEffectStack;
}

export interface EvaluatedTextState extends BaseElementState {
  type: "text";
  text: string;
  style: TextStyle;
}

export interface EvaluatedImageState extends BaseElementState {
  type: "image";
  assetId: string;
}

export interface EvaluatedVideoState extends BaseElementState {
  type: "video";
  assetId: string;
  sourceTime: Time;
}

export interface EvaluatedAudioState extends BaseElementState {
  type: "audio";
  assetId: string;
  sourceTime: Time;
  volume: number;
}

export interface EvaluatedShapeState extends BaseElementState {
  type: "shape";
  shapeType: ShapeType;
  shapeData: ShapeData;
  style: ShapeStyle;
}

export interface EvaluatedGroupState extends BaseElementState {
  type: "group";
  children: BaseElementState[];
}

export type EvaluatedElement =
  | EvaluatedTextState
  | EvaluatedImageState
  | EvaluatedVideoState
  | EvaluatedAudioState
  | EvaluatedShapeState
  | EvaluatedGroupState
  | BaseElementState;
