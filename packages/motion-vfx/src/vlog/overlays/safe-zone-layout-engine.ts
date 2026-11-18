import { SafeZoneResolver, StandardSafeZoneProfiles } from "../../captions/safezones/SafeZoneResolver.js";
import { RectBounds } from "../../captions/types/index.js";
import { VlogAspectRatio } from "../contracts/vlog.constants.js";

export type OverlayPlacementSlot =
  | "TOP_LEFT"
  | "TOP_RIGHT"
  | "TOP_CENTER"
  | "CENTER"
  | "BOTTOM_LEFT"
  | "BOTTOM_RIGHT"
  | "BOTTOM_CENTER";

export interface OverlayBoundingBox {
  x: number; // Coordenadas en píxeles
  y: number;
  width: number;
  height: number;
}

export interface ScreenDimensions {
  width: number;
  height: number;
}

export interface LayoutPlacementResult {
  slot: OverlayPlacementSlot;
  box: OverlayBoundingBox;
  isSafe: boolean;
  conflictsDetected: string[];
}

/**
 * Motor de Disposición Espacial y Zonas Seguras Multi-Aspecto (Milestone 6-D).
 * Reutiliza y extiende SafeZoneResolver para posicionar gráficos y subtítulos
 * evitando colisiones entre sí y esquivando los controles de interfaz social en 9:16.
 */
export class SafeZoneLayoutEngine {
  /**
   * Obtiene las dimensiones estándar en píxeles para un aspect ratio.
   */
  public static getDimensionsForAspectRatio(aspectRatio: VlogAspectRatio): ScreenDimensions {
    switch (aspectRatio) {
      case "9:16":
        return { width: 1080, height: 1920 };
      case "1:1":
        return { width: 1080, height: 1080 };
      case "4:5":
        return { width: 1080, height: 1350 };
      case "21:9":
        return { width: 2560, height: 1080 };
      case "16:9":
      default:
        return { width: 1920, height: 1080 };
    }
  }

  /**
   * Obtiene las regiones prohibidas (ej. botones laterales y barra inferior de TikTok/Reels).
   */
  public static getForbiddenRegions(aspectRatio: VlogAspectRatio): RectBounds[] {
    if (aspectRatio === "9:16") {
      // Reutilizar regiones prohibidas canónicas de TikTok/Reels
      return StandardSafeZoneProfiles["tiktok-portrait"].forbiddenRegions ?? [];
    }

    const { width, height } = this.getDimensionsForAspectRatio(aspectRatio);
    // Margen seguro general del 5%
    return [
      { x: 0, y: 0, width, height: height * 0.05 }, // borde superior extremo
      { x: 0, y: height * 0.95, width, height: height * 0.05 }, // borde inferior extremo
    ];
  }

  /**
   * Calcula la caja delimitadora en píxeles para un slot de colocación.
   */
  public static calculateSlotBoundingBox(
    slot: OverlayPlacementSlot,
    itemWidth: number,
    itemHeight: number,
    aspectRatio: VlogAspectRatio = "16:9"
  ): OverlayBoundingBox {
    const { width, height } = this.getDimensionsForAspectRatio(aspectRatio);

    // Márgenes seguros canónicos
    const marginX = aspectRatio === "9:16" ? width * 0.08 : width * 0.05;
    const marginTop = aspectRatio === "9:16" ? height * 0.10 : height * 0.06;
    const marginBottom = aspectRatio === "9:16" ? height * 0.22 : height * 0.10;

    let x = marginX;
    let y = marginTop;

    switch (slot) {
      case "TOP_LEFT":
        x = marginX;
        y = marginTop;
        break;
      case "TOP_RIGHT":
        x = width - marginX - itemWidth;
        y = marginTop;
        break;
      case "TOP_CENTER":
        x = (width - itemWidth) / 2;
        y = marginTop;
        break;
      case "CENTER":
        x = (width - itemWidth) / 2;
        y = (height - itemHeight) / 2;
        break;
      case "BOTTOM_LEFT":
        x = marginX;
        y = height - marginBottom - itemHeight;
        break;
      case "BOTTOM_RIGHT":
        x = width - marginX - itemWidth;
        y = height - marginBottom - itemHeight;
        break;
      case "BOTTOM_CENTER":
        x = (width - itemWidth) / 2;
        y = height - marginBottom - itemHeight;
        break;
    }

    return {
      x: Math.round(x),
      y: Math.round(y),
      width: Math.round(itemWidth),
      height: Math.round(itemHeight),
    };
  }

  /**
   * Verifica si dos cajas delimitadoras colisionan espacialmente.
   */
  public static doBoxesOverlap(boxA: OverlayBoundingBox, boxB: OverlayBoundingBox): boolean {
    return (
      boxA.x < boxB.x + boxB.width &&
      boxA.x + boxA.width > boxB.x &&
      boxA.y < boxB.y + boxB.height &&
      boxA.y + boxA.height > boxB.y
    );
  }

  /**
   * Verifica si una caja invade alguna región prohibida de interfaz social.
   */
  public static intersectsForbiddenRegions(box: OverlayBoundingBox, forbidden: RectBounds[]): boolean {
    for (const f of forbidden) {
      const fBox: OverlayBoundingBox = { x: f.x, y: f.y, width: f.width, height: f.height };
      if (this.doBoxesOverlap(box, fBox)) {
        return true;
      }
    }
    return false;
  }

  /**
   * Resuelve el slot seguro óptimo para un overlay, desplazándolo si colisiona.
   */
  public static resolveSafePlacement(
    preferredSlot: OverlayPlacementSlot,
    itemWidth: number,
    itemHeight: number,
    existingObstacles: OverlayBoundingBox[] = [],
    aspectRatio: VlogAspectRatio = "16:9"
  ): LayoutPlacementResult {
    const forbidden = this.getForbiddenRegions(aspectRatio);

    // Lista de slots alternativos en orden de preferencia
    const candidateSlots: OverlayPlacementSlot[] = [
      preferredSlot,
      "TOP_LEFT",
      "TOP_RIGHT",
      "TOP_CENTER",
      "BOTTOM_LEFT",
      "BOTTOM_RIGHT",
      "BOTTOM_CENTER",
      "CENTER",
    ];

    const uniqueCandidates = Array.from(new Set(candidateSlots));

    for (const slot of uniqueCandidates) {
      const box = this.calculateSlotBoundingBox(slot, itemWidth, itemHeight, aspectRatio);

      const hitsForbidden = this.intersectsForbiddenRegions(box, forbidden);
      const hitsObstacle = existingObstacles.some((obs) => this.doBoxesOverlap(box, obs));

      if (!hitsForbidden && !hitsObstacle) {
        return {
          slot,
          box,
          isSafe: true,
          conflictsDetected: [],
        };
      }
    }

    // Si todos los slots tienen obstáculos, entregar preferredSlot con advertencia
    const fallbackBox = this.calculateSlotBoundingBox(preferredSlot, itemWidth, itemHeight, aspectRatio);
    return {
      slot: preferredSlot,
      box: fallbackBox,
      isSafe: false,
      conflictsDetected: ["Unable to find conflict-free slot: all candidate positions overlap"],
    };
  }
}
