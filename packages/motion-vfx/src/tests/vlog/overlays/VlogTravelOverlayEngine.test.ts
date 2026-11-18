import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { RoutePath } from "../../../vlog/contracts/travel-overlays.types.js";
import { VlogTravelOverlayEngine } from "../../../vlog/overlays/vlog-travel-overlay-engine.js";

describe("Milestone 6-E — Vlog Travel Overlay Engine Suite", () => {
  it("creates a safe GeoBadge overlay item", () => {
    const item = VlogTravelOverlayEngine.createGeoBadgeItem(
      {
        id: "badge_gdl",
        cityName: "Guadalajara",
        countryName: "México",
        countryCode: "MX",
        coordinates: { latitude: 20.6597, longitude: -103.3496 },
        stylePreset: "editorial_red",
      },
      2.0,
      4.0,
      { aspectRatio: "16:9" }
    );

    assert.equal(item.id, "badge_gdl");
    assert.equal(item.type, "GEO_BADGE");
    assert.equal(item.timelineStartSeconds, 2.0);
    assert.equal(item.timelineEndSeconds, 6.0);
    assert.equal(item.safeZoneCompliance, true);
    assert.equal(item.priority, 2);
  });

  it("creates a LocationCard overlay item", () => {
    const item = VlogTravelOverlayEngine.createLocationCardItem(
      {
        id: "loc_tequila",
        title: "Destilería La Rojeña",
        subtitle: "Pueblo Mágico",
        region: "Tequila, Jalisco",
        durationSeconds: 4.5,
      },
      10.0,
      { aspectRatio: "16:9" }
    );

    assert.equal(item.type, "LOCATION_CARD");
    assert.equal(item.timelineStartSeconds, 10.0);
    assert.equal(item.timelineEndSeconds, 14.5);
    assert.equal(item.safeZoneCompliance, true);
    assert.equal(item.priority, 3);
  });

  it("creates a RoutePath item and calculates Haversine distance", () => {
    const item = VlogTravelOverlayEngine.createRoutePathItem(
      {
        id: "route_jalisco",
        points: [
          { id: "pt1", name: "Guadalajara", latitude: 20.6597, longitude: -103.3496 },
          { id: "pt2", name: "Tequila", latitude: 20.8863, longitude: -103.8372 },
        ],
        travelMode: "driving",
        animationDurationSeconds: 3.0,
        trimPathsStart: 0,
        trimPathsEnd: 100,
      },
      5.0
    );

    assert.equal(item.type, "ROUTE_MAP");
    const routeData = item.data as RoutePath;
    assert.ok(routeData.totalDistanceKm > 50 && routeData.totalDistanceKm < 70);
  });

  it("creates a Polaroid item with synchronized shutter SFX buffer", () => {
    const { item, shutterSfxBuffer } = VlogTravelOverlayEngine.createPolaroidItem({
      id: "pol_agave",
      freezeTimestampSeconds: 8.0,
      captionText: "Campos de Agave Azul",
    });

    assert.equal(item.type, "POLAROID_FREEZE");
    assert.equal(item.priority, 5); // Máxima prioridad
    assert.ok(shutterSfxBuffer.length > 44);
  });

  it("builds a full overlay track and guarantees deterministic SHA-256", () => {
    const badge = VlogTravelOverlayEngine.createGeoBadgeItem(
      { id: "b1", cityName: "Madrid" },
      0.0,
      3.0
    );
    const loc = VlogTravelOverlayEngine.createLocationCardItem(
      { id: "l1", title: "Plaza Mayor", region: "Madrid", durationSeconds: 4.0 },
      2.0
    );

    const track1 = VlogTravelOverlayEngine.buildOverlayTrack("track_01", [badge, loc]);
    const track2 = VlogTravelOverlayEngine.buildOverlayTrack("track_01", [badge, loc]);

    assert.equal(track1.checksumSha256, track2.checksumSha256);
    assert.equal(track1.items.length, 2);
    // Orden cronológico
    assert.equal(track1.items[0].id, "b1");
    assert.equal(track1.items[1].id, "l1");
  });
});
