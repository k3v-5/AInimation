import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { StyleProfileManager } from "../../styles/StyleProfileManager.js";
import { ProductionDSLCompiler, DeclarativeProductionIntent } from "../../dsl/ProductionDSL.js";
import { CreativePlanner } from "../../ai-planner/creative/CreativePlanner.js";
import { ProductionJobQueue } from "../../runtime/jobs/ProductionJobQueue.js";

describe("Autonomous MCP v2 — Production OS, DSL & Batch Systems", () => {
  it("retrieves and validates master StyleProfiles", () => {
    const profiles = StyleProfileManager.getAllProfiles();
    assert.equal(profiles.length, 19);

    const timeProfile = StyleProfileManager.getProfile("time_editorial_impact");
    assert.equal(timeProfile.typography.fontFamily, "Impact");
    assert.equal(timeProfile.typography.verticalStretchPct, 130);
    assert.equal(timeProfile.soundDesign.autoDuckingDb, -3.5);

    const tiktokProfile = StyleProfileManager.getProfile("tiktok_retention_master");
    assert.equal(tiktokProfile.typography.fontFamily, "Arial Black");
    assert.equal(tiktokProfile.motion.transitionType, "zoom");
  });

  it("compiles Declarative Production DSL into canonical ProjectIR in 1 step", () => {
    const intent: DeclarativeProductionIntent = {
      video: {
        format: "9:16",
        durationSec: 30.0,
        projectName: "Viral_Reel_Project",
      },
      style: {
        preset: "time_editorial_impact",
        title: "HOW AI IS CHANGING EDITING",
      },
      editing: {
        pacing: "aggressive",
        beatSync: true,
        speedRamping: true,
        depthSandwich: true,
      },
      captions: {
        enabled: true,
        text: "THIS IS THE FUTURE OF MOTION GRAPHICS",
      },
      soundDesign: {
        enabled: true,
        autoDucking: true,
      },
    };

    const compiled = ProductionDSLCompiler.compile(intent);
    assert.equal(compiled.composition.width, 1080);
    assert.equal(compiled.composition.height, 1920);
    assert.equal(compiled.composition.duration, 30.0);
    assert.ok(compiled.appliedProfile.includes("TIME Magazine"));
  });

  it("plans structured narrative arcs and pacing curves via CreativePlanner", () => {
    const plan = CreativePlanner.createNarrativePlan("LUXURY WATCH LAUNCH", 45.0, "visual_punch");
    assert.equal(plan.segments.length, 5);
    assert.equal(plan.segments[0].purpose, "hook");
    assert.ok(plan.segments[0].duration <= 3.0);
    assert.equal(plan.segments[3].purpose, "climax_drop");
    assert.equal(plan.segments[3].energyLevel, 10);
    assert.equal(plan.pacingCurve.length, 5);
  });

  it("processes batch jobs in ProductionJobQueue with priority and high acceptance rate", async () => {
    const queue = new ProductionJobQueue();

    // Encolar 3 trabajos con diferentes prioridades
    queue.enqueue({
      priority: "normal",
      intent: {
        video: { format: "9:16", durationSec: 15.0 },
        style: { preset: "time_editorial_impact", title: "Job 1 Normal" },
        editing: { pacing: "aggressive", beatSync: true, speedRamping: false, depthSandwich: true },
      },
    });

    queue.enqueue({
      priority: "high",
      intent: {
        video: { format: "9:16", durationSec: 20.0 },
        style: { preset: "tiktok_retention_master", title: "Job 2 High Priority" },
        editing: { pacing: "aggressive", beatSync: true, speedRamping: true, depthSandwich: false },
      },
    });

    const summary = await queue.processBatch();
    assert.equal(summary.totalJobs, 2);
    assert.equal(summary.completed, 2);
    assert.equal(summary.failed, 0);
    assert.equal(summary.humanAcceptanceRatePct, 100.0);
    assert.ok(summary.averageMCPCalls < 30);
  });
});
