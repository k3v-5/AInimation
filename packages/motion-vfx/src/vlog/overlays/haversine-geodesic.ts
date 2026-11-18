import { RoutePoint } from "../contracts/travel-overlays.types.js";
import { GEODESIC_CONSTANTS } from "../contracts/vlog.constants.js";

/**
 * Calculador Geodésico y Rutas Basado en la Fórmula de Haversine (Milestone 6-C).
 * Utiliza EARTH_MEAN_RADIUS_KM = 6371.0088 como radio canónico terrestre.
 */
export class HaversineGeodesic {
  public static readonly EARTH_MEAN_RADIUS_KM = GEODESIC_CONSTANTS.EARTH_MEAN_RADIUS_KM;

  /**
   * Calcula la distancia geodésica en kilómetros entre dos coordenadas geográficas.
   */
  public static calculateDistanceKm(
    lat1: number,
    lon1: number,
    lat2: number,
    lon2: number
  ): number {
    if (lat1 === lat2 && lon1 === lon2) {
      return 0.0;
    }

    const toRad = Math.PI / 180;
    const phi1 = lat1 * toRad;
    const phi2 = lat2 * toRad;
    const deltaPhi = (lat2 - lat1) * toRad;
    const deltaLambda = (lon2 - lon1) * toRad;

    const a =
      Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
      Math.cos(phi1) * Math.cos(phi2) *
      Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);

    const c = 2 * Math.atan2(Math.sqrt(Math.max(0, Math.min(1, a))), Math.sqrt(Math.max(0, 1 - a)));
    const distance = this.EARTH_MEAN_RADIUS_KM * c;

    return Number(distance.toFixed(4));
  }

  /**
   * Calcula la distancia total acumulada a lo largo de una secuencia de puntos de ruta.
   */
  public static calculateTotalRouteDistanceKm(points: RoutePoint[]): number {
    if (!points || points.length < 2) {
      return 0.0;
    }

    let total = 0.0;
    for (let i = 0; i < points.length - 1; i++) {
      total += this.calculateDistanceKm(
        points[i].latitude,
        points[i].longitude,
        points[i + 1].latitude,
        points[i + 1].longitude
      );
    }

    return Number(total.toFixed(4));
  }

  /**
   * Calcula el rumbo o acimut inicial en grados [0, 360) entre dos puntos.
   */
  public static calculateInitialBearingDegrees(
    lat1: number,
    lon1: number,
    lat2: number,
    lon2: number
  ): number {
    const toRad = Math.PI / 180;
    const phi1 = lat1 * toRad;
    const phi2 = lat2 * toRad;
    const deltaLambda = (lon2 - lon1) * toRad;

    const y = Math.sin(deltaLambda) * Math.cos(phi2);
    const x =
      Math.cos(phi1) * Math.sin(phi2) -
      Math.sin(phi1) * Math.cos(phi2) * Math.cos(deltaLambda);

    const theta = Math.atan2(y, x);
    const bearing = (theta * 180 / Math.PI + 360) % 360;

    return Number(bearing.toFixed(2));
  }
}
