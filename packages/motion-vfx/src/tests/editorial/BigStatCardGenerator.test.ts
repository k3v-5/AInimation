import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  BigStatSpec,
  generateBigStatCard,
  TIME_EDITORIAL_STYLE,
  DEFAULT_SAFE_ZONE,
} from "../../editorial/data-visualization/index.js";

describe("REQ-025 — BigStatCardGenerator", () => {
  const spec: BigStatSpec = {
    id: "stat_inflation_peak",
    type: "BIG_STAT_CARD",
    value: 9.1,
    label: "Peak US Inflation Rate",
    prefix: "",
    suffix: "%",
    secondaryText: "Highest level recorded in four decades (June 2022)",
    accentLine: true,
    animateValue: true,
    decimals: 1,
    format: "PERCENTAGE",
    width: 1920,
    height: 1080,
    durationSeconds: 4.5,
    startTimeSeconds: 0.2,
    safeZone: DEFAULT_SAFE_ZONE,
    style: TIME_EDITORIAL_STYLE,
    animation: {
      entranceDurationSeconds: 1.0,
      exitDurationSeconds: 0.5,
      easing: "EASE_OUT",
    },
  };

  it("generates editorial Big Stat Card without requiring a tabular dataset", () => {
    const result = generateBigStatCard(spec);

    assert.equal(result.success, true);
    assert.ok(result.ir);
    assert.equal(result.ir.type, "BIG_STAT_CARD");
    assert.equal(result.ir.width, 1920);
    assert.equal(result.ir.height, 1080);

    // Verificar capas requeridas
    const valLayer = result.ir.layers.find((l) => l.name === "DV::STAT::VALUE");
    const labelLayer = result.ir.layers.find((l) => l.name === "DV::STAT::LABEL");
    const secLayer = result.ir.layers.find((l) => l.name === "DV::STAT::SECONDARY");
    const lineLayer = result.ir.layers.find((l) => l.name === "DV::STAT::ACCENT_LINE");

    assert.ok(valLayer);
    assert.ok(labelLayer);
    assert.ok(secLayer);
    assert.ok(lineLayer);

    // Formato determinista del valor
    assert.equal(valLayer.text?.content, "9.1%");
    assert.equal(labelLayer.text?.content, "PEAK US INFLATION RATE");
    assert.equal(secLayer.text?.content, "Highest level recorded in four decades (June 2022)");

    // Animación de contador
    const counterAnim = valLayer.animation?.properties.find((p) => p.property === "counterValue");
    assert.ok(counterAnim);
    assert.equal(counterAnim.keyframes[1].value, 9.1);

    // Checksum determinista
    assert.ok(result.checksumSha256);
    assert.equal(result.checksumSha256.length, 64);
  });

  it("formats currency values deterministically with thousand separators", () => {
    const currencySpec: BigStatSpec = {
      ...spec,
      id: "stat_national_debt",
      value: 34500000,
      format: "CURRENCY",
      decimals: 0,
      suffix: " USD",
    };

    const result = generateBigStatCard(currencySpec);
    assert.equal(result.success, true);
    assert.ok(result.ir);

    const valLayer = result.ir.layers.find((l) => l.name === "DV::STAT::VALUE");
    assert.equal(valLayer?.text?.content, "$34,500,000 USD");
  });
});
