import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { describe, it } from "node:test";
import { AutoClipPipelineOrchestrator } from "../../automation/pipeline/AutoClipPipelineOrchestrator.js";

describe("Automation Pipeline Suite — AutoClipPipelineOrchestrator 1-Click", () => {
  it("executes the complete end-to-end auto-clip pipeline generating JSX scripts and manifests", () => {
    const testOutDir = path.resolve("./dist/test_autoclip_pipeline");

    const result = AutoClipPipelineOrchestrator.run({
      inputVideoPath: "E:/Respaldo/TestVideo.mp4",
      transcriptText: "¿CUÁL ES EL SECRETO DETRÁS DEL ÉXITO DE ESTE GRAN PROYECTO? NADIE TE CUENTA LA VERDAD SOBRE EL ESFUERZO Y LA DEDICACIÓN QUE SE NECESITAN CADA DÍA PARA TRIUNFAR EN ESTE MUNDO DIGITAL.",
      totalDurationSec: 90.0,
      stylePreset: "hormozi_cashflow_captions",
      outputDir: testOutDir,
      topK: 2,
      projectName: "Test_AutoShorts",
      includeSoundBank: true,
    });

    assert.equal(result.totalClipsGenerated, 2);
    assert.equal(result.clips.length, 2);

    for (const clip of result.clips) {
      assert.ok(fs.existsSync(clip.jsxScriptPath), `JSX script must exist: ${clip.jsxScriptPath}`);
      assert.ok(fs.existsSync(clip.manifestPath), `Manifest must exist: ${clip.manifestPath}`);
      const jsxContent = fs.readFileSync(clip.jsxScriptPath, "utf-8");
      assert.ok(jsxContent.includes("1080, 1920"), "Must be 9:16 vertical resolution");
      assert.ok(jsxContent.includes("ParagraphJustification.CENTER_JUSTIFY"));
    }

    // Cleanup
    fs.rmSync(testOutDir, { recursive: true, force: true });
  });
});
