import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { CameraMatrix } from "../../camera/core/CameraMatrix.js";
import { CameraShakeModifier, PunchInModifier } from "../../camera/modifiers/CameraModifiers.js";
import { CameraPresetRegistry } from "../../camera/presets/CameraPresets.js";
import { Camera } from "../../camera/types/index.js";

describe("Fase 5H — Camera Projections, Modifiers & Presets Tests", () => {
  it("projects world point through 2D camera view matrix with zoom and pan", () => {
    const camera: Camera = {
      position: { x: 100, y: 50, z: 0 },
      rotation: { x: 0, y: 0, z: 0 },
      zoom: 2.0, // Zoom x2
    };

    const screenW = 1000;
    const screenH = 1000;

    // Punto en el mundo coincidente con el centro de la cámara (100 + 500, 50 + 500) = (600, 550)
    // Debe proyectarse exactamente al centro de la pantalla (500, 500)
    const projectedCenter = CameraMatrix.projectPoint({ x: 600, y: 550 }, camera, screenW, screenH);
    assert.strictEqual(Math.round(projectedCenter.x), 500);
    assert.strictEqual(Math.round(projectedCenter.y), 500);
  });

  it("applies deterministic camera shake with identical results under same seed", () => {
    const initialCam: Camera = {
      position: { x: 0, y: 0, z: 0 },
      rotation: { x: 0, y: 0, z: 0 },
      zoom: 1.0,
    };

    const shake1 = new CameraShakeModifier(10, 4, 12345);
    const shake2 = new CameraShakeModifier(10, 4, 12345);

    const evaluated1 = shake1.evaluate(0.5, initialCam);
    const evaluated2 = shake2.evaluate(0.5, initialCam);

    assert.deepStrictEqual(evaluated1, evaluated2);
    assert.ok(evaluated1.position.x !== 0 || evaluated1.position.y !== 0);
  });

  it("registers and retrieves camera presets (handheld-shake, punch-in)", () => {
    assert.strictEqual(CameraPresetRegistry.has("handheld-shake"), true);
    assert.strictEqual(CameraPresetRegistry.has("punch-in"), true);

    const punchIn = CameraPresetRegistry.get("punch-in");
    assert.ok(punchIn.modifier instanceof PunchInModifier);
  });
});
