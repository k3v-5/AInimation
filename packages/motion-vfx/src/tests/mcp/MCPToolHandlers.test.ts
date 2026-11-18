import { describe, it, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { handleCreateVideoFromScript } from "../../mcp/tools/create-video-from-script.js";
import { handleApplyViralCaptionStyle } from "../../mcp/tools/apply-viral-caption-style.js";
import { handleGetTimelinePreviewFrame } from "../../mcp/tools/get-timeline-preview-frame.js";
import { handleExportAfterEffectsJSX } from "../../mcp/tools/export-after-effects-jsx.js";
import { MCPProjectStore } from "../../mcp/types.js";

describe("Fase 17 — MCP High-Level Tool Handlers Tests", () => {
  beforeEach(() => {
    MCPProjectStore.clear();
  });

  it("executes the full AI project lifecycle across the 4 MCP tools", async () => {
    // 1. Tool 1: create_video_from_script
    const createResult = await handleCreateVideoFromScript({
      script: "Aprende a editar videos como un profesional utilizando inteligencia artificial determinista.",
      styleId: "fast-tiktok",
      aspectRatio: "9:16",
      durationTarget: 15,
      captionPreset: "hormozi-impact",
      seed: 42,
    });

    assert.ok(createResult.projectId.startsWith("proj_"));
    assert.ok(createResult.revisionId && createResult.revisionId.startsWith("rev_"));
    assert.equal(createResult.status, "created");
    assert.equal(createResult.width, 1080);
    assert.equal(createResult.height, 1920);

    const projectId = createResult.projectId;
    const rev1 = createResult.revisionId!;

    // 2. Tool 2: apply_viral_caption_style (Genera rev_2)
    const applyCaptionResult = await handleApplyViralCaptionStyle({
      projectId,
      revisionId: rev1,
      preset: "beast-clean",
      overrides: { fontSize: 72 },
    });

    assert.equal(applyCaptionResult.projectId, projectId);
    assert.equal(applyCaptionResult.parentRevisionId, rev1);
    assert.ok(applyCaptionResult.newRevisionId.startsWith("rev_"));
    assert.notEqual(applyCaptionResult.newRevisionId, rev1);

    const rev2 = applyCaptionResult.newRevisionId;

    // 3. Tool 3: get_timeline_preview_frame en t = 2.5s
    const previewResult = await handleGetTimelinePreviewFrame({
      projectId,
      revisionId: rev2,
      time: 2.5,
    });

    assert.equal(previewResult.projectId, projectId);
    assert.equal(previewResult.revisionId, rev2);
    assert.equal(previewResult.time, 2.5);
    assert.ok(previewResult.activeLayers.length > 0);
    assert.ok(previewResult.frameHash.length === 64);

    // 4. Tool 4: export_to_after_effects_jsx
    const exportResult = await handleExportAfterEffectsJSX({
      projectId,
      revisionId: rev2,
      strict: false,
    });

    assert.equal(exportResult.projectId, projectId);
    assert.equal(exportResult.revisionId, rev2);
    assert.ok(exportResult.jsxContent && exportResult.jsxContent.includes('addComp('));
    assert.ok(exportResult.manifest.deterministicHash.length === 64);
  });
});
