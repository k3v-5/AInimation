import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { OmniChannelMultiExporter } from "../../exporters/omni/OmniChannelMultiExporter.js";

describe("Exporters — OmniChannelMultiExporter Tests", () => {
  it("generates complete multi-format manifest for 9:16, 16:9 and 1:1", () => {
    const manifest = OmniChannelMultiExporter.generateManifest("Guadalajara_Edit", 220.0, [
      "9:16",
      "16:9",
      "1:1",
    ]);

    assert.equal(manifest.projectName, "Guadalajara_Edit");
    assert.equal(manifest.duration, 220.0);
    assert.equal(manifest.formats.length, 3);

    // 9:16 vertical
    assert.equal(manifest.formats[0].width, 1080);
    assert.equal(manifest.formats[0].height, 1920);

    // 16:9 widescreen
    assert.equal(manifest.formats[1].width, 1920);
    assert.equal(manifest.formats[1].height, 1080);

    // 1:1 square
    assert.equal(manifest.formats[2].width, 1080);
    assert.equal(manifest.formats[2].height, 1080);
  });

  it("generates well-formed ExtendScript multi-composition creation snippet", () => {
    const manifest = OmniChannelMultiExporter.generateManifest("Guadalajara_Edit", 60.0);
    const snippet = OmniChannelMultiExporter.generateOmniExportScript("project", manifest);

    assert.ok(snippet.includes('project.items.addComp("Guadalajara_Edit_9x16", 1080, 1920'));
    assert.ok(snippet.includes('project.items.addComp("Guadalajara_Edit_16x9", 1920, 1080'));
    assert.ok(snippet.includes('project.items.addComp("Guadalajara_Edit_1x1", 1080, 1080'));
  });
});
