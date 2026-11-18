#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const mcpRoot = path.join(__dirname, 'stykanimate-mcp');

const { Editor, createStartupDocument, buildContainerV2 } = await import(
  pathToFileURL(path.join(mcpRoot, 'src', 'core.js')).href
);
const { createFrame, createObject } = await import(
  pathToFileURL(path.join(mcpRoot, 'vendor', 'stykanimate', 'src', 'demo.mjs')).href
);
const { exportToHtml } = await import(pathToFileURL(path.join(__dirname, 'export-html.js')).href);

export async function createMonkeyAnimation() {
  console.log('🐒 Diseñando personaje avanzado: "Mono Animado" (Cartoon Monkey)...');

  const editor = new Editor({ demo: false });
  editor.load(createStartupDocument());

  // Configurar lienzo y FPS
  editor.report.canvas_width = 960;
  editor.report.canvas_height = 540;
  editor.report.fps = 24;

  // Reemplazamos la figura básica 'Blue' por nuestro "Mono" avanzado con volumen y rasgos faciales
  const furDark = [109, 76, 65];      // Marrón pelaje #6D4C41
  const furLight = [215, 204, 200];  // Beige hocico/orejas #D7CCC8
  const skinOrange = [255, 112, 67]; // Camiseta / Pecho #FF7043
  const eyeWhite = [255, 255, 255];  // Blanco ojos
  const eyeBlack = [33, 33, 33];     // Pupilas
  const pantsBlue = [33, 150, 243];  // Pantalones #2196F3
  const earPink = [244, 143, 177];   // Oreja interior #F48FB1

  // Definición del esqueleto avanzado del Mono
  // parent_id: 0 es Root (Cadera)
  const segments = [
    // 1: Columna baja / Pelvis
    { segment_id: 1, parent_id: 0, length: 30, angle_rad: -Math.PI / 2, thickness: 28, primitive_code: 0, color_rgb: pantsBlue, name: 'Pelvis', z_order: 10 },
    // 2: Torso / Pecho (Camiseta)
    { segment_id: 2, parent_id: 1, length: 45, angle_rad: -Math.PI / 2, thickness: 34, primitive_code: 0, color_rgb: skinOrange, name: 'Torso', z_order: 11 },
    // 3: Cuello
    { segment_id: 3, parent_id: 2, length: 15, angle_rad: -Math.PI / 2, thickness: 16, primitive_code: 0, color_rgb: furDark, name: 'Neck', z_order: 12 },
    // 4: Cabeza (Círculo relleno marrón grande)
    { segment_id: 4, parent_id: 3, length: 48, angle_rad: -Math.PI / 2, thickness: 0, primitive_code: 3, color_rgb: furDark, name: 'Head', z_order: 20 },
    // 5: Hocico / Cara (Círculo relleno beige frontal)
    { segment_id: 5, parent_id: 4, length: 32, angle_rad: Math.PI / 2, thickness: 0, primitive_code: 3, color_rgb: furLight, name: 'Muzzle', z_order: 21 },
    // 6: Ojo Izquierdo (Blanco)
    { segment_id: 6, parent_id: 4, length: 14, angle_rad: -Math.PI * 0.75, thickness: 0, primitive_code: 3, color_rgb: eyeWhite, name: 'EyeL_White', z_order: 22 },
    // 7: Pupila Izquierda
    { segment_id: 7, parent_id: 6, length: 6, angle_rad: 0, thickness: 0, primitive_code: 3, color_rgb: eyeBlack, name: 'EyeL_Pupil', z_order: 23 },
    // 8: Ojo Derecho (Blanco)
    { segment_id: 8, parent_id: 4, length: 14, angle_rad: -Math.PI * 0.25, thickness: 0, primitive_code: 3, color_rgb: eyeWhite, name: 'EyeR_White', z_order: 22 },
    // 9: Pupila Derecha
    { segment_id: 9, parent_id: 8, length: 6, angle_rad: 0, thickness: 0, primitive_code: 3, color_rgb: eyeBlack, name: 'EyeR_Pupil', z_order: 23 },
    // 10: Oreja Izquierda exterior
    { segment_id: 10, parent_id: 4, length: 22, angle_rad: -Math.PI * 0.95, thickness: 0, primitive_code: 3, color_rgb: furDark, name: 'EarL_Outer', z_order: 15 },
    // 11: Oreja Izquierda interior (Rosa)
    { segment_id: 11, parent_id: 10, length: 12, angle_rad: 0, thickness: 0, primitive_code: 3, color_rgb: earPink, name: 'EarL_Inner', z_order: 16 },
    // 12: Oreja Derecha exterior
    { segment_id: 12, parent_id: 4, length: 22, angle_rad: -Math.PI * 0.05, thickness: 0, primitive_code: 3, color_rgb: furDark, name: 'EarR_Outer', z_order: 15 },
    // 13: Oreja Derecha interior (Rosa)
    { segment_id: 13, parent_id: 12, length: 12, angle_rad: 0, thickness: 0, primitive_code: 3, color_rgb: earPink, name: 'EarR_Inner', z_order: 16 },

    // COLA DE MONO ARTICULADA (4 secciones curvadas)
    // 14: Cola base
    { segment_id: 14, parent_id: 0, length: 28, angle_rad: Math.PI * 0.8, thickness: 12, primitive_code: 0, color_rgb: furDark, name: 'Tail1', z_order: 5 },
    // 15: Cola media 1
    { segment_id: 15, parent_id: 14, length: 28, angle_rad: Math.PI * 0.9, thickness: 11, primitive_code: 0, color_rgb: furDark, name: 'Tail2', z_order: 5 },
    // 16: Cola media 2
    { segment_id: 16, parent_id: 15, length: 26, angle_rad: -Math.PI * 0.8, thickness: 10, primitive_code: 0, color_rgb: furDark, name: 'Tail3', z_order: 5 },
    // 17: Cola punta curva
    { segment_id: 17, parent_id: 16, length: 22, angle_rad: -Math.PI * 0.4, thickness: 9, primitive_code: 0, color_rgb: furDark, name: 'TailTip', z_order: 5 },

    // BRAZO IZQUIERDO (Hombro -> Codo -> Mano)
    // 18: Brazo sup izq
    { segment_id: 18, parent_id: 2, length: 42, angle_rad: Math.PI * 0.7, thickness: 15, primitive_code: 0, color_rgb: furDark, name: 'ArmL_Up', z_order: 18 },
    // 19: Antebrazo izq
    { segment_id: 19, parent_id: 18, length: 38, angle_rad: Math.PI * 0.4, thickness: 13, primitive_code: 0, color_rgb: furDark, name: 'ArmL_Low', z_order: 18 },
    // 20: Mano izq (Círculo relleno beige)
    { segment_id: 20, parent_id: 19, length: 16, angle_rad: Math.PI * 0.2, thickness: 0, primitive_code: 3, color_rgb: furLight, name: 'HandL', z_order: 19 },

    // BRAZO DERECHO (Hombro -> Codo -> Mano)
    // 21: Brazo sup der
    { segment_id: 21, parent_id: 2, length: 42, angle_rad: Math.PI * 0.3, thickness: 15, primitive_code: 0, color_rgb: furDark, name: 'ArmR_Up', z_order: 25 },
    // 22: Antebrazo der
    { segment_id: 22, parent_id: 21, length: 38, angle_rad: Math.PI * 0.6, thickness: 13, primitive_code: 0, color_rgb: furDark, name: 'ArmR_Low', z_order: 25 },
    // 23: Mano der (Círculo relleno beige)
    { segment_id: 23, parent_id: 22, length: 16, angle_rad: Math.PI * 0.2, thickness: 0, primitive_code: 3, color_rgb: furLight, name: 'HandR', z_order: 26 },

    // PIERNA IZQUIERDA (Cadera -> Rodilla -> Pie)
    // 24: Muslo izq (Pantalón)
    { segment_id: 24, parent_id: 0, length: 46, angle_rad: Math.PI * 0.6, thickness: 18, primitive_code: 0, color_rgb: pantsBlue, name: 'LegL_Thigh', z_order: 8 },
    // 25: Pantorrilla izq (Pelaje)
    { segment_id: 25, parent_id: 24, length: 44, angle_rad: Math.PI * 0.4, thickness: 14, primitive_code: 0, color_rgb: furDark, name: 'LegL_Calf', z_order: 8 },
    // 26: Pie izq (Zapato rojo/blanco o pata)
    { segment_id: 26, parent_id: 25, length: 24, angle_rad: 0, thickness: 12, primitive_code: 0, color_rgb: [229, 57, 53], name: 'FootL', z_order: 9 },

    // PIERNA DERECHA (Cadera -> Rodilla -> Pie)
    // 27: Muslo der (Pantalón)
    { segment_id: 27, parent_id: 0, length: 46, angle_rad: Math.PI * 0.4, thickness: 18, primitive_code: 0, color_rgb: pantsBlue, name: 'LegR_Thigh', z_order: 12 },
    // 28: Pantorrilla der (Pelaje)
    { segment_id: 28, parent_id: 27, length: 44, angle_rad: Math.PI * 0.6, thickness: 14, primitive_code: 0, color_rgb: furDark, name: 'LegR_Calf', z_order: 12 },
    // 29: Pie der
    { segment_id: 29, parent_id: 28, length: 24, angle_rad: 0, thickness: 12, primitive_code: 0, color_rgb: [229, 57, 53], name: 'FootR', z_order: 13 },
  ];

  // Añadimos propiedades estándar a cada segmento
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

  const monkeyFigure = {
    figure_type_id: 201,
    name: 'Mono_Animado',
    segment_count: formattedSegments.length,
    segments: formattedSegments,
    polyfills: [
      // Polyfill para rellenar el torso (Camiseta cerrada entre cadera, torso y hombros)
      {
        polyfill_id: 1,
        segment_ids: [0, 1, 2],
        color_rgb: skinOrange,
        z_order: 9,
      }
    ],
    image_assets: [],
    text_assets: [],
  };

  // Reemplazamos la lista de tipos con nuestro Mono y un escenario (Suelo)
  const groundFigure = {
    figure_type_id: 202,
    name: 'Suelo_Jungla',
    segment_count: 1,
    segments: [
      {
        segment_id: 1,
        parent_id: 0,
        length: 900,
        angle_rad: 0,
        thickness: 14,
        bend_rad: 0,
        primitive_code: 0,
        aux_code: 0,
        flags: 0,
        segment_type: 'line',
        segment_kind: 'line',
        color_rgb: [76, 175, 80], // Verde césped
        transparency: 0,
        visible: true,
        z_order: 1,
        name: 'Grass',
      }
    ],
    polyfills: [],
    image_assets: [],
    text_assets: [],
  };

  editor.report.figure_types = [monkeyFigure, groundFigure];

  // Instanciamos el Mono y el Suelo en el fotograma 0
  const monkeySlot = {
    object_slot: 0,
    unique_id: 1,
    figure_type_id: 201,
    root_x: 480,
    root_y: 340,
    scale: 1.1,
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

  const groundSlot = {
    object_slot: 1,
    unique_id: 2,
    figure_type_id: 202,
    root_x: 30,
    root_y: 470,
    scale: 1,
    color_override_raw: 0,
    color_override_rgb: [0, 0, 0],
    color_override_mix: 0,
    transparency: 0,
    opacity: 1,
    field28: 0,
    angles: [0],
    len_flag: 0,
    lengths: [],
    bend_flag: 0,
    bends: [],
    join: null,
  };

  // Creación de una secuencia de animación:
  // El mono saluda alegremente, flexiona rodillas, da un gran salto en el aire moviendo la cola y brazos, y aterriza triunfante!
  console.log('🤸 Creando fotogramas clave y poses de animación...');

  const initialAngles = [...monkeySlot.angles];

  // Helper para generar variaciones de pose
  function makeAngles(overrideMap) {
    const arr = [...initialAngles];
    for (const [segId, rad] of Object.entries(overrideMap)) {
      arr[Number(segId) - 1] = rad;
    }
    return arr;
  }

  // Fotograma 0: De pie saludando (Mano levantada, cola relajada)
  const frame0 = {
    duration_ticks: 12,
    objects: [
      {
        ...monkeySlot,
        root_x: 480,
        root_y: 340,
        angles: makeAngles({
          18: Math.PI * 0.9,  // Brazo izq relajado
          19: Math.PI * 0.4,
          21: -Math.PI * 0.7, // Brazo der arriba saludando
          22: -Math.PI * 0.2, // Mano arriba
          14: Math.PI * 0.7,  // Cola ondeando
          15: Math.PI * 0.85,
          16: -Math.PI * 0.6,
          17: -Math.PI * 0.2,
        })
      },
      { ...groundSlot }
    ]
  };

  // Fotograma 1: Agacharse en preparación para el salto (Crouch)
  const frame1 = {
    duration_ticks: 10,
    objects: [
      {
        ...monkeySlot,
        root_x: 480,
        root_y: 380, // Baja cadera
        angles: makeAngles({
          24: Math.PI * 0.8, // Flexiona muslos
          25: Math.PI * 0.2,
          27: Math.PI * 0.3,
          28: Math.PI * 0.8,
          18: Math.PI * 0.85, // Brazos hacia atrás tomando impulso
          19: Math.PI * 0.8,
          21: Math.PI * 0.25,
          22: Math.PI * 0.3,
          14: Math.PI * 0.9,  // Cola tensa atrás
          15: Math.PI * 0.95,
          16: -Math.PI * 0.8,
        })
      },
      { ...groundSlot }
    ]
  };

  // Fotograma 2: Despegue hacia arriba (Salto explosivo)
  const frame2 = {
    duration_ticks: 12,
    objects: [
      {
        ...monkeySlot,
        root_x: 480,
        root_y: 200, // En el aire alto
        angles: makeAngles({
          24: Math.PI * 0.55, // Piernas estiradas impulsando
          25: Math.PI * 0.5,
          27: Math.PI * 0.45,
          28: Math.PI * 0.5,
          18: -Math.PI * 0.6, // Brazos extendidos al cielo
          19: -Math.PI * 0.7,
          21: -Math.PI * 0.4,
          22: -Math.PI * 0.3,
          14: Math.PI * 0.4,  // Cola enrollada dinámica
          15: Math.PI * 0.2,
          16: -Math.PI * 0.3,
          17: -Math.PI * 0.8,
        })
      },
      { ...groundSlot }
    ]
  };

  // Fotograma 3: En el aire haciendo pose acrobática (Kung-fu / acrobacia)
  const frame3 = {
    duration_ticks: 14,
    objects: [
      {
        ...monkeySlot,
        root_x: 480,
        root_y: 170, // Pico del salto
        angles: makeAngles({
          24: Math.PI * 0.75, // Una pierna recogida, otra estirada
          25: Math.PI * 0.15,
          27: Math.PI * 0.2,
          28: Math.PI * 0.6,
          18: Math.PI * 0.1,  // Brazo extendido hacia el frente
          19: Math.PI * 0.1,
          21: -Math.PI * 0.8, // Brazo der arriba con puño
          22: -Math.PI * 0.5,
          14: Math.PI * 0.1,  // Cola ondeando hacia arriba
          15: -Math.PI * 0.3,
          16: -Math.PI * 0.8,
          17: -Math.PI * 1.1,
        })
      },
      { ...groundSlot }
    ]
  };

  // Fotograma 4: Descendiendo hacia el suelo
  const frame4 = {
    duration_ticks: 10,
    objects: [
      {
        ...monkeySlot,
        root_x: 480,
        root_y: 310, // Bajando
        angles: makeAngles({
          24: Math.PI * 0.65,
          25: Math.PI * 0.35,
          27: Math.PI * 0.35,
          28: Math.PI * 0.65,
          18: Math.PI * 0.5,
          19: Math.PI * 0.4,
          21: Math.PI * 0.5,
          22: Math.PI * 0.4,
          14: Math.PI * 0.7,
          15: Math.PI * 0.8,
          16: -Math.PI * 0.4,
        })
      },
      { ...groundSlot }
    ]
  };

  // Fotograma 5: Aterrizaje amortiguado (Crouch de impacto heroico)
  const frame5 = {
    duration_ticks: 12,
    objects: [
      {
        ...monkeySlot,
        root_x: 480,
        root_y: 390, // Aterriza bajo
        angles: makeAngles({
          24: Math.PI * 0.85, // Rodillas bien flexionadas
          25: Math.PI * 0.15,
          27: Math.PI * 0.2,
          28: Math.PI * 0.85,
          18: Math.PI * 0.7,  // Mano en el suelo (Superhero landing)
          19: Math.PI * 0.2,
          21: -Math.PI * 0.2, // Brazo hacia atrás
          22: 0,
          14: Math.PI * 0.8,
          15: Math.PI * 0.9,
          16: -Math.PI * 0.6,
        })
      },
      { ...groundSlot }
    ]
  };

  // Fotograma 6: De pie de nuevo, orgulloso
  const frame6 = {
    duration_ticks: 18,
    objects: [
      {
        ...monkeySlot,
        root_x: 480,
        root_y: 340,
        angles: [...initialAngles]
      },
      { ...groundSlot }
    ]
  };

  const keyframes = [frame0, frame1, frame2, frame3, frame4, frame5, frame6];

  editor.report.keyframes = keyframes.map(kf => createFrame(kf.objects, kf.duration_ticks));

  editor.report.total_output_frames = keyframes.reduce((sum, f) => sum + f.duration_ticks, 0);

  const outputPath = path.join(__dirname, 'mono_animado.styk');
  const container = await buildContainerV2(editor.serialize(), 'styk');
  await writeFile(outputPath, container);
  console.log(`✅ Archivo de animación de Mono guardado en: ${outputPath}`);

  // Exportar al reproductor HTML
  const htmlPath = path.join(__dirname, 'mono_animado.html');
  await exportToHtml(outputPath, htmlPath);
  console.log(`🎉 Visualizador web generado en: ${htmlPath}`);
}

createMonkeyAnimation().catch(console.error);
