import { Transform } from "../../transform/Transform.js";
import { ChartData, CounterFormat, GraphicElement } from "../types/index.js";

/**
 * Formateador inteligente de contadores para números y métricas (Fase 5J).
 */
export class CounterFormatter {
  public static format(value: number, format: CounterFormat = "integer"): string {
    const rounded = Math.round(value * 100) / 100;

    switch (format) {
      case "compact": {
        if (Math.abs(rounded) >= 1_000_000) {
          return `${(rounded / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`;
        }
        if (Math.abs(rounded) >= 1_000) {
          return `${(rounded / 1_000).toFixed(1).replace(/\.0$/, "")}K`;
        }
        return `${rounded}`;
      }
      case "currency":
        return `$${rounded.toLocaleString("en-US")}`;
      case "percentage":
        return `${Math.round(rounded)}%`;
      case "integer":
      default:
        return Math.round(rounded).toLocaleString("en-US");
    }
  }
}

/**
 * Generador de elementos de componentes gráficos semánticos (Fase 5J).
 */
export class GraphicComponents {
  /**
   * Genera los elementos gráficos de una barra de progreso animable.
   */
  public static createProgressBar(
    value: number,
    min = 0,
    max = 100,
    width = 400,
    height = 24
  ): GraphicElement[] {
    const normalized = Math.max(0, Math.min(1, (value - min) / (max - min || 1)));
    const fillWidth = Math.max(2, width * normalized);

    const background: GraphicElement = {
      id: "pb_bg",
      geometry: { type: "rounded-rectangle", width, height, radius: height / 2 },
      style: {
        fill: { type: "solid", color: { r: 0.2, g: 0.2, b: 0.2, a: 0.8 } },
        opacity: 1.0,
      },
      transform: new Transform(),
    };

    const fill: GraphicElement = {
      id: "pb_fill",
      geometry: { type: "rounded-rectangle", width: fillWidth, height, radius: height / 2 },
      style: {
        fill: { type: "solid", color: { r: 0.0, g: 0.8, b: 1.0, a: 1.0 } },
        opacity: 1.0,
      },
      transform: new Transform(),
    };

    return [background, fill];
  }

  /**
   * Genera las barras geométricas de un gráfico de barras simple.
   */
  public static createBarChart(data: ChartData, width = 500, height = 300): GraphicElement[] {
    const count = data.values.length;
    if (count === 0) return [];

    const elements: GraphicElement[] = [];
    const maxVal = Math.max(...data.values, 1);
    const barWidth = (width / count) * 0.7;
    const spacing = width / count;

    for (let i = 0; i < count; i++) {
      const val = data.values[i];
      const barHeight = Math.max(4, (val / maxVal) * (height - 40));
      const color = data.colors?.[i] ?? { r: 1.0, g: 0.6, b: 0.0, a: 1.0 };

      const bar: GraphicElement = {
        id: `bar_${i}`,
        geometry: {
          type: "rounded-rectangle",
          width: barWidth,
          height: barHeight,
          radius: 4,
        },
        style: {
          fill: { type: "solid", color },
          opacity: 1.0,
        },
        transform: new Transform({
          position: {
            x: i * spacing + spacing / 2 - barWidth / 2,
            y: height - barHeight,
          },
        }),
      };

      elements.push(bar);
    }

    return elements;
  }
}
