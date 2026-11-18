#!/usr/bin/env node
/**
 * Generate Act 1 Tactical 2D IK Pre-Vis (.styk + evaluated 72-frame JSON)
 * using StykAnimate's native Editor, Analytical 2-Bone IK, validateScene, and ContainerV2 codec.
 */
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, '..');
const mcpRoot = path.join(projectRoot, 'packages', 'stick-animator', 'stykanimate-mcp');
const outDir = path.join(projectRoot, 'outputs', 'showcase_monorepo');

const { Editor, createStartupDocument, buildContainerV2 } = await import(
  pathToFileURL(path.join(mcpRoot, 'src', 'core.js')).href
);
const { createFrame } = await import(
  pathToFileURL(path.join(mcpRoot, 'vendor', 'stykanimate', 'src', 'demo.mjs')).href
);
const { validateScene } = await import(
  pathToFileURL(path.join(mcpRoot, 'vendor', 'stykanimate', 'src', 'pivot', 'model.mjs')).href
);

/**
 * Analytical Two-Bone 2D IK Solver (world angles in radians matching StykAnimate coordinates:
 * +X right, +Y down).
 */
function solveLegIK(hipX, hipY, footTargetX, footTargetY, l1, l2, bendForward = true) {
  const dx = footTargetX - hipX;
  const dy = footTargetY - hipY;
  const maxReach = (l1 + l2) * 0.995;
  const minReach = Math.abs(l1 - l2) + 2.0;
  const dist = Math.max(minReach, Math.min(maxReach, Math.hypot(dx, dy)));
  const baseAngle = Math.atan2(dy, dx);

  const cosHip = Math.max(-1, Math.min(1, (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist)));
  const hipOffset = Math.acos(cosHip);
  // Knees bend forward (+X) -> thigh angled ahead (smaller angle), knee back -> larger angle
  const thighAngle = bendForward ? baseAngle - hipOffset : baseAngle + hipOffset;

  const kneeX = hipX + l1 * Math.cos(thighAngle);
  const kneeY = hipY + l1 * Math.sin(thighAngle);
  const calfAngle = Math.atan2(footTargetY - kneeY, footTargetX - kneeX);
  return { thighAngle, calfAngle, kneeX, kneeY, footX: kneeX + l2 * Math.cos(calfAngle), footY: kneeY + l2 * Math.sin(calfAngle) };
}

