import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { ProductionDSLCompiler, DeclarativeProductionIntent } from "../../dsl/ProductionDSL.js";

describe("Milestone 15 — Declarative Production DSL Vlog Integration Suite", () => {
  it("preserves 100% backward compatibility when vlog block is omitted", () => {
    const intent: DeclarativeProductionIntent = {
      video: {
        format: "16:9",
        durationSec: 60.0,
        projectName: "Classic_Project",
      },
      style: {
        preset: "time_editorial_poster",
        title: "TIME EXCLUSIVE",
      },
      editing: {
        pacing: "aggressive",
        beatSync: true,
        speedRamping: false,
        depthSandwich: false,
      },
    };

    const res = ProductionDSLCompiler.compile(intent);
    assert.equal(res.composition.name, "Classic_Project");
    assert.equal(res.metadata.totalDuration, 60.0);
    assert.equal(res.vlogMetadata, undefined);
  });

  it("compiles declarative intent with vlog configuration and multilingual targets", () => {
    const intent: DeclarativeProductionIntent = {
      video: {
        format: "9:16",
        durationSec: 45.0,
        projectName: "Vlog_Shorts_9x16",
      },
      style: {
        preset: "cinematic_flow_vlog",
        title: "EXPLORING TOKYO",
      },
      editing: {
        pacing: "balanced",
        beatSync: true,
        speedRamping: true,
        depthSandwich: true,
      },
      vlog: {
        enabled: true,
        sourceLocale: "es-MX",
        targetLanguages: ["es-MX", "en-US", "pt-BR"],
        autoJumpCut: true,
        punchInScale: 1.15,
      },
    };

    const res = ProductionDSLCompiler.compile(intent);
    assert.equal(res.composition.width, 1080);
    assert.equal(res.composition.height, 1920);
    assert.ok(res.vlogMetadata !== undefined);
    assert.equal(res.vlogMetadata!.vlogModeActive, true);
    assert.equal(res.vlogMetadata!.autoJumpCut, true);
    assert.equal(res.vlogMetadata!.punchInScale, 1.15);
    assert.equal(res.vlogMetadata!.targetLanguages.length, 3);
    assert.equal(res.vlogMetadata!.hasTravelOverlays, false);
  });

  it("detects travel overlays when geoBadge or locationCard are configured", () => {
    const intent: DeclarativeProductionIntent = {
      video: {
        format: "16:9",
        durationSec: 30.0,
      },
      style: {
        preset: "johnny_harris_investigative",
        title: "ROUTE MAP",
      },
      editing: {
        pacing: "balanced",
        beatSync: false,
        speedRamping: false,
        depthSandwich: false,
      },
      vlog: {
        enabled: true,
        travelOverlays: {
          locationCard: {
            id: "loc_01",
            title: "Catedral de Guadalajara",
            region: "Jalisco, Mexico",
            durationSeconds: 4.0,
          },
        },
      },
    };

    const res = ProductionDSLCompiler.compile(intent);
    assert.ok(res.vlogMetadata !== undefined);
    assert.equal(res.vlogMetadata!.hasTravelOverlays, true);
  });

  it("PBT: estimated render duration is strictly positive and proportional to duration", () => {
    fc.assert(
      fc.property(
        fc.float({ min: 5.0, max: 600.0, noNaN: true }),
        fc.constantFrom("16:9", "9:16", "1:1"),
        (duration, format) => {
          const res = ProductionDSLCompiler.compile({
            video: { format: format as any, durationSec: duration },
            style: { preset: "time_editorial_poster", title: "Test" },
            editing: { pacing: "aggressive", beatSync: true, speedRamping: false, depthSandwich: false },
            vlog: { enabled: true },
          });

          return res.estimatedRenderDurationSec > 0.0 && res.estimatedRenderDurationSec <= duration;
        }
      ),
      { numRuns: 50 }
    );
  });
});
