import { Composition, Layer, Vector2, serializeComposition, deserializeComposition } from "../core/index.js";

/**
 * Ejemplo ejecutable del Core Temporal del Motion Engine (Fase 1).
 */
function main() {
  console.log("=== Motion Engine Core (Fase 1) ===");

  // 1. Crear Composición
  const composition = new Composition({
    name: "Intro Motion",
    width: 1080,
    height: 1920,
    fps: 30,
    duration: 5.0,
  });

  // 2. Crear Capa de Título
  const titleLayer = new Layer({
    id: "title_layer",
    name: "Main Headline",
    startTime: 0.0,
    endTime: 4.0,
  });

  // 3. Configurar animación de Opacidad y Escala
  titleLayer.property<number>("opacity").addKeyframe(0.0, 0.0, "easeOut");
  titleLayer.property<number>("opacity").addKeyframe(0.5, 1.0);

  titleLayer.property<Vector2>("scale").addKeyframe(0.0, { x: 0.5, y: 0.5 }, "easeOut");
  titleLayer.property<Vector2>("scale").addKeyframe(0.5, { x: 1.0, y: 1.0 });

  titleLayer.property<Vector2>("position").addKeyframe(0.0, { x: 540, y: 1200 }, "easeInOut");
  titleLayer.property<Vector2>("position").addKeyframe(1.0, { x: 540, y: 960 });

  composition.addLayer(titleLayer);

  // 4. Evaluar en t = 0.25s
  console.log("\n[Evaluando a t = 0.25s]:");
  const state025 = composition.evaluate(0.25);
  console.log(JSON.stringify(state025, null, 2));

  // 5. Evaluar en t = 1.0s
  console.log("\n[Evaluando a t = 1.0s]:");
  const state100 = composition.evaluate(1.0);
  console.log(JSON.stringify(state100, null, 2));

  // 6. Serializar a JSON
  console.log("\n[Serializando a JSON Schema v0.1.0]:");
  const json = serializeComposition(composition);
  console.log(JSON.stringify(json, null, 2));

  // 7. Deserializar y comprobar evaluación idéntica
  const reloaded = deserializeComposition(json);
  const reloadedState = reloaded.evaluate(0.25);
  console.log("\n[Comprobación de Determinismo]:", JSON.stringify(state025) === JSON.stringify(reloadedState) ? "PASS (100% IDÉNTICO)" : "FAIL");
}

main();
