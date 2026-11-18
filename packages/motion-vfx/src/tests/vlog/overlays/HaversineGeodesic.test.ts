import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { HaversineGeodesic } from "../../../vlog/overlays/haversine-geodesic.js";

describe("Milestone 6-C — Haversine Geodesic Suite", () => {
  it("calculates accurate distance between known cities (CDMX to Guadalajara)", () => {
    // CDMX: 19.4326, -99.1332
    // Guadalajara: 20.6597, -103.3496
    // Distancia geodésica real conocida ~460 km
    const dist = HaversineGeodesic.calculateDistanceKm(19.4326, -99.1332, 20.6597, -103.3496);

    assert.ok(dist >= 450 && dist <= 470, `Expected ~460km, got ${dist}km`);
  });

  it("calculates 0km for identical coordinates", () => {
    const dist = HaversineGeodesic.calculateDistanceKm(48.8566, 2.3522, 48.8566, 2.3522);
    assert.equal(dist, 0.0);
  });

  it("calculates cumulative route distance across multiple waypoints", () => {
    const points = [
      { id: "p1", name: "Madrid", latitude: 40.4168, longitude: -3.7038 },
      { id: "p2", name: "Barcelona", latitude: 41.3879, longitude: 2.1699 },
      { id: "p3", name: "Valencia", latitude: 39.4699, longitude: -0.3763 },
    ];

    const totalDist = HaversineGeodesic.calculateTotalRouteDistanceKm(points);
    assert.ok(totalDist > 700 && totalDist < 900, `Expected ~800km, got ${totalDist}km`);
  });

  it("PBT: Haversine distance is strictly symmetric d(A,B) == d(B,A) and non-negative", () => {
    fc.assert(
      fc.property(
        fc.double({ min: -85.0, max: 85.0, noNaN: true }),
        fc.double({ min: -175.0, max: 175.0, noNaN: true }),
        fc.double({ min: -85.0, max: 85.0, noNaN: true }),
        fc.double({ min: -175.0, max: 175.0, noNaN: true }),
        (lat1, lon1, lat2, lon2) => {
          const d1 = HaversineGeodesic.calculateDistanceKm(lat1, lon1, lat2, lon2);
          const d2 = HaversineGeodesic.calculateDistanceKm(lat2, lon2, lat1, lon1);

          assert.ok(d1 >= 0.0);
          assert.equal(d1, d2);
        }
      )
    );
  });
});
