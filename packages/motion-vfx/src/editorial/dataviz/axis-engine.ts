import { DataVizElement, Point2D, Rect } from "./types.js";

export interface AxisConfig {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  color: string;
  thicknessPx: number;
  ticks?: { position: Point2D; label: string; value: number }[];
}

/**
 * REQ-025 §95: Axis & Baseline Geometry Engine.
 */
export class AxisEngine {
  public static createAxisElement(id: string, config: AxisConfig, datasetId?: string): DataVizElement {
    return {
      id,
      type: "AXIS",
      position: { x: config.x1, y: config.y1 },
      bounds: {
        x: Math.min(config.x1, config.x2),
        y: Math.min(config.y1, config.y2),
        width: Math.abs(config.x2 - config.x1) || config.thicknessPx,
        height: Math.abs(config.y2 - config.y1) || config.thicknessPx,
      },
      dataBinding: datasetId ? { datasetId, dataPointId: id, sourcePath: "axis" } : undefined,
      properties: {
        x1: config.x1,
        y1: config.y1,
        x2: config.x2,
        y2: config.y2,
        color: config.color,
        thicknessPx: config.thicknessPx,
        ticks: config.ticks ?? [],
      },
    };
  }
}
