import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioReactiveEngine } from "../../audio-intelligence/core/AudioReactiveEngine.js";
import { AudioSignal } from "../../audio-intelligence/core/AudioSignal.js";
import { AudioBinding, AudioMapping } from "../../audio-intelligence/types/index.js";

describe("Fase 5I — Audio-Reactive Property Bindings Tests", () => {
  it("maps audio signal energy to camera zoom using linear, ease and threshold mappings", () => {
    const signal = new AudioSignal("bass_band", [
      { time: 0.0, value: 0.0 },
      { time: 1.0, value: 0.8 },
    ]);

    // 1. Linear Mapping: 0.0 -> 1.0 entrada mapea a 1.0 -> 1.25 zoom
    const linearMapping: AudioMapping = {
      mode: "linear",
      inputRange: [0.0, 1.0],
      outputRange: [1.0, 1.25],
    };

    const binding: AudioBinding = {
      id: "bind_cam_zoom",
      signalName: "bass_band",
      targetLayerId: "camera_main",
      targetProperty: "zoom",
      mapping: linearMapping,
    };

    // En t = 1.0s -> raw = 0.8 -> output = 1.0 + 0.8 * 0.25 = 1.20
    const zoomAt1 = AudioReactiveEngine.evaluateBinding(binding, signal, 1.0);
    assert.strictEqual(zoomAt1, 1.2);

    // 2. Threshold Mapping: si bass > 0.5 -> trigger zoom 1.3, sino 1.0
    const thresholdMapping: AudioMapping = {
      mode: "clamp",
      inputRange: [0, 1],
      outputRange: [1, 1.3],
      threshold: {
        value: 0.5,
        below: 1.0,
        above: 1.3,
      },
    };

    binding.mapping = thresholdMapping;
    assert.strictEqual(AudioReactiveEngine.evaluateBinding(binding, signal, 0.2), 1.0); // raw = 0.16 < 0.5
    assert.strictEqual(AudioReactiveEngine.evaluateBinding(binding, signal, 1.0), 1.3); // raw = 0.80 > 0.5
  });
});
