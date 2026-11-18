import { Vec2 } from "../../masks/types/index.js";
import { AnchorPosition, SafeAreaInsets, StackLayoutOptions } from "../types/index.js";

/**
 * Motor de posicionamiento y distribución semántica de interfaces y gráficos (Fase 5J).
 */
export class LayoutEngine {
  public static readonly DEFAULT_SAFE_AREAS_9_16: SafeAreaInsets = {
    top: 150, // Evita la barra de estado y filtros superiores
    bottom: 320, // Evita botones de descripción, música y comentarios
    left: 40,
    right: 130, // Evita la columna de botones de interacción lateral (like, share, etc.)
  };

  /**
   * Calcula la posición (x, y) de un elemento en base a su punto de anclaje canónico.
   */
  public static calculateAnchorPosition(
    anchor: AnchorPosition,
    elementWidth: number,
    elementHeight: number,
    containerWidth: number,
    containerHeight: number,
    insets: SafeAreaInsets = { top: 0, bottom: 0, left: 0, right: 0 }
  ): Vec2 {
    const usableLeft = insets.left;
    const usableRight = containerWidth - insets.right;
    const usableTop = insets.top;
    const usableBottom = containerHeight - insets.bottom;

    const usableWidth = Math.max(0, usableRight - usableLeft);
    const usableHeight = Math.max(0, usableBottom - usableTop);

    let x = usableLeft;
    let y = usableTop;

    // Calcular coordenada X
    if (anchor.endsWith("-left")) {
      x = usableLeft;
    } else if (anchor.endsWith("-center") || anchor === "center") {
      x = usableLeft + (usableWidth - elementWidth) / 2;
    } else if (anchor.endsWith("-right")) {
      x = usableRight - elementWidth;
    }

    // Calcular coordenada Y
    if (anchor.startsWith("top-")) {
      y = usableTop;
    } else if (anchor.startsWith("center-") || anchor === "center") {
      y = usableTop + (usableHeight - elementHeight) / 2;
    } else if (anchor.startsWith("bottom-")) {
      y = usableBottom - elementHeight;
    }

    return { x, y };
  }

  /**
   * Dispone una lista de elementos en pila (horizontal o vertical) calculando sus desplazamientos relativos.
   */
  public static layoutStack(
    elements: Array<{ width: number; height: number }>,
    options: StackLayoutOptions
  ): Vec2[] {
    const positions: Vec2[] = [];
    let currentOffset = 0;

    for (let i = 0; i < elements.length; i++) {
      const el = elements[i];
      if (options.direction === "horizontal") {
        positions.push({ x: currentOffset, y: 0 });
        currentOffset += el.width + options.gap;
      } else {
        positions.push({ x: 0, y: currentOffset });
        currentOffset += el.height + options.gap;
      }
    }

    return positions;
  }
}
