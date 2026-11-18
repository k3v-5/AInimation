import { z } from "zod";

/** Tipos de overlays de viaje */
export type VlogOverlayType =
  | "GEO_BADGE"
  | "LOCATION_CARD"
  | "TIME_BADGE"
  | "ROUTE_MAP"
  | "ROUTE_PATH"
  | "POLAROID_FREEZE"
  | "CHAPTER_CARD"
  | "PHOTO_CARD";

export const VlogOverlayTypeSchema = z.enum([
  "GEO_BADGE",
  "LOCATION_CARD",
  "TIME_BADGE",
  "ROUTE_MAP",
  "ROUTE_PATH",
  "POLAROID_FREEZE",
  "CHAPTER_CARD",
  "PHOTO_CARD",
]);

/** Datos para insignia geográfica (Geo-Badge) */
export interface GeoBadge {
  id: string;
  cityName: string;
  countryName?: string;
  countryCode?: string; // ISO 3166-1 alpha-2 ej. "MX", "ES", "JP"
  coordinates?: {
    latitude: number; // [-90, 90]
    longitude: number; // [-180, 180]
  };
  altitudeMeters?: number;
  localTime?: string; // ej. "14:30"
  weatherTemperatureC?: number;
  stylePreset?: "editorial_red" | "dark_minimal" | "cyber_neon" | "vintage_stamp";
}

export const GeoBadgeSchema = z.object({
  id: z.string().min(1),
  cityName: z.string().min(1),
  countryName: z.string().optional(),
  countryCode: z.string().max(2).optional(),
  coordinates: z.object({
    latitude: z.number().min(-90).max(90),
    longitude: z.number().min(-180).max(180),
  }).optional(),
  altitudeMeters: z.number().optional(),
  localTime: z.string().optional(),
  weatherTemperatureC: z.number().optional(),
  stylePreset: z.enum(["editorial_red", "dark_minimal", "cyber_neon", "vintage_stamp"]).default("editorial_red"),
});

/** Tarjeta de ubicación (Location Card) con jerarquía visual */
export interface LocationCard {
  id: string;
  title: string; // ej. "Catedral de Guadalajara"
  subtitle?: string; // ej. "Centro Histórico"
  region: string; // ej. "Jalisco, México"
  categoryTag?: string; // ej. "Arquitectura", "Gastronomía"
  durationSeconds: number;
}

export const LocationCardSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1),
  subtitle: z.string().optional(),
  region: z.string().min(1),
  categoryTag: z.string().optional(),
  durationSeconds: z.number().positive().default(4.0),
});

/** Punto de ruta para mapas interactivos y cálculo Haversine */
export interface RoutePoint {
  id: string;
  name: string;
  latitude: number; // [-90, 90]
  longitude: number; // [-180, 180]
  timestamp?: number;
  markerIcon?: "pin" | "dot" | "airport" | "camera";
}

export const RoutePointSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
  timestamp: z.number().optional(),
  markerIcon: z.enum(["pin", "dot", "airport", "camera"]).default("pin"),
});

/** Ruta animada con cálculo geodésico y trazado vectorial */
export interface RoutePath {
  id: string;
  points: RoutePoint[];
  totalDistanceKm: number; // Calculada con fórmula Haversine
  travelMode: "flight" | "driving" | "walking" | "train";
  animationDurationSeconds: number;
  trimPathsStart: number; // [0, 100]%
  trimPathsEnd: number; // [0, 100]%
}

export const RoutePathSchema = z.object({
  id: z.string().min(1),
  points: z.array(RoutePointSchema).min(2),
  totalDistanceKm: z.number().min(0),
  travelMode: z.enum(["flight", "driving", "walking", "train"]).default("driving"),
  animationDurationSeconds: z.number().positive().default(3.0),
  trimPathsStart: z.number().min(0).max(100).default(0),
  trimPathsEnd: z.number().min(0).max(100).default(100),
});

/** Congelación fotográfica tipo Polaroid con marco, rotación y audio obturador */
export interface PolaroidFreezeFrame {
  id: string;
  freezeTimestampSeconds: number;
  holdDurationSeconds: number; // Duración del freeze ej. 2.0s
  rotationDegrees: number; // [-15, 15] determinista basado en seed
  captionText?: string;
  handwrittenFont?: string;
  pinTackColor?: string;
  dropShadow: {
    opacity: number; // [0, 1]
    distancePx: number;
    softnessPx: number;
  };
  shutterSfxSyncSeconds: number; // Timestamp exacto del SFX del obturador (±1 frame)
}

export const PolaroidFreezeFrameSchema = z.object({
  id: z.string().min(1),
  freezeTimestampSeconds: z.number().min(0),
  holdDurationSeconds: z.number().positive().default(2.0),
  rotationDegrees: z.number().min(-15).max(15).default(0),
  captionText: z.string().optional(),
  handwrittenFont: z.string().optional(),
  pinTackColor: z.string().optional(),
  dropShadow: z.object({
    opacity: z.number().min(0).max(1).default(0.4),
    distancePx: z.number().min(0).default(15),
    softnessPx: z.number().min(0).default(20),
  }),
  shutterSfxSyncSeconds: z.number().min(0),
});

/** Definición unificada de un overlay en la línea temporal */
export interface VlogOverlayItem {
  id: string;
  type: VlogOverlayType;
  timelineStartSeconds: number;
  timelineEndSeconds: number;
  durationSeconds: number;
  data: GeoBadge | LocationCard | RoutePath | PolaroidFreezeFrame;
  safeZoneCompliance: boolean;
  priority: number; // Mayor número = mayor prioridad de colisión
}
