import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AEJSXParser } from "../../exporters/ae/importer/AEJSXParser.js";
import { AETemplateImporter } from "../../exporters/ae/importer/AETemplateImporter.js";
import { TextElement } from "../../elements/TextElement.js";

describe("Fase 26 — Capa 3: After Effects JSX Parser & Template Importer Tests", () => {
  const sampleJSX = `
// Generated After Effects Project
var comp = app.project.items.addComp("Promo_Template", 1920, 1080, 1.0, 15.0, 30.0);
var textLayer_1 = comp.layers.addText("SPECIAL OFFER");
textLayer_1.name = "Heading_Text";
var solidLayer_1 = comp.layers.addSolid([0, 0, 0], "Background", 1920, 1080, 1.0);
`;

  it("AEJSXParser parses composition dimensions, fps, duration and layer properties", () => {
    const parsed = AEJSXParser.parse(sampleJSX);

    assert.equal(parsed.name, "Promo_Template");
    assert.equal(parsed.width, 1920);
    assert.equal(parsed.height, 1080);
    assert.equal(parsed.fps, 30.0);
    assert.equal(parsed.duration, 15.0);
    assert.equal(parsed.textLayers.length, 1);
    assert.equal(parsed.textLayers[0].text, "SPECIAL OFFER");
    assert.equal(parsed.textLayers[0].name, "Heading_Text");
    assert.equal(parsed.solidLayers.length, 1);
    assert.equal(parsed.solidLayers[0].name, "Background");
  });

  it("AETemplateImporter reconstructs a canonical Composition with TextElements", () => {
    const result = AETemplateImporter.importTemplate(sampleJSX, "comp_imported_promo");

    assert.equal(result.composition.id, "comp_imported_promo");
    assert.equal(result.composition.name, "Promo_Template");
    assert.equal(result.composition.width, 1920);
    assert.equal(result.composition.height, 1080);
    assert.equal(result.composition.duration, 15.0);
    assert.equal(result.composition.fps, 30.0);

    const elements = result.composition.getElements();
    assert.equal(elements.length, 1);
    assert.ok(elements[0] instanceof TextElement);
    const textEl = elements[0] as TextElement;
    assert.equal(textEl.text.getValue(), "SPECIAL OFFER");
    assert.equal(typeof result.canonicalHash, "string");
  });
});