async function main() {
  await mkdir(outDir, { recursive: true });
  const editor = new Editor({ demo: false });
  editor.load(createStartupDocument());

  editor.report.canvas_width = 1280;
  editor.report.canvas_height = 720;
  editor.report.fps = 24;

  // Palette matching Ragdoll Firefighter & TIME Poster theme
  const coatDark = [48, 50, 56];
  const coatStripe = [225, 200, 40];
  const helmetRed = [215, 30, 42];
  const brimSteel = [235, 238, 244];
  const hairOrange = [230, 105, 30];
  const woodBrown = [135, 72, 42];
  const neonCyan = [0, 235, 255];
  const floorGray = [32, 36, 44];

  const L_PELVIS = 24;
  const L_TORSO = 36;
  const L_CHEST = 32;
  const L_THIGH = 52;
  const L_CALF = 50;

  const segments = [
    { segment_id: 1, parent_id: 0, length: L_PELVIS, angle_rad: -Math.PI / 2, thickness: 28, primitive_code: 0, color_rgb: coatDark, name: 'Pelvis', z_order: 10 },
    { segment_id: 2, parent_id: 1, length: L_TORSO, angle_rad: -Math.PI / 2, thickness: 32, primitive_code: 0, color_rgb: coatDark, name: 'Torso', z_order: 11 },
    { segment_id: 3, parent_id: 2, length: L_CHEST, angle_rad: -Math.PI / 2, thickness: 36, primitive_code: 0, color_rgb: coatStripe, name: 'ChestStripe', z_order: 12 },
    { segment_id: 4, parent_id: 3, length: 14, angle_rad: -Math.PI / 2, thickness: 18, primitive_code: 0, color_rgb: coatDark, name: 'Neck', z_order: 13 },
    { segment_id: 5, parent_id: 4, length: 38, angle_rad: -Math.PI / 2, thickness: 0, primitive_code: 3, color_rgb: hairOrange, name: 'Head', z_order: 14 },
    { segment_id: 6, parent_id: 5, length: 28, angle_rad: -Math.PI / 2, thickness: 24, primitive_code: 0, color_rgb: helmetRed, name: 'HelmetDome', z_order: 15 },
    { segment_id: 7, parent_id: 5, length: 34, angle_rad: -0.08, thickness: 8, primitive_code: 0, color_rgb: helmetRed, name: 'HelmetBrim', z_order: 16 },
    // Left arm (back)
    { segment_id: 8, parent_id: 3, length: 36, angle_rad: Math.PI * 0.72, thickness: 14, primitive_code: 0, color_rgb: coatDark, name: 'UpperArmL', z_order: 6 },
    { segment_id: 9, parent_id: 8, length: 32, angle_rad: Math.PI * 0.45, thickness: 13, primitive_code: 0, color_rgb: coatStripe, name: 'LowerArmL', z_order: 6 },
    // Left leg (back)
    { segment_id: 10, parent_id: 1, length: L_THIGH, angle_rad: Math.PI * 0.60, thickness: 20, primitive_code: 0, color_rgb: coatDark, name: 'ThighL', z_order: 5 },
    { segment_id: 11, parent_id: 10, length: L_CALF, angle_rad: Math.PI * 0.48, thickness: 17, primitive_code: 0, color_rgb: coatStripe, name: 'CalfL', z_order: 5 },
    { segment_id: 12, parent_id: 11, length: 24, angle_rad: 0.0, thickness: 14, primitive_code: 0, color_rgb: [28, 30, 35], name: 'BootL', z_order: 6 },
    // Right leg (front)
    { segment_id: 13, parent_id: 1, length: L_THIGH, angle_rad: Math.PI * 0.35, thickness: 20, primitive_code: 0, color_rgb: coatDark, name: 'ThighR', z_order: 15 },
    { segment_id: 14, parent_id: 13, length: L_CALF, angle_rad: Math.PI * 0.52, thickness: 17, primitive_code: 0, color_rgb: coatStripe, name: 'CalfR', z_order: 15 },
    { segment_id: 15, parent_id: 14, length: 24, angle_rad: 0.0, thickness: 14, primitive_code: 0, color_rgb: [28, 30, 35], name: 'BootR', z_order: 16 },
    // Right arm + Fire Axe Prop (Segments 16-20)
    { segment_id: 16, parent_id: 3, length: 36, angle_rad: Math.PI * 0.30, thickness: 14, primitive_code: 0, color_rgb: coatDark, name: 'UpperArmR', z_order: 20 },
    { segment_id: 17, parent_id: 16, length: 32, angle_rad: -Math.PI * 0.12, thickness: 13, primitive_code: 0, color_rgb: coatStripe, name: 'LowerArmR', z_order: 21 },
    { segment_id: 18, parent_id: 17, length: 68, angle_rad: -Math.PI * 0.35, thickness: 8, primitive_code: 0, color_rgb: woodBrown, name: 'AxeHandle', z_order: 22 },
    { segment_id: 19, parent_id: 18, length: 28, angle_rad: Math.PI * 0.15, thickness: 20, primitive_code: 0, color_rgb: helmetRed, name: 'AxeHeadRed', z_order: 23 },
    { segment_id: 20, parent_id: 19, length: 12, angle_rad: Math.PI * 0.15, thickness: 22, primitive_code: 0, color_rgb: brimSteel, name: 'AxeEdgeSteel', z_order: 24 },
  ];

  const formattedSegments = segments.map((s) => ({
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

  const heroFigure = {
    figure_type_id: 401,
    name: 'Rescue_Firefighter_2D',
    segment_count: formattedSegments.length,
    segments: formattedSegments,
    polyfills: [],
    image_assets: [],
    text_assets: [],
  };

  const floorFigure = {
    figure_type_id: 402,
    name: 'Sector7_Floor',
    segment_count: 2,
    segments: [
      {
        segment_id: 1,
        parent_id: 0,
        length: 1120,
        angle_rad: 0,
        thickness: 14,
        primitive_code: 0,
        aux_code: 0,
        flags: 0,
        segment_type: 'line',
        segment_kind: 'line',
        color_rgb: floorGray,
        transparency: 0,
        visible: true,
        z_order: 1,
        name: 'FloorDeck',
      },
      {
        segment_id: 2,
        parent_id: 0,
        length: 1120,
        angle_rad: 0,
        thickness: 3,
        primitive_code: 0,
        aux_code: 0,
        flags: 0,
        segment_type: 'line',
        segment_kind: 'line',
        color_rgb: neonCyan,
        transparency: 0,
        visible: true,
        z_order: 2,
        name: 'FloorGridLine',
      },
    ],
    polyfills: [],
    image_assets: [],
    text_assets: [],
  };

  const droneFigure = {
    figure_type_id: 403,
    name: 'Thermal_Core_Drone',
    segment_count: 2,
    segments: [
      {
        segment_id: 1,
        parent_id: 0,
        length: 54,
        angle_rad: 0,
        thickness: 0,
        primitive_code: 3,
        aux_code: 0,
        flags: 3,
        segment_type: 'circle',
        segment_kind: 'circleFill',
        color_rgb: [255, 85, 25],
        transparency: 0,
        visible: true,
        z_order: 8,
        name: 'CoreSphere',
      },
      {
        segment_id: 2,
        parent_id: 1,
        length: 76,
        angle_rad: Math.PI / 4,
        thickness: 5,
        primitive_code: 0,
        aux_code: 0,
        flags: 0,
        segment_type: 'line',
        segment_kind: 'line',
        color_rgb: neonCyan,
        transparency: 0,
        visible: true,
        z_order: 9,
        name: 'ReactorRing',
      },
    ],
    polyfills: [],
    image_assets: [],
    text_assets: [],
  };

  editor.report.figure_types = [heroFigure, floorFigure, droneFigure];

  const baseAngles = formattedSegments.map((s) => s.angle_rad);
  const heroTemplate = {
    object_slot: 0,
    unique_id: 1,
    figure_type_id: 401,
    root_x: 180,
    root_y: 440,
    scale: 1.0,
    color_override_raw: 0,
    color_override_rgb: [0, 0, 0],
    color_override_mix: 0,
    transparency: 0,
    opacity: 1,
    field28: 0,
    angles: baseAngles,
    len_flag: 0,
    lengths: [],
    bend_flag: 0,
    bends: [],
    join: null,
  };

  const floorSlot = {
    object_slot: 1,
    unique_id: 2,
    figure_type_id: 402,
    root_x: 80,
    root_y: 540,
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

  // Build 13 keyframes summing to exactly 72 ticks (24 FPS x 3.0s)
  const keyframeSpecs = [
    { tick: 0, dur: 6, rootX: 200, rootY: 448, lFoot: [165, 540], rFoot: [240, 540], lean: 0.14, axeAngle: -0.55 },
    { tick: 6, dur: 6, rootX: 265, rootY: 440, lFoot: [295, 540], rFoot: [215, 520], lean: 0.22, axeAngle: -0.70 },
    { tick: 12, dur: 6, rootX: 335, rootY: 448, lFoot: [380, 540], rFoot: [295, 540], lean: 0.18, axeAngle: -0.60 },
    { tick: 18, dur: 6, rootX: 410, rootY: 458, lFoot: [365, 540], rFoot: [445, 540], lean: 0.25, axeAngle: -0.85 },
    { tick: 24, dur: 6, rootX: 490, rootY: 405, lFoot: [445, 500], rFoot: [545, 480], lean: 0.30, axeAngle: -1.35 },
    { tick: 30, dur: 6, rootX: 575, rootY: 365, lFoot: [520, 465], rFoot: [625, 450], lean: 0.32, axeAngle: -1.75 },
    { tick: 36, dur: 6, rootX: 655, rootY: 382, lFoot: [600, 480], rFoot: [705, 472], lean: 0.28, axeAngle: -1.55 },
    { tick: 42, dur: 6, rootX: 735, rootY: 448, lFoot: [695, 540], rFoot: [785, 530], lean: 0.20, axeAngle: -1.00 },
    { tick: 48, dur: 6, rootX: 795, rootY: 465, lFoot: [755, 540], rFoot: [835, 540], lean: 0.16, axeAngle: -0.65 },
    { tick: 54, dur: 6, rootX: 830, rootY: 446, lFoot: [795, 540], rFoot: [865, 540], lean: 0.08, axeAngle: -0.50 },
    { tick: 60, dur: 6, rootX: 850, rootY: 444, lFoot: [815, 540], rFoot: [885, 540], lean: 0.04, axeAngle: -0.45 },
    { tick: 66, dur: 6, rootX: 860, rootY: 444, lFoot: [825, 540], rFoot: [895, 540], lean: 0.02, axeAngle: -0.40 },
  ];

  const ikTelemetry = [];
  editor.report.keyframes = keyframeSpecs.map((k, idx) => {
    const angles = [...baseAngles];
    const spineBase = -Math.PI / 2 + k.lean;
    angles[0] = spineBase;
    angles[1] = spineBase;
    angles[2] = spineBase;
    angles[3] = -Math.PI / 2 + k.lean * 0.4;
    angles[4] = -Math.PI / 2;

    const lIk = solveLegIK(k.rootX, k.rootY, k.lFoot[0], k.lFoot[1], L_THIGH, L_CALF, true);
    const rIk = solveLegIK(k.rootX, k.rootY, k.rFoot[0], k.rFoot[1], L_THIGH, L_CALF, true);

    angles[9] = lIk.thighAngle;
    angles[10] = lIk.calfAngle;
    angles[11] = 0.0;

    angles[12] = rIk.thighAngle;
    angles[13] = rIk.calfAngle;
    angles[14] = 0.0;

    // Arms & axe
    angles[7] = Math.PI * 0.72 - k.lean * 1.4;
    angles[8] = Math.PI * 0.40 - k.lean * 0.8;
    angles[15] = 0.35 + k.axeAngle * 0.45;
    angles[16] = k.axeAngle * 0.55;
    angles[17] = k.axeAngle;
    angles[18] = k.axeAngle + Math.PI / 2;
    angles[19] = k.axeAngle + Math.PI / 2;

    ikTelemetry.push({
      keyframe: idx,
      tick: k.tick,
      root: { x: k.rootX, y: k.rootY },
      left_foot_target: { x: k.lFoot[0], y: k.lFoot[1] },
      right_foot_target: { x: k.rFoot[0], y: k.rFoot[1] },
      left_knee: { x: Math.round(lIk.kneeX * 10) / 10, y: Math.round(lIk.kneeY * 10) / 10 },
      right_knee: { x: Math.round(rIk.kneeX * 10) / 10, y: Math.round(rIk.kneeY * 10) / 10 },
      left_thigh_deg: Math.round((lIk.thighAngle * 180 / Math.PI) * 10) / 10,
      right_thigh_deg: Math.round((rIk.thighAngle * 180 / Math.PI) * 10) / 10,
    });

    const hero = {
      ...heroTemplate,
      root_x: k.rootX,
      root_y: k.rootY,
      angles,
    };
    const drone = {
      object_slot: 2,
      unique_id: 3,
      figure_type_id: 403,
      root_x: 1120,
      root_y: 350 + Math.round(Math.sin((idx / 12) * Math.PI * 2) * 16),
      scale: 1.0,
      color_override_raw: 0,
      color_override_rgb: [0, 0, 0],
      color_override_mix: 0,
      transparency: 0,
      opacity: 1,
      field28: 0,
      angles: [0, (idx * Math.PI) / 6],
      len_flag: 0,
      lengths: [],
      bend_flag: 0,
      bends: [],
      join: null,
    };
    return createFrame([hero, floorSlot, drone], k.dur);
  });

  editor.report.total_output_frames = 72;
  delete editor.report._styk?.layerSheet;

  validateScene(editor.report);

  const stykPath = path.join(outDir, 'act1_tactical_previz.styk');
  const serialized = editor.serialize();
  const binaryContainer = await buildContainerV2(serialized, 'styk');
  await writeFile(stykPath, binaryContainer);

  // Re-open in Editor and evaluate all 72 interpolated frames for exact drawable coordinates
  const evalEditor = new Editor({ demo: false });
  evalEditor.load(serialized);
  const frames = [];
  for (let t = 0; t < 72; t++) {
    evalEditor.seek(t);
    const drawables = (evalEditor.geometry.drawables || []).map((d) => ({
      type: d.type,
      start: d.start ? { x: Math.round(d.start.x * 10) / 10, y: Math.round(d.start.y * 10) / 10 } : null,
      end: d.end ? { x: Math.round(d.end.x * 10) / 10, y: Math.round(d.end.y * 10) / 10 } : null,
      points: d.points ? d.points.map((p) => ({ x: Math.round(p.x * 10) / 10, y: Math.round(p.y * 10) / 10 })) : null,
      length: d.length ? Math.round(d.length * 10) / 10 : 0,
      thickness: d.thickness ? Math.round(d.thickness * 10) / 10 : 6,
      rgb: d.rgb || [200, 200, 200],
      alpha: d.alpha ?? 1,
      z: d.z || 0,
      code: d.seg?.primitive_code ?? 0,
      name: d.seg?.name || '',
    }));
    drawables.sort((a, b) => a.z - b.z);
    frames.push(drawables);
  }

  const jsonPath = path.join(outDir, 'act1_ik_frames.json');
  await writeFile(
    jsonPath,
    JSON.stringify(
      {
        canvas_width: 1280,
        canvas_height: 720,
        fps: 24,
        total_frames: 72,
        segment_lengths_px: { pelvis: L_PELVIS, torso: L_TORSO, chest: L_CHEST, thigh: L_THIGH, calf: L_CALF },
        ik_telemetry: ikTelemetry,
        frames,
      },
      null,
      2,
    ),
    'utf-8',
  );
  console.log(`Generated StykAnimate binary (${binaryContainer.length} bytes): ${stykPath}`);
  console.log(`Exported 72 evaluated IK frames: ${jsonPath}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
