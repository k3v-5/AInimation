import { DataVizElement, Rect } from "./types.js";

export interface LegendItem {
  label: string;
  color: string;
  category?: string;
}

/**
 * REQ-025: Categorical Legend Engine.
 */
export class LegendEngine {
  public static createLegendElements(
    idPrefix: string,
    items: LegendItem[],
    contentBounds: Rect
  ): DataVizElement[] {
    const elements: DataVizElement[] = [];
    const itemHeight = 24;
    const startX = contentBounds.x;
    const startY = contentBounds.y + 10;

    let currentX = startX;

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      const estimatedWidth = 20 + item.label.length * 8 + 16;

      elements.push({
        id: `${idPrefix}_item_${i}`,
        type: "CARD",
        position: { x: currentX, y: startY },
        bounds: { x: currentX, y: startY, width: estimatedWidth, height: itemHeight },
        properties: {
          label: item.label,
          color: item.color,
          category: item.category,
        },
      });

      currentX += estimatedWidth;
    }

    return elements;
  }
}
