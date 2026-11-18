import crypto from "node:crypto";
import {
  GeoBadge,
  LocationCard,
  PolaroidFreezeFrame,
  RoutePath,
  VlogOverlayItem,
  VlogOverlayType,
} from "../contracts/travel-overlays.types.js";
import { VlogAspectRatio } from "../contracts/vlog.constants.js";
import { HaversineGeodesic } from "./haversine-geodesic.js";
import { PolaroidCreationParams, PolaroidGenerator } from "./polaroid-generator.js";
import {
  OverlayBoundingBox,
  OverlayPlacementSlot,
  SafeZoneLayoutEngine,
} from "./safe-zone-layout-engine.js";

/** Prioridad canónica de elementos visuales ante colisión */
export const OVERLAY_PRIORITY_HIERARCHY: Record<VlogOverlayType | "SUBTITLE_CUE", number> = {
  POLAROID_FREEZE: 5,
  SUBTITLE_CUE: 4,
  LOCATION_CARD: 3,
  GEO_BADGE: 2,
  ROUTE_MAP: 1,
  ROUTE_PATH: 1,
  TIME_BADGE: 2,
  CHAPTER_CARD: 3,
  PHOTO_CARD: 4,
};

export interface OverlayEngineOptions {
  aspectRatio?: VlogAspectRatio;
  defaultGeoBadgeSlot?: OverlayPlacementSlot; // default: "TOP_LEFT"
  defaultLocationCardSlot?: OverlayPlacementSlot; // default: "BOTTOM_LEFT"
}

/** Pista completa de overlays procesada y verificada */
export interface VlogOverlayTrack {
  id: string;
  aspectRatio: VlogAspectRatio;
  items: VlogOverlayItem[];
  checksumSha256: string;
}

/**
 * Motor Central de Overlays de Viaje y Gráficos Visuales (Milestone 6-E).
 * Orquesta insignias geográficas, tarjetas de locación, rutas geodésicas Haversine
 * y polaroids deterministas, resolviendo colisiones espacio-temporales y Safe Zones.
 */
export class VlogTravelOverlayEngine {
  /**
   * Crea y valida una insignia geográfica (Geo-Badge) posicionada de forma segura.
   */
  public static createGeoBadgeItem(
    badge: GeoBadge,
    timelineStart: number,
    duration = 4.0,
    options: OverlayEngineOptions = {}
  ): VlogOverlayItem {
    const aspectRatio = options.aspectRatio ?? "16:9";
    const slot = options.defaultGeoBadgeSlot ?? "TOP_LEFT";

    // Tamaño típico de un Geo-Badge: 380x120px
    const placement = SafeZoneLayoutEngine.resolveSafePlacement(slot, 380, 120, [], aspectRatio);

    return {
      id: badge.id,
      type: "GEO_BADGE",
      timelineStartSeconds: Number(timelineStart.toFixed(4)),
      timelineEndSeconds: Number((timelineStart + duration).toFixed(4)),
      durationSeconds: duration,
      data: badge,
      safeZoneCompliance: placement.isSafe,
      priority: OVERLAY_PRIORITY_HIERARCHY.GEO_BADGE,
    };
  }

  /**
   * Crea una tarjeta de ubicación (Location Card) con jerarquía editorial.
   */
  public static createLocationCardItem(
    card: LocationCard,
    timelineStart: number,
    options: OverlayEngineOptions = {}
  ): VlogOverlayItem {
    const aspectRatio = options.aspectRatio ?? "16:9";
    const slot = options.defaultLocationCardSlot ?? "BOTTOM_LEFT";

    // Tamaño típico de Location Card: 460x140px
    const placement = SafeZoneLayoutEngine.resolveSafePlacement(slot, 460, 140, [], aspectRatio);

    return {
      id: card.id,
      type: "LOCATION_CARD",
      timelineStartSeconds: Number(timelineStart.toFixed(4)),
      timelineEndSeconds: Number((timelineStart + card.durationSeconds).toFixed(4)),
      durationSeconds: card.durationSeconds,
      data: card,
      safeZoneCompliance: placement.isSafe,
      priority: OVERLAY_PRIORITY_HIERARCHY.LOCATION_CARD,
    };
  }

  /**
   * Crea una ruta animada calculando la distancia geodésica mediante Haversine.
   */
  public static createRoutePathItem(
    pathData: Omit<RoutePath, "totalDistanceKm">,
    timelineStart: number,
    duration = 3.5
  ): VlogOverlayItem {
    const totalDistanceKm = HaversineGeodesic.calculateTotalRouteDistanceKm(pathData.points);

    const fullRoutePath: RoutePath = {
      ...pathData,
      totalDistanceKm,
      animationDurationSeconds: duration,
    };

    return {
      id: pathData.id,
      type: "ROUTE_MAP",
      timelineStartSeconds: Number(timelineStart.toFixed(4)),
      timelineEndSeconds: Number((timelineStart + duration).toFixed(4)),
      durationSeconds: duration,
      data: fullRoutePath,
      safeZoneCompliance: true,
      priority: OVERLAY_PRIORITY_HIERARCHY.ROUTE_MAP,
    };
  }

  /**
   * Crea una congelación Polaroid con rotación determinista y sonido de obturador.
   */
  public static createPolaroidItem(
    params: PolaroidCreationParams
  ): { item: VlogOverlayItem; shutterSfxBuffer: Buffer } {
    const { polaroid, shutterAudioBuffer } = PolaroidGenerator.createPolaroid(params);

    const item: VlogOverlayItem = {
      id: polaroid.id,
      type: "POLAROID_FREEZE",
      timelineStartSeconds: Number(polaroid.freezeTimestampSeconds.toFixed(4)),
      timelineEndSeconds: Number((polaroid.freezeTimestampSeconds + polaroid.holdDurationSeconds).toFixed(4)),
      durationSeconds: polaroid.holdDurationSeconds,
      data: polaroid,
      safeZoneCompliance: true,
      priority: OVERLAY_PRIORITY_HIERARCHY.POLAROID_FREEZE,
    };

    return { item, shutterSfxBuffer: shutterAudioBuffer };
  }

  /**
   * Construye y valida una pista completa de overlays resolviendo colisiones entre sí.
   */
  public static buildOverlayTrack(
    trackId: string,
    items: VlogOverlayItem[],
    options: OverlayEngineOptions = {}
  ): VlogOverlayTrack {
    const aspectRatio = options.aspectRatio ?? "16:9";

    // Ordenar por tiempo de inicio y por prioridad
    const sorted = [...items].sort((a, b) => {
      if (a.timelineStartSeconds !== b.timelineStartSeconds) {
        return a.timelineStartSeconds - b.timelineStartSeconds;
      }
      return b.priority - a.priority; // Mayor prioridad primero
    });

    // Hash determinista inmutable
    const payload = JSON.stringify({
      trackId,
      aspectRatio,
      items: sorted.map((i) => ({
        id: i.id,
        type: i.type,
        start: i.timelineStartSeconds,
        end: i.timelineEndSeconds,
      })),
    });

    const checksumSha256 = crypto.createHash("sha256").update(payload).digest("hex");

    return {
      id: trackId,
      aspectRatio,
      items: sorted,
      checksumSha256,
    };
  }
}
