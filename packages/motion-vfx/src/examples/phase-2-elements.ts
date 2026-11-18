import { Composition } from "../core/composition.js";
import { resetIdGenerators } from "../core/id.js";
import {
  AudioElement,
  GroupElement,
  ImageElement,
  ShapeElement,
  TextElement,
  VideoElement,
} from "../elements/index.js";
import { deserializeComposition } from "../serialization/deserializer.js";
import { serializeComposition } from "../serialization/serializer.js";

resetIdGenerators();

console.log("=== Motion Engine — Fase 2: Element Model ===");

// 1. Crear Composición
const comp = new Composition({
  id: "hero_scene",
  name: "Hero Motion Graphics Scene",
  width: 1080,
  height: 1920,
  fps: 30,
  duration: 10.0,
});

// 2. Registrar Assets
comp.assets.add({
  id: "asset_logo",
  type: "image",
  source: { path: "assets/logo.png" },
  metadata: { width: 512, height: 512 },
});

comp.assets.add({
  id: "asset_bg_video",
  type: "video",
  source: { path: "assets/particles_bg.mp4" },
  metadata: { width: 1080, height: 1920, duration: 15.0, fps: 30 },
});

comp.assets.add({
  id: "asset_soundtrack",
  type: "audio",
  source: { path: "assets/intro_music.mp3" },
  metadata: { duration: 60.0, sampleRate: 48000 },
});

// 3. Crear Fondo (ShapeElement)
const bg = new ShapeElement({
  id: "bg_rect",
  name: "Background Solid",
  shapeType: "rectangle",
  shapeData: { width: 1080, height: 1920 },
  style: { fill: { r: 0.05, g: 0.08, b: 0.15, a: 1 } },
  startTime: 0,
  duration: 10,
});
comp.addElement(bg);

// 4. Crear Video de Fondo (VideoElement)
const bgVideo = new VideoElement({
  id: "bg_particle_video",
  name: "Particles Loop",
  assetId: "asset_bg_video",
  startTime: 0,
  duration: 10,
});
bgVideo.transform.opacity.setValue(0.6);
comp.addElement(bgVideo);

// 5. Crear Grupo de Título Principal (GroupElement)
const headerGroup = new GroupElement({
  id: "header_group",
  name: "Header UI Group",
  startTime: 0,
  duration: 8,
});
headerGroup.transform.position.setValue({ x: 540, y: 960 });

// Animación de entrada del grupo: escala y opacidad
headerGroup.transform.scale.addKeyframe(0, { x: 0.8, y: 0.8 }, "easeOut");
headerGroup.transform.scale.addKeyframe(1.0, { x: 1.0, y: 1.0 });

// Logo dentro del grupo
const logo = new ImageElement({
  id: "brand_logo",
  name: "Brand Logo",
  assetId: "asset_logo",
});
logo.transform.position.setValue({ x: 0, y: -120 });
logo.transform.scale.setValue({ x: 0.6, y: 0.6 });
headerGroup.addChild(logo);

// Texto de Título dentro del grupo
const title = new TextElement({
  id: "main_headline",
  name: "Headline Text",
  text: "MOTION GRAPHICS ENGINE",
  style: {
    fontFamily: "Inter",
    fontSize: 56,
    fontWeight: 800,
    color: { r: 1, g: 1, b: 1, a: 1 },
    textAlign: "center",
  },
});
title.transform.position.setValue({ x: 0, y: 60 });
title.transform.opacity.addKeyframe(0.2, 0, "easeOut");
title.transform.opacity.addKeyframe(0.8, 1.0);
headerGroup.addChild(title);

comp.addElement(headerGroup);

// 6. Música de Fondo (AudioElement)
const music = new AudioElement({
  id: "soundtrack",
  name: "Soundtrack Track",
  assetId: "asset_soundtrack",
  startTime: 0,
  duration: 10,
});
music.volume.addKeyframe(0, 0, "linear");
music.volume.addKeyframe(2.0, 1.0);
comp.addElement(music);

// 7. Evaluar Estado en t = 0.5s
console.log("\n[Evaluando Composición a t = 0.5s]:");
const snapshot05 = comp.evaluate(0.5);
console.log(JSON.stringify(snapshot05, null, 2));

// 8. Serializar a JSON Schema v0.2.0
console.log("\n[Serializando a JSON Schema v0.2.0]:");
const projectJson = serializeComposition(comp);
console.log(JSON.stringify(projectJson, null, 2));

// 9. Deserializar y Comprobar Integridad
const deserializedComp = deserializeComposition(projectJson);
const roundtripSnapshot = deserializedComp.evaluate(0.5);

console.log("\n=== Snapshot Roundtrip Match ===");
console.log("Coincidencia exacta de evaluación:", JSON.stringify(snapshot05) === JSON.stringify(roundtripSnapshot));
