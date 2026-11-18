/**
 * Compact, model-friendly views of an open project.
 *
 * The editor's own data is dense and uses native field names. These helpers
 * keep the names a model can act on, drop the parts no tool reads, and cap
 * the size of every list so a tool result never floods the context window.
 */

/** Cap on the number of rows any one list returns. */
export const DEFAULT_LIMIT = 50;
export const MAX_LIMIT = 500;

const round = (value, places = 2) => {
  if (typeof value !== 'number' || !Number.isFinite(value)) return value;
  const factor = 10 ** places;
  return Math.round(value * factor) / factor;
};

const point = value => (value ? { x: round(value.x), y: round(value.y) } : null);

/**
 * The figure instances the animation shows at the playhead.
 *
 * The figures come from the evaluated frame, so a project with an advanced
 * timeline reports the figures its sheet exposes, not only the ones a stored
 * keyframe happens to hold. `keyframes` lists the stored poses that contain
 * each figure.
 */
export function figureRows(editor) {
  const report = editor.report;
  const names = figureNames(report);
  const layerOf = editor.layerForUid?.bind(editor);
  const evaluated = editor.evaluatedFrame;

  const appearances = new Map();
  report.keyframes.forEach((frame, frameIndex) => {
    for (const object of frame.objects) {
      if (!appearances.has(object.unique_id)) appearances.set(object.unique_id, []);
      appearances.get(object.unique_id).push(frameIndex);
    }
  });

  const rows = new Map();
  for (const object of evaluated.objects) {
    rows.set(object.unique_id, {
      uid: object.unique_id,
      name: names.get(object.unique_id)?.name ?? names.get(object.figure_type_id)?.name ?? `Figure ${object.unique_id}`,
      figureTypeId: object.figure_type_id,
      layerId: layerOf ? layerOf(object.unique_id) : null,
      keyframes: appearances.get(object.unique_id) ?? [],
      root: { x: round(object.root_x), y: round(object.root_y) },
      scale: round(object.scale ?? 1),
      opacity: round(object.opacity ?? 1),
      colorRgb: object.color_override_rgb ?? null,
      joinedTo: object.join ? { uid: object.join.target_unique_id ?? null, handleId: object.join.target_handle_id } : null,
      hasIk: Boolean(object._stykIK && Object.keys(object._stykIK).length),
    });
  }
  return [...rows.values()];
}

function figureNames(report) {
  const names = new Map();
  for (const figure of report.figure_types) {
    if (figure.name) names.set(figure.figure_type_id, { name: figure.name });
  }
  for (const key of Object.keys(report._styk?.figureNames ?? {})) {
    names.set(Number(key), { name: report._styk.figureNames[key] });
  }
  return names;
}

/**
 * The stored poses of a project.
 *
 * `position` says where the playback reaches a pose; it is null for a pose
 * the playback never shows, which a project with an advanced timeline can
 * hold. A position is the number the pose and figure tools take.
 */
export function keyframeRows(editor) {
  const report = editor.report;
  const timeline = editor.timeline;
  return report.keyframes.map((frame, index) => {
    const position = timeline.findIndex(entry => entry.index === index);
    const row = position < 0 ? null : timeline[position];
    const duration = Math.max(0, frame.duration_raw ?? 1);
    return {
      keyframe: index,
      position: position < 0 ? null : position,
      frameId: editor.getFrameId?.(index) ?? null,
      durationRaw: duration,
      inbetweens: report.version >= 5 ? Math.max(0, duration - 1) : 0,
      startTick: row?.start ?? null,
      outputTicks: row?.count ?? null,
      seconds: round((row?.count ?? duration) / (report.fps || 1), 3),
      objects: frame.objects?.length ?? 0,
      backgroundId: frame.background_id ?? 0,
      camera: frame.camera?.is_default ? 'default' : 'moved',
    };
  });
}

