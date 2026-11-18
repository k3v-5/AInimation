export type VisualizationAspectRatio = "16:9" | "9:16" | "1:1";

export interface VisualizationBoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface CanvasDimensions {
  width: number;
  height: number;
}

/**
 * REQ-4I-047 & REQ-4I-048: Safe Zone & Responsive Layout Resolver for Data Visualizations.
 */
export class VisualizationLayout {
  public static getCanvasDimensions(aspectRatio: VisualizationAspectRatio): CanvasDimensions {
    switch (aspectRatio) {
      case "9:16":
        return { width: 1080, height: 1920 };
      case "1:1":
        return { width: 1080, height: 1080 };
      case "16:9":
      default:
        return { width: 1920, height: 1080 };
    }
  }

  /**
   * Calculates safe printable bounding box reserving margin for platform UI exclusions.
   */
  public static getSafeContentArea(aspectRatio: VisualizationAspectRatio): VisualizationBoundingBox {
    const canvas = this.getCanvasDimensions(aspectRatio);

    switch (aspectRatio) {
      case "9:16":
        // Reserved: 250px top (header), 450px bottom (captions/audio), 120px right (engagement buttons)
        return {
          x: 100,
          y: 280,
          width: canvas.width - 100 - 140, // 840px
          height: canvas.height - 280 - 460, // 1180px
        };
      case "1:1":
        return {
          x: 90,
          y: 90,
          width: canvas.width - 180,
          height: canvas.height - 180,
        };
      case "16:9":
      default:
        // 10% EBU Title Safe
        return {
          x: 192,
          y: 108,
          width: canvas.width - 384, // 1536px
          height: canvas.height - 216, // 864px
        };
    }
  }
}
