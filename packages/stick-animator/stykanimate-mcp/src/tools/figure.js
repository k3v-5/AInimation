/**
 * Figure tools: find, add, duplicate, remove and transform the figures in a
 * project.
 *
 * Every change goes through the editor's own range commands, so a tool call
 * is one undoable step and the same rules apply as in the app.
 */
import { z } from 'zod/v4';
import { figureDefinition, figureRows, paginate, DEFAULT_LIMIT } from '../summary.js';
import { ToolError } from '../errors.js';
import { degrees, goToKeyframe, keyframeIndex, nativeIndices, project, rangeOptions, result, selectObject } from './shared.js';

const projectField = z
  .string()
  .optional()
  .describe('The id of an open project, from project_open. Defaults to the project used most recently.');
const frameField = z.number().int().optional().describe('The place on the timeline to work on. Defaults to the playhead.');
const uidField = z.number().int().describe('The id of the figure instance.');

export function registerFigureTools(server, { store }) {
  server.registerTool(
    'figure_list',
    {
      title: 'List figures',
      description:
        'List the figure instances the animation shows, with their ids, names, layers, position, scale, opacity ' +
        'and colour, and the stored keyframes that hold them. ' +
        'Give a keyframe number to list the figures at that moment; without one the playhead decides. ' +
        'Use the ids this returns with the other figure and pose tools.',
      inputSchema: z.object({
        project: projectField,
        frame: frameField,
        layer: z.string().optional().describe('Only figures on this layer id.'),
        name: z.string().optional().describe('Only figures whose name contains this text.'),
        limit: z.number().int().min(1).max(500).optional().describe(`How many rows to return (default ${DEFAULT_LIMIT}).`),
      }),
      annotations: { readOnlyHint: true, idempotentHint: true },
    },
    async input => {
      const current = project(store, input);
      if (input.frame !== undefined) goToKeyframe(current.editor, keyframeIndex(current.editor, input));
      let rows = figureRows(current.editor);
      if (input.layer) rows = rows.filter(row => row.layerId === input.layer);
      if (input.name) {
        const needle = input.name.toLowerCase();
        rows = rows.filter(row => (row.name ?? '').toLowerCase().includes(needle));
      }
      const page = paginate(rows, { limit: input.limit });
      return result(`${page.returned} of ${page.total} figures.`, { figures: page });
    },
  );

  server.registerTool(
    'figure_describe',
    {
      title: 'Describe a figure',
      description:
        'Report one figure in full: its definition (every joint with its handle id, parent, length, angle, ' +
        'thickness, shape and colour), its fills, its rig, and where it sits in a keyframe. ' +
        'Name an instance with "uid", or a definition with "figureTypeId".',
      inputSchema: z.object({
        project: projectField,
        uid: uidField.optional().describe('The figure instance to describe.'),
        figureTypeId: z.number().int().optional().describe('The figure definition to describe.'),
        frame: frameField,
      }),
      annotations: { readOnlyHint: true, idempotentHint: true },
    },
    async input => {
      const current = project(store, input);
      const editor = current.editor;
      if (input.uid === undefined && input.figureTypeId === undefined) {
        throw new ToolError('Give a figure uid or a figureTypeId.', { code: 'missing_target' });
      }
      const index = keyframeIndex(editor, input);
      goToKeyframe(editor, index);
      let instance = null;
      if (input.uid !== undefined) {
        instance = selectObject(editor, input.uid, { required: false });
        if (!instance) {
          const here = (editor.selectionFrame ?? editor.frame).objects.map(entry => entry.unique_id);
          throw new ToolError(
            `Figure ${input.uid} is not in keyframe ${index}. Figures there: ${here.length ? here.join(', ') : 'none'}.`,
            { code: 'unknown_figure' },
          );
        }
      }
      const typeId = instance ? instance.figure_type_id : input.figureTypeId;
      const definition = figureDefinition(editor.report, typeId);
      if (!definition) {
        throw new ToolError(`The project has no figure definition with the id ${typeId}.`, { code: 'unknown_figure_type' });
      }
      const data = { definition, keyframe: index };
      if (instance) {
        data.instance = {
          uid: instance.unique_id,
          figureTypeId: instance.figure_type_id,
          root: { x: instance.root_x, y: instance.root_y },
          scale: instance.scale,
          opacity: instance.opacity,
          colorRgb: instance.color_override_rgb ?? null,
          layerId: editor.layerForUid?.(instance.unique_id) ?? null,
          joinedTo: instance.join ? { uid: instance.join.target_unique_id ?? null, handleId: instance.join.target_handle_id } : null,
          ikControllers: Object.entries(instance._stykIK ?? {}).map(([handleId, controller]) => ({
            handleId: Number(handleId),
            enabled: controller.enabled !== false,
            pinned: Boolean(controller.pinned),
            allowStretch: Boolean(controller.allowStretch),
            chainLength: controller.chainLength ?? null,
            target: controller.target ? { x: controller.target.x, y: controller.target.y } : null,
          })),
        };
      }
      return result(
        `${definition.name ?? `Figure ${typeId}`}: ${definition.segmentCount} joints` +
          (instance ? `, instance ${instance.unique_id} at (${Math.round(instance.root_x)}, ${Math.round(instance.root_y)})` : '') +
          ` in keyframe ${index}.`,
        data,
      );
    },
  );

  server.registerTool(
    'figure_add',
    {
      title: 'Add a figure',
      description:
        'Add a figure instance to the keyframe the playhead is on, using one of the existing figure definitions. ' +
        'The new figure is placed at the given position, or at the centre of the canvas. ' +
        'Give a keyframe number to choose the keyframe; without one the playhead decides. ' +
        'Give the definition to use with "figureTypeId"; omit it to use the first definition in the project.',
      inputSchema: z.object({
        project: projectField,
        figureTypeId: z.number().int().optional().describe('The figure definition to instantiate.'),
        frame: frameField,
        x: z.number().optional().describe('Where to place the figure, in canvas pixels.'),
        y: z.number().optional().describe('Where to place the figure, in canvas pixels.'),
      }),
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false },
    },
    async input => {
      const current = project(store, input);
      const editor = current.editor;
      const index = keyframeIndex(editor, input);
      goToKeyframe(editor, index);
      const typeId = input.figureTypeId ?? editor.report.figure_types[0]?.figure_type_id;
      if (typeId === undefined) {
        throw new ToolError('The project has no figure definitions to add.', { code: 'no_definitions' });
      }
      const operation = { kind: 'add', typeId };
      if (input.x !== undefined) operation.x = input.x;
      if (input.y !== undefined) operation.y = input.y;
      editor.applyFigureRange(operation, { atPlayhead: true, label: 'Add figure' });
      const added = editor.selectedUid;
      return result(
        `Added a figure to keyframe ${index} (uid ${added}).`,
        { uid: added, figureTypeId: typeId, keyframe: index, project: current.id },
      );
    },
  );

  server.registerTool(
    'figure_duplicate',
    {
      title: 'Duplicate a figure',
      description:
        'Copy a figure, including its pose, into a keyframe. Give a keyframe number to choose it; without one the ' +
        'playhead decides. The copy is nudged by an offset so it does not sit exactly on the original. ' +
        'The copy gets a new id.',
      inputSchema: z.object({
        project: projectField,
        uid: uidField,
        frame: frameField.describe('The keyframe to copy into. Defaults to the one the figure is in.'),
        offset: z.number().optional().describe('How far to move the copy, in pixels. Defaults to 24.'),
      }),
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false },
    },
    async input => {
      const current = project(store, input);
      const editor = current.editor;
      const source = keyframeIndex(editor, input);
      goToKeyframe(editor, source);
      selectObject(editor, input.uid);
      const options = { offset: input.offset ?? 24, uids: [input.uid] };
      const outcome = editor.duplicateFiguresInFrames(nativeIndices(editor, [source]), options);
      const copy = outcome.insertedUids?.[0] ?? editor.selectedUid;
      return result(`Duplicated figure ${input.uid} into keyframe ${source} as uid ${copy}.`, {
        uid: copy,
        sourceUid: input.uid,
        keyframe: source,
        project: current.id,
      });
    },
  );

  server.registerTool(
    'figure_delete',
    {
      title: 'Remove a figure',
      description:
        'Remove a figure from a keyframe. Figures joined to it are detached and kept. ' +
        'Give "frames" to remove it from several keyframes at once.',
      inputSchema: z.object({
        project: projectField,
        uid: uidField,
        frame: frameField,
        frames: z.array(z.number().int()).optional().describe('Several keyframes to remove the figure from.'),
      }),
      annotations: { readOnlyHint: false, destructiveHint: true, idempotentHint: true },
    },
    async input => {
      const current = project(store, input);
      const editor = current.editor;
      const positions = input.frames ?? [keyframeIndex(editor, input)];
      for (const position of positions) {
        if (position < 0 || position >= editor.timeline.length) {
          throw new ToolError(
            `There is no keyframe ${position}. The animation has ${editor.timeline.length} keyframes ` +
              `(0 to ${editor.timeline.length - 1}).`,
            { code: 'bad_frame' },
          );
        }
      }
      if (!figureAppears(editor, input.uid, positions)) {
        throw new ToolError(
          `Figure ${input.uid} is not in ${positions.length === 1 ? 'that keyframe' : 'those keyframes'}. ` +
            'Use figure_list to see the figures that are there.',
          { code: 'unknown_figure' },
        );
      }
      const outcome = editor.deleteFiguresInFrames(nativeIndices(editor, positions), { uids: [input.uid] });
      return result(`Removed figure ${input.uid} from ${outcome.changedFrames} keyframe(s).`, {
        uid: input.uid,
        changedFrames: outcome.changedFrames,
        project: current.id,
      });
    },
  );

  server.registerTool(
    'figure_transform',
    {
      title: 'Transform a figure',
      description:
        'Change where a figure sits: move it, rotate it, scale it, flip it, align it with other figures, ' +
        'centre it, or change its draw order. Angles are in degrees and turns anticlockwise. ' +
        'Give "uids" to transform several figures in one step; they move together.',
      inputSchema: z.object({
        project: projectField,
        uid: uidField.optional().describe('The figure to transform.'),
        uids: z.array(z.number().int()).optional().describe('Several figures to transform together.'),
        frame: frameField,
        frames: z.array(z.number().int()).optional().describe('Several keyframes to transform the figure in.'),
        action: z
          .enum(['move', 'rotate', 'scale', 'mirror', 'align', 'center', 'order'])
          .describe('The transform to apply.'),
        dx: z.number().optional().describe('For "move": how far to move along x, in pixels.'),
        dy: z.number().optional().describe('For "move": how far to move along y, in pixels.'),
        degrees: z.number().optional().describe('For "rotate": the angle in degrees.'),
        factor: z.number().optional().describe('For "scale": the size factor. 2 doubles the figure.'),
        axis: z
          .enum(['horizontal', 'vertical', 'x', 'y'])
          .optional()
          .describe('For "mirror": the axis to flip across. For "align" and "center": the axis to align on.'),
        edge: z
          .enum(['start', 'center', 'end'])
          .optional()
          .describe('For "align": which edges to line up.'),
        direction: z
          .enum(['front', 'back', 'up', 'down'])
          .optional()
          .describe('For "order": which way to move the figure in the draw order.'),
      }),
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false },
    },
    async input => {
      const current = project(store, input);
      const editor = current.editor;
      const uids = input.uids ?? (input.uid === undefined ? [] : [input.uid]);
      if (!uids.length) {
        throw new ToolError('Give a figure uid to transform.', { code: 'missing_target' });
      }
      const positions = input.frames ?? [keyframeIndex(editor, input)];
      for (const position of positions) {
        if (position < 0 || position >= editor.timeline.length) {
          throw new ToolError(
            `There is no keyframe ${position}. The animation has ${editor.timeline.length} keyframes ` +
              `(0 to ${editor.timeline.length - 1}).`,
            { code: 'bad_frame' },
          );
        }
      }
      goToKeyframe(editor, positions[0]);
      const selected = editor.selectMany(uids);
      if (!selected.length) {
        throw new ToolError(
          `None of the figures ${uids.join(', ')} is in keyframe ${positions[0]}. ` +
            'Use figure_list to see the figures that are there.',
          { code: 'unknown_figure' },
        );
      }
      const range = rangeOptions(editor, positions);
      const frames = range.indices ?? range.ticks ?? [];

      let changed = 0;
      switch (input.action) {
        case 'move': {
          const dx = input.dx ?? 0;
          const dy = input.dy ?? 0;
          changed = editor.moveSelectionInFrames(dx, dy, nativeIndices(editor, positions));
          break;
        }
        case 'rotate': {
          if (input.degrees === undefined) throw new ToolError('Give the angle in degrees.', { code: 'missing_value' });
          changed = editor.rotateFiguresInFrames(degrees(input.degrees), frames).changedFrames;
          break;
        }
        case 'scale': {
          if (input.factor === undefined) throw new ToolError('Give the size factor.', { code: 'missing_value' });
          changed = editor.scaleFiguresInFrames(input.factor, frames, { relative: true }).changedFrames;
          break;
        }
        case 'mirror': {
          if (!input.axis || !['horizontal', 'vertical'].includes(input.axis)) {
            throw new ToolError('Mirroring needs axis "horizontal" or "vertical".', { code: 'missing_value' });
          }
          changed = editor.mirrorFiguresInFrames(input.axis, frames).changedFrames;
          break;
        }
        case 'align': {
          if (!input.axis || !['x', 'y'].includes(input.axis)) {
            throw new ToolError('Aligning needs axis "x" or "y".', { code: 'missing_value' });
          }
          if (!input.edge) {
            throw new ToolError('Aligning needs an edge: "start", "center" or "end".', { code: 'missing_value' });
          }
          changed = editor.alignFiguresInFrames(input.axis, input.edge, frames).changedFrames;
          break;
        }
        case 'center': {
          changed = editor.centerFiguresInFrames(frames).changedFrames;
          break;
        }
        case 'order': {
          if (!input.direction) throw new ToolError('Give a draw order direction.', { code: 'missing_value' });
          const direction =
            input.direction === 'front' ? 'front' : input.direction === 'back' ? 'back' : input.direction === 'up' ? 1 : -1;
          changed = editor.orderFiguresInFrames(direction, frames).changedFrames;
          break;
        }
        default:
          throw new ToolError(`Unknown transform "${input.action}".`, { code: 'bad_action' });
      }
      return result(
        changed
          ? `Applied ${input.action} to ${selected.length} figure(s) across ${positions.length} keyframe(s).`
          : `The ${input.action} changed nothing.`,
        { action: input.action, uids: selected.map(entry => entry.unique_id), frames: positions, changedFrames: changed },
      );
    },
  );
}

/** Whether a figure is shown in any of the given keyframes. */
function figureAppears(editor, uid, positions) {
  const playhead = editor.tick;
  try {
    return positions.some(position => {
      const row = editor.timeline[position];
      if (!row) return false;
      const frame = editor.seek(row.start);
      return Boolean(frame.objects?.some(object => object.unique_id === uid));
    });
  } finally {
    editor.seek(playhead);
  }
}