/** The playback timeline: the places the playhead moves through. */
export function playbackRows(editor, { from = 0, to = Infinity } = {}) {
  return editor.timeline
    .map((row, position) => ({
      position,
      keyframe: row.index,
      startTick: row.start,
      ticks: row.count,
      seconds: round(row.count / (editor.report.fps || 1), 3),
    }))
    .filter(row => row.startTick >= from && row.startTick <= to);
}

/** The layer list, with the figures each one holds. */
export function layerRows(editor) {
  return editor.getLayers().map(layer => ({
    id: layer.id,
    name: layer.name,
    kind: layer.kind,
    visible: layer.visible,
    locked: layer.locked,
    figureCount: layer.figureUids?.length ?? 0,
    figureUids: layer.figureUids ?? [],
  }));
}

/** How many distinct figure instances the project holds. */
export function instanceCount(editor) {
  const uids = new Set();
  for (const frame of editor.report.keyframes) {
    for (const object of frame.objects) uids.add(object.unique_id);
  }
  for (const frame of Object.values(editor.report._styk?.frameSources ?? {})) {
    for (const object of frame.objects ?? []) uids.add(object.unique_id);
  }
  return uids.size;
}

/** The whole project at a glance. */
export function projectSummary(project) {
  const { editor } = project;
  const report = editor.report;
  const rows = editor.timeline;
  const last = rows.at(-1);
  const totalTicks = last ? last.start + last.count : 0;
  const figures = figureRows(editor);
  const warnings = editor.geometry?.warnings ?? [];
  return {
    id: project.id,
    name: project.name,
    path: project.path,
    format: project.kind,
    documentVersion: report.version,
    canvas: { width: report.canvas_width, height: report.canvas_height },
    fps: report.fps,
    frames: {
      keyframes: report.keyframes.length,
      totalTicks,
      outputFrames: report.total_output_frames ?? totalTicks,
      durationSeconds: round(report.duration_seconds ?? totalTicks / (report.fps || 1), 3),
    },
    figures: {
      definitions: report.figure_types.length,
      instances: instanceCount(editor),
      visibleNow: figures.length,
    },
    layers: layerRows(editor).length,
    backgrounds: (report.backgrounds ?? []).length,
    vfxClips: Object.keys(report._styk?.vfx?.clips ?? {}).length,
    movieclips: report.figure_types.filter(figure => figure._styk?.movieclip).length,
    audioTracks: (report._styk?.audio?.tracks ?? []).length,
    advancedTimeline: Boolean(report._styk?.layerSheet),
    hasAnimationChannels: (editor.animationChannels ?? []).length > 0,
    dirty: editor.dirty,
    revision: editor.revision,
    undoDepth: editor.canUndo ? editor.undoLabel : null,
    geometryWarnings: warnings,
  };
}

/**
 * The definition of one figure type: its segments, fills and rig.
 *
 * `handleId` is the native segment identity that every other tool accepts;
 * `index` is the position in the segment array.
 */
export function figureDefinition(report, figureTypeId) {
  const figure = report.figure_types.find(entry => entry.figure_type_id === figureTypeId);
  if (!figure) return null;
  const segments = (figure.segments ?? []).map((segment, index) => ({
    handleId: segment.segment_id,
    index,
    name: segment.name ?? null,
    parentHandleId: segment.parent_id,
    length: round(segment.length),
    angleRad: round(segment.angle_rad, 4),
    bendRad: round(segment.bend_rad ?? 0, 4),
    thickness: round(segment.thickness),
    shape: segment.segment_type ?? segment.segment_kind ?? 'line',
    colorRgb: segment.color_rgb ?? null,
    transparency: segment.transparency ?? 0,
    zOrder: segment.z_order ?? null,
    visible: segment.visible !== false,
    isStatic: Boolean(segment.is_static),
  }));
  const polyfills = (figure.polyfills ?? []).map((polygon, index) => ({
    index,
    handleIds: polygon.handle_ids ?? polygon.handleIds ?? [],
    colorRgb: polygon.color_rgb ?? null,
    opacity: polygon.color_alpha ?? null,
    zOrder: polygon.z_order ?? null,
  }));
  return {
    figureTypeId: figure.figure_type_id,
    name: figure.name ?? null,
    segmentCount: segments.length,
    segments,
    polyfills,
    rig: {
      isMovieclip: Boolean(figure._styk?.movieclip),
      hasPoseChoices: Boolean(figure._styk?.poseChoices),
      hasSpatialMesh: figure._styk?.spatialMesh !== undefined,
      animationOrigin: figure._styk?.animationOrigin ?? null,
      colorMode: figure._styk?.colorMode ?? null,
    },
  };
}

