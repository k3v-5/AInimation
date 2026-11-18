#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const mcpRoot = path.join(__dirname, 'stykanimate-mcp');

// 1. Importar directamente del núcleo de StykAnimate
const { Editor, createStartupDocument, buildContainerV2 } = await import(
  pathToFileURL(path.join(mcpRoot, 'src', 'core.js')).href
);
const { createFrame, createObject } = await import(
  pathToFileURL(path.join(mcpRoot, 'vendor', 'stykanimate', 'src', 'demo.mjs')).href
);
const { validateScene } = await import(
  pathToFileURL(path.join(mcpRoot, 'vendor', 'stykanimate', 'src', 'pivot', 'model.mjs')).href
);
const { exportToHtml } = await import(
  pathToFileURL(path.join(__dirname, 'export-html.js')).href
);

async function runTest() {
  console.log('⚡ [StykAnimate Core] Iniciando prueba con el motor nativo de StykAnimate...');

  const editor = new Editor({ demo: false });
  editor.load(createStartupDocument());

  editor.report.canvas_width = 960;
  editor.report.canvas_height = 540;
  editor.report.fps = 24;

  // Paleta de colores "Cyber Samurai"
  const armorDark = [24, 28, 36];      // Grafito oscuro #181C24
  const armorPlate = [45, 52, 64];     // Armadura placas #2D3440
  const neonCyan = [0, 240, 255];      // Neón Ciber / Visor / Espada #00F0FF
  const neonRed = [255, 45, 85];       // Neón rojo / Núcleo #FF2D55
  const scarfRed = [220, 20, 60];      // Bufanda roja fluido
  const bladeGlow = [180, 255, 255];   // Hoja brillante

  // Definición de figura avanzada: Cyber Samurai
  const segments = [
    // 1: Pelvis / Cintura
    { segment_id: 1, parent_id: 0, length: 25, angle_rad: -Math.PI / 2, thickness: 26, primitive_code: 0, color_rgb: armorDark, name: 'Pelvis', z_order: 10 },
    // 2: Torso bajo / Abdomen
    { segment_id: 2, parent_id: 1, length: 25, angle_rad: -Math.PI / 2, thickness: 24, primitive_code: 0, color_rgb: armorPlate, name: 'Abdomen', z_order: 11 },
    // 3: Pecho acorazado
    { segment_id: 3, parent_id: 2, length: 30, angle_rad: -Math.PI / 2, thickness: 32, primitive_code: 0, color_rgb: armorDark, name: 'Chest', z_order: 12 },
    // 4: Núcleo de energía en el pecho (Glowing Core)
    { segment_id: 4, parent_id: 3, length: 12, angle_rad: Math.PI / 2, thickness: 0, primitive_code: 3, color_rgb: neonRed, name: 'Core', z_order: 13 },
    // 5: Cuello
    { segment_id: 5, parent_id: 3, length: 12, angle_rad: -Math.PI / 2, thickness: 14, primitive_code: 0, color_rgb: armorPlate, name: 'Neck', z_order: 14 },
    // 6: Casco / Cabeza
    { segment_id: 6, parent_id: 5, length: 34, angle_rad: -Math.PI / 2, thickness: 0, primitive_code: 3, color_rgb: armorDark, name: 'Helmet', z_order: 20 },
    // 7: Visor cibernético brillante
    { segment_id: 7, parent_id: 6, length: 18, angle_rad: 0, thickness: 7, primitive_code: 0, color_rgb: neonCyan, name: 'Visor', z_order: 21 },
    // 8: Cuerno / Cresta del casco
    { segment_id: 8, parent_id: 6, length: 22, angle_rad: -Math.PI * 0.75, thickness: 6, primitive_code: 0, color_rgb: neonCyan, name: 'HelmetHorn', z_order: 19 },

    // BUFANDA FLOTANTE (3 articulaciones)
    // 9: Bufanda base
    { segment_id: 9, parent_id: 5, length: 24, angle_rad: Math.PI * 0.9, thickness: 10, primitive_code: 0, color_rgb: scarfRed, name: 'Scarf1', z_order: 6 },
    // 10: Bufanda medio
    { segment_id: 10, parent_id: 9, length: 26, angle_rad: Math.PI * 0.95, thickness: 8, primitive_code: 0, color_rgb: scarfRed, name: 'Scarf2', z_order: 6 },
    // 11: Bufanda punta
    { segment_id: 11, parent_id: 10, length: 28, angle_rad: Math.PI * 0.85, thickness: 6, primitive_code: 0, color_rgb: scarfRed, name: 'Scarf3', z_order: 6 },

    // BRAZO TRASERO / IZQUIERDO (Hombro -> Codo -> Mano)
    // 12: Hombrera izq (armadura)
    { segment_id: 12, parent_id: 3, length: 16, angle_rad: Math.PI * 0.85, thickness: 18, primitive_code: 0, color_rgb: armorPlate, name: 'ShoulderL', z_order: 8 },
    // 13: Brazo sup izq
    { segment_id: 13, parent_id: 12, length: 34, angle_rad: Math.PI * 0.6, thickness: 12, primitive_code: 0, color_rgb: armorDark, name: 'ArmL_Up', z_order: 7 },
    // 14: Antebrazo izq
    { segment_id: 14, parent_id: 13, length: 32, angle_rad: Math.PI * 0.3, thickness: 11, primitive_code: 0, color_rgb: armorPlate, name: 'ArmL_Low', z_order: 7 },
    // 15: Mano izq
    { segment_id: 15, parent_id: 14, length: 12, angle_rad: 0, thickness: 0, primitive_code: 3, color_rgb: armorDark, name: 'HandL', z_order: 8 },

    // PIERNA TRASERA / IZQUIERDA
    // 16: Muslo acorazado izq
    { segment_id: 16, parent_id: 1, length: 44, angle_rad: Math.PI * 0.65, thickness: 18, primitive_code: 0, color_rgb: armorPlate, name: 'ThighL', z_order: 4 },
    // 17: Greba / Pantorrilla izq
    { segment_id: 17, parent_id: 16, length: 42, angle_rad: Math.PI * 0.35, thickness: 15, primitive_code: 0, color_rgb: armorDark, name: 'CalfL', z_order: 4 },
    // 18: Bota izq
    { segment_id: 18, parent_id: 17, length: 22, angle_rad: 0, thickness: 12, primitive_code: 0, color_rgb: armorPlate, name: 'BootL', z_order: 5 },

    // PIERNA DELANTERA / DERECHA
    // 19: Muslo acorazado der
    { segment_id: 19, parent_id: 1, length: 44, angle_rad: Math.PI * 0.35, thickness: 18, primitive_code: 0, color_rgb: armorPlate, name: 'ThighR', z_order: 14 },
    // 20: Greba / Pantorrilla der
    { segment_id: 20, parent_id: 19, length: 42, angle_rad: Math.PI * 0.65, thickness: 15, primitive_code: 0, color_rgb: armorDark, name: 'CalfR', z_order: 14 },
    // 21: Bota der
    { segment_id: 21, parent_id: 20, length: 22, angle_rad: 0, thickness: 12, primitive_code: 0, color_rgb: armorPlate, name: 'BootR', z_order: 15 },

    // BRAZO DELANTERO / DERECHO (Con Espada Katana Neón)
    // 22: Hombrera der
    { segment_id: 22, parent_id: 3, length: 16, angle_rad: Math.PI * 0.15, thickness: 18, primitive_code: 0, color_rgb: armorPlate, name: 'ShoulderR', z_order: 22 },
    // 23: Brazo sup der
    { segment_id: 23, parent_id: 22, length: 34, angle_rad: Math.PI * 0.4, thickness: 12, primitive_code: 0, color_rgb: armorDark, name: 'ArmR_Up', z_order: 23 },
    // 24: Antebrazo der
    { segment_id: 24, parent_id: 23, length: 32, angle_rad: Math.PI * 0.7, thickness: 11, primitive_code: 0, color_rgb: armorPlate, name: 'ArmR_Low', z_order: 23 },
    // 25: Mano der
    { segment_id: 25, parent_id: 24, length: 12, angle_rad: 0, thickness: 0, primitive_code: 3, color_rgb: armorDark, name: 'HandR', z_order: 24 },
    // 26: Empuñadura Katana
    { segment_id: 26, parent_id: 25, length: 18, angle_rad: -Math.PI * 0.4, thickness: 6, primitive_code: 0, color_rgb: armorDark, name: 'Hilt', z_order: 25 },
    // 27: Hoja Katana Neón (Luz Cian)
    { segment_id: 27, parent_id: 26, length: 85, angle_rad: -Math.PI * 0.4, thickness: 7, primitive_code: 0, color_rgb: neonCyan, name: 'BladeNeon', z_order: 26 },
    // 28: Filo brillante de la hoja
    { segment_id: 28, parent_id: 26, length: 82, angle_rad: -Math.PI * 0.4, thickness: 3, primitive_code: 0, color_rgb: bladeGlow, name: 'BladeCore', z_order: 27 },
  ];

  const formattedSegments = segments.map(s => ({
    bend_rad: 0,
    aux_code: 0,
    flags: s.primitive_code,
    segment_type: s.primitive_code === 3 ? 'circle' : 'line',
    segment_kind: s.primitive_code === 3 ? 'circleFill' : 'line',
    transparency: 0,
    visible: true,
    is_static: false,
    ...s,
  }));

  const samuraiFigure = {
    figure_type_id: 301,
    name: 'Cyber_Samurai',
    segment_count: formattedSegments.length,
    segments: formattedSegments,
    polyfills: [
      // Placa de armadura en el pecho (triángulo de protección)
      {
        polyfill_id: 1,
        segment_ids: [1, 2, 3],
        color_rgb: armorPlate,
        z_order: 11,
      }
    ],
    image_assets: [],
    text_assets: [],
  };

  // Suelo estilo laboratorio / cyberpunk
  const floorFigure = {
    figure_type_id: 302,
    name: 'Cyber_Floor',
    segment_count: 2,
    segments: [
      {
        segment_id: 1,
        parent_id: 0,
        length: 920,
        angle_rad: 0,
        thickness: 16,
        primitive_code: 0,
        aux_code: 0,
        flags: 0,
        segment_type: 'line',
        segment_kind: 'line',
        color_rgb: [18, 22, 30],
        transparency: 0,
        visible: true,
        z_order: 1,
        name: 'FloorBase',
      },
      {
        segment_id: 2,
        parent_id: 0,
        length: 920,
        angle_rad: 0,
        thickness: 2,
        primitive_code: 0,
        aux_code: 0,
        flags: 0,
        segment_type: 'line',
        segment_kind: 'line',
        color_rgb: neonCyan,
        transparency: 0,
        visible: true,
        z_order: 2,
        name: 'FloorNeonLine',
      }
    ],
    polyfills: [],
    image_assets: [],
    text_assets: [],
  };

  editor.report.figure_types = [samuraiFigure, floorFigure];

  const samuraiSlot = {
    object_slot: 0,
    unique_id: 1,
    figure_type_id: 301,
    root_x: 240,
    root_y: 350,
    scale: 1.15,
    color_override_raw: 0,
    color_override_rgb: [0, 0, 0],
    color_override_mix: 0,
    transparency: 0,
    opacity: 1,
    field28: 0,
    angles: formattedSegments.map(s => s.angle_rad),
    len_flag: 0,
    lengths: [],
    bend_flag: 0,
    bends: [],
    join: null,
  };

  const floorSlot = {
    object_slot: 1,
    unique_id: 2,
    figure_type_id: 302,
    root_x: 20,
    root_y: 470,
    scale: 1,
    color_override_raw: 0,
    color_override_rgb: [0, 0, 0],
    color_override_mix: 0,
    transparency: 0,
    opacity: 1,
    field28: 0,
    angles: [0, 0],
    len_flag: 0,
    lengths: [],
    bend_flag: 0,
    bends: [],
    join: null,
  };

  const baseAngles = [...samuraiSlot.angles];
  function pose(overrides) {
    const res = [...baseAngles];
    for (const [id, val] of Object.entries(overrides)) {
      res[Number(id) - 1] = val;
    }
    return res;
  }

  console.log('⚔️ Generando coreografía: Flash-Step & Katana Dimensional Slash...');

  // 1. Pose de Espera (Guardia con Katana baja)
  const kf0 = {
    duration: 14,
    x: 240, y: 350,
    angles: pose({
      9: Math.PI * 0.9, 10: Math.PI * 0.95, 11: Math.PI * 0.85,
      23: Math.PI * 0.35, 24: Math.PI * 0.75, 26: -Math.PI * 0.35, 27: -Math.PI * 0.35, 28: -Math.PI * 0.35
    })
  };

  // 2. Carga / Tensión (Se agacha profundamente, la hoja se carga de energía)
  const kf1 = {
    duration: 10,
    x: 220, y: 390,
    angles: pose({
      16: Math.PI * 0.85, 17: Math.PI * 0.2,
      19: Math.PI * 0.25, 20: Math.PI * 0.85,
      9: Math.PI * 1.1, 10: Math.PI * 1.15,
      23: Math.PI * 0.9, 24: Math.PI * 0.9, // Brazo atrás listo
      26: Math.PI * 0.8, 27: Math.PI * 0.8, 28: Math.PI * 0.8
    })
  };

  // 3. Flash-Step (Aceleración ultrasónica cruzando la pantalla)
  const kf2 = {
    duration: 8,
    x: 520, y: 310,
    angles: pose({
      1: -Math.PI * 0.35, 2: -Math.PI * 0.35, 3: -Math.PI * 0.35, // Inclinado hacia delante
      16: Math.PI * 0.45, 17: Math.PI * 0.5,
      19: Math.PI * 0.55, 20: Math.PI * 0.45,
      9: Math.PI * 0.95, 10: Math.PI * 0.98, 11: Math.PI * 0.99, // Bufanda estirada por la velocidad
      23: -Math.PI * 0.2, 24: -Math.PI * 0.1, // Espada desenvainándose en el aire
      26: -Math.PI * 0.1, 27: -Math.PI * 0.1, 28: -Math.PI * 0.1
    })
  };

  // 4. Dimensional Slash (Corte horizontal completo con Katana extendida)
  const kf3 = {
    duration: 14,
    x: 720, y: 340,
    angles: pose({
      16: Math.PI * 0.75, 17: Math.PI * 0.25,
      19: Math.PI * 0.2, 20: Math.PI * 0.75,
      9: Math.PI * 0.6, 10: Math.PI * 0.4, 11: Math.PI * 0.2, // Bufanda en arco
      13: Math.PI * 0.9, 14: Math.PI * 0.8, // Brazo izquierdo atrás balanceando
      23: -Math.PI * 0.05, 24: -Math.PI * 0.05, // Brazo derecho totalmente extendido cortando
      26: 0, 27: 0, 28: 0 // Hoja horizontal hacia el frente
    })
  };

  // 5. Aterrizaje y envaine (Giro y caída con pose elegante)
  const kf4 = {
    duration: 12,
    x: 750, y: 385,
    angles: pose({
      16: Math.PI * 0.85, 17: Math.PI * 0.15,
      19: Math.PI * 0.15, 20: Math.PI * 0.85,
      9: Math.PI * 0.75, 10: Math.PI * 0.8,
      23: Math.PI * 0.4, 24: Math.PI * 0.85,
      26: Math.PI * 0.75, 27: Math.PI * 0.75, 28: Math.PI * 0.75 // Espada bajando
    })
  };

  // 6. Pose final triunfal (De pie con la Katana envainada en guardia)
  const kf5 = {
    duration: 18,
    x: 740, y: 350,
    angles: [...baseAngles]
  };

  const keyframeDefs = [kf0, kf1, kf2, kf3, kf4, kf5];

  editor.report.keyframes = keyframeDefs.map(k => {
    const character = {
      ...samuraiSlot,
      root_x: k.x,
      root_y: k.y,
      angles: k.angles,
    };
    return createFrame([character, floorSlot], k.duration);
  });

  editor.report.total_output_frames = keyframeDefs.reduce((acc, k) => acc + k.duration, 0);
  delete editor.report._styk?.layerSheet;

  // 3. Ejecutar la validación oficial del modelo de StykAnimate
  console.log('🛡️ Validando integridad con el validador oficial de StykAnimate (validateScene)...');
  try {
    validateScene(editor.report);
    console.log('✅ Validación oficial de StykAnimate: ¡Documento 100% válido y sin errores!');
  } catch (err) {
    console.error('❌ Error de validación en StykAnimate:', err.message);
    throw err;
  }

  // 4. Serializar en contenedor binario nativo V2 de StykAnimate (.styk)
  const stykPath = path.join(__dirname, 'cyber_samurai.styk');
  const serialized = editor.serialize();
  const binaryContainer = await buildContainerV2(serialized, 'styk');
  await writeFile(stykPath, binaryContainer);
  console.log(`📦 Contenedor binario guardado: ${stykPath} (${binaryContainer.length} bytes)`);

  // 5. Exportar al reproductor HTML interactivo
  const htmlPath = path.join(__dirname, 'cyber_samurai.html');
  await exportToHtml(stykPath, htmlPath);
  console.log(`🎬 Reproductor interactivo generado en: ${htmlPath}`);

  return { stykPath, htmlPath, totalFrames: editor.report.total_output_frames };
}

runTest().catch(console.error);