/**
 * The evaluated rig at one point in time.
 *
 * `joints` are the world positions of every handle; `segments` carry the
 * solved endpoints, so a model can reason about where a limb actually is.
 */
export function poseReport(editor, { keyframe, tick, uids = null }) {
  const report = editor.report;
  const rows = editor.timeline;
  const position = Math.max(0, Math.min(rows.length - 1, keyframe));
  const row = rows[position];
  const absoluteTick = tick ?? row?.start ?? 0;
  const frame = editor.seek(absoluteTick);
  const geometry = editor.geometry;
  const wanted = uids ? new Set(uids.map(Number)) : null;
  const figures = [];

  for (const object of frame.objects) {
    if (wanted && !wanted.has(object.unique_id)) continue;
    const solved = geometry.objects.get(object.object_slot);
    const definition = report.figure_types.find(entry => entry.figure_type_id === object.figure_type_id);
    if (!solved) continue;
    const segments = definition?.segments ?? [];
    figures.push({
      uid: object.unique_id,
      name: definition?.name ?? null,
      figureTypeId: object.figure_type_id,
      root: point(solved.root),
      scale: round(object.scale ?? 1),
      opacity: round(object.opacity ?? 1),
      joints: [...solved.joints.entries()]
        .map(([handleId, joint]) => {
          const segment = segments.find(entry => entry.segment_id === handleId);
          return {
            handleId,
            index: segment ? segments.indexOf(segment) : null,
            name: segment?.name ?? (handleId === 0 ? 'Root' : null),
            parentHandleId: segment?.parent_id ?? null,
            x: round(joint.x),
            y: round(joint.y),
          };
        })
        .sort((a, b) => a.handleId - b.handleId),
      segments: (solved.segments ?? []).map(render => ({
        handleId: render.seg?.segment_id ?? null,
        index: render.index,
        name: render.seg?.name ?? null,
        shape: render.type,
        start: point(render.start),
        end: point(render.end),
        length: round(render.length),
        angleRad: round(render.angle, 6),
        thickness: round(render.thickness),
        colorRgb: render.rgb ?? null,
        visible: render.seg?.visible !== false,
      })),
      ik: Object.entries(object._stykIK ?? {}).map(([handleId, controller]) => ({
        handleId: Number(handleId),
        enabled: controller.enabled !== false,
        pinned: Boolean(controller.pinned),
        allowStretch: Boolean(controller.allowStretch),
        chainLength: controller.chainLength ?? null,
        target: point(controller.target),
      })),
      joinedTo: object.join ? { uid: object.join.target_unique_id ?? null, handleId: object.join.target_handle_id } : null,
    });
  }

  return {
    keyframe: position,
    tick: absoluteTick,
    seconds: round(absoluteTick / (report.fps || 1), 3),
    figureCount: figures.length,
    figures,
  };
}

/** Cap a list and say so, so the model knows it did not see everything. */
export function paginate(items, { limit = DEFAULT_LIMIT, offset = 0 } = {}) {
  const capped = Math.max(1, Math.min(MAX_LIMIT, Math.trunc(limit) || DEFAULT_LIMIT));
  const start = Math.max(0, Math.trunc(offset) || 0);
  const slice = items.slice(start, start + capped);
  return {
    items: slice,
    total: items.length,
    returned: slice.length,
    offset: start,
    truncated: start + slice.length < items.length,
    nextOffset: start + slice.length < items.length ? start + slice.length : null,
  };
}
