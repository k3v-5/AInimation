/**
 * Layer and appearance tools: organise the figures into layers and change
 * how they look.
 */
import { z } from 'zod/v4';
import { layerRows } from '../summary.js';
import { ToolError } from '../errors.js';
import { goToKeyframe, keyframeIndex, nativeIndices, project, result, rgbBytes, selectObject } from './shared.js';

const projectField = z
  .string()
  .optional()
  .describe('The id of an open project, from project_open. Defaults to the project used most recently.');
const frameField = z.number().int().optional().describe('The place on the timeline to work on. Defaults to the playhead.');

export function registerLayerTools(server, { store }) {
  server.registerTool(
    'layer_list',
    {
      title: 'List layers',
      description:
        'List the layers of the open project, with their ids, names, visibility, lock state and the figures each ' +
        'one holds. Use the layer ids this returns with layer_edit and figure_transform.',
      inputSchema: z.object({ project: projectField }),
      annotations: { readOnlyHint: true, idempotentHint: true },
    },
    async input => {
      const current = project(store, input);
      const rows = layerRows(current.editor);
      return result(`${rows.length} layers.`, { layers: rows });
    },
  );

  server.registerTool(
    'layer_edit',
    {
      title: 'Edit layers',
      description:
        'Change the layers of the project: create one, rename one, delete one, reorder them, move figures ' +
        'between them, or show, hide, lock or unlock one. Give the action and the fields it needs.',
      inputSchema: z.object({
        project: projectField,
        action: z
          .enum(['create', 'rename', 'delete', 'reorder', 'assign', 'visible', 'lock'])
          .describe('The change to make.'),
        layerId: z.string().optional().describe('The layer to change.'),
        name: z.string().optional().describe('For "create" and "rename": the layer name.'),
        uids: z.array(z.number().int()).optional().describe('For "assign": the figures to move.'),
        order: z.array(z.string()).optional().describe('For "reorder": every user layer id, in the wanted order.'),
        index: z.number().int().optional().describe('For "create": where to put the new layer.'),
        visible: z.boolean().optional().describe('For "visible": whether to show the layer.'),
        locked: z.boolean().optional().describe('For "lock": whether to lock the layer.'),
      }),
      annotations: { readOnlyHint: false, destructiveHint: true, idempotentHint: false },
    },
    async input => {
      const current = project(store, input);
      const editor = current.editor;
      switch (input.action) {
        case 'create': {
          if (!input.name) throw new ToolError('Give the new layer a name.', { code: 'missing_value' });
          const options = {};
          if (input.index !== undefined) options.index = input.index;
          const layer = editor.createLayer(input.name, options);
          return result(`Created the layer "${layer.name}" (${layer.id}).`, { layer, project: current.id });
        }
        case 'rename': {
          if (!input.layerId) throw new ToolError('Give the layer to rename.', { code: 'missing_value' });
          if (!input.name) throw new ToolError('Give the new layer name.', { code: 'missing_value' });
          editor.renameLayer(input.layerId, input.name);
          return result(`Renamed the layer ${input.layerId} to "${input.name}".`, {
            layerId: input.layerId,
            name: input.name,
            project: current.id,
          });
        }
        case 'delete': {
          if (!input.layerId) throw new ToolError('Give the layer to delete.', { code: 'missing_value' });
          editor.deleteLayer(input.layerId);
          return result(`Deleted the layer ${input.layerId}. Its figures moved to another layer.`, {
            layerId: input.layerId,
            layers: layerRows(editor),
            project: current.id,
          });
        }
        case 'reorder': {
          if (!input.order?.length) throw new ToolError('Give every user layer id in the wanted order.', { code: 'missing_value' });
          editor.reorderLayers(input.order);
          return result(`Reordered the layers.`, { layers: layerRows(editor), project: current.id });
        }
        case 'assign': {
          if (!input.layerId) throw new ToolError('Give the layer to move the figures to.', { code: 'missing_value' });
          if (!input.uids?.length) throw new ToolError('Give the figures to move.', { code: 'missing_value' });
          editor.assignFiguresToLayer(input.uids, input.layerId);
          return result(`Moved ${input.uids.length} figure(s) to the layer ${input.layerId}.`, {
            layerId: input.layerId,
            uids: input.uids,
            project: current.id,
          });
        }
        case 'visible': {
          if (!input.layerId) throw new ToolError('Give the layer to show or hide.', { code: 'missing_value' });
          if (input.visible === undefined) throw new ToolError('Say whether to show the layer.', { code: 'missing_value' });
          editor.setLayerVisible(input.layerId, input.visible);
          return result(`${input.visible ? 'Showed' : 'Hid'} the layer ${input.layerId}.`, {
            layerId: input.layerId,
            visible: input.visible,
            project: current.id,
          });
        }
        case 'lock': {
          if (!input.layerId) throw new ToolError('Give the layer to lock or unlock.', { code: 'missing_value' });
          if (input.locked === undefined) throw new ToolError('Say whether to lock the layer.', { code: 'missing_value' });
          editor.setLayerLocked(input.layerId, input.locked);
          return result(`${input.locked ? 'Locked' : 'Unlocked'} the layer ${input.layerId}.`, {
            layerId: input.layerId,
            locked: input.locked,
            project: current.id,
          });
        }
        default:
          throw new ToolError(`Unknown action "${input.action}".`, { code: 'bad_action' });
      }
    },
  );

  server.registerTool(
    'style_set',
    {
      title: 'Change appearance',
      description:
        'Change how something looks: the colour or opacity of a figure, the colour or thickness of one of its ' +
        'parts, the colour of a layer, or the colour behind the scene. ' +
        'A figure colour applies to every keyframe the figure appears in. ' +
        'A part colour changes the shared figure definition, so every instance of it changes too. ' +
        'Give a colour as "#rrggbb" or as three red, green and blue bytes.',
      inputSchema: z.object({
        project: projectField,
        target: z.enum(['figure', 'part', 'layer', 'scene']).describe('What to restyle.'),
        uid: z.number().int().optional().describe('For "figure" and "part": the figure instance.'),
        handleId: z.number().int().optional().describe('For "part": the joint whose segment to restyle.'),
        layerId: z.string().optional().describe('For "layer": the layer to restyle.'),
        frame: frameField,
        frames: z.array(z.number().int()).optional().describe('For "figure": only these keyframes.'),
        color: z
          .union([z.string(), z.array(z.number().int().min(0).max(255))])
          .optional()
          .describe(
            'The new colour. For a figure, a part or the scene: "#rrggbb" or three RGB bytes. ' +
              'For a layer: a palette name (blue, violet, rose, orange, green, teal); ' +
              'a colour is matched to the nearest one.',
          ),
        opacity: z.number().min(0).max(1).optional().describe('The new opacity, from 0 to 1.'),
        thickness: z.number().min(0).optional().describe('For "part": the new thickness of the segment.'),
      }),
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true },
    },
    async input => {
      const current = project(store, input);
      const editor = current.editor;
      const index = keyframeIndex(editor, input);

      switch (input.target) {
        case 'figure': {
          if (input.uid === undefined) throw new ToolError('Give the figure to restyle.', { code: 'missing_target' });
          if (input.color === undefined && input.opacity === undefined) {
            throw new ToolError('Give a colour, an opacity, or both.', { code: 'missing_value' });
          }
          const operation = { kind: 'recolor', mode: 'all' };
          if (input.color !== undefined) operation.color = rgbBytes(input.color);
          if (input.opacity !== undefined) operation.opacity = input.opacity;

          if (editor.report._styk?.layerSheet) {
            // An advanced timeline exposes its poses as cells, so the change has
            // to name the ticks the playback reaches rather than stored poses.
            const ticks = input.frames
              ? input.frames.map(position => editor.timeline[position]?.start).filter(tick => tick !== undefined)
              : ticksHolding(editor, input.uid);
            if (!ticks.length) {
              throw new ToolError(
                `Figure ${input.uid} is not exposed by the playback timeline, so it cannot be restyled.`,
                { code: 'not_exposed' },
              );
            }
            editor.applyFigureRange(operation, { ticks, uids: [input.uid], label: 'Edit figure colors' });
            return result(
              `Restyled figure ${input.uid} in ${ticks.length} place(s) on the timeline.`,
              { uid: input.uid, ticks, project: current.id },
            );
          }

          const frames = input.frames ?? framesHolding(editor, input.uid);
          if (!frames.length) {
            throw new ToolError(`Figure ${input.uid} is not in any keyframe.`, { code: 'unknown_figure' });
          }
          goToKeyframe(editor, frames[0]);
          editor.applyFigureRange(operation, {
            indices: nativeIndices(editor, frames),
            uids: [input.uid],
            label: 'Edit figure colors',
          });
          return result(
            `Restyled figure ${input.uid} in ${frames.length} keyframe(s).`,
            { uid: input.uid, frames, project: current.id },
          );
        }
        case 'part': {
          if (input.uid === undefined) throw new ToolError('Give the figure whose part to restyle.', { code: 'missing_target' });
          if (input.handleId === undefined) throw new ToolError('Give the joint whose segment to restyle.', { code: 'missing_target' });
          if (input.color === undefined && input.thickness === undefined) {
            throw new ToolError('Give a colour or a thickness.', { code: 'missing_value' });
          }
          goToKeyframe(editor, index);
          selectObject(editor, input.uid);
          const figure = editor.figure;
          const jointIndex = figure.segments.findIndex(segment => segment.segment_id === input.handleId);
          if (jointIndex < 0) {
            throw new ToolError(
              `That figure has no joint with the handle id ${input.handleId}. Its handles: ${figure.segments.map(segment => segment.segment_id).join(', ') || 'none'}.`,
              { code: 'unknown_joint' },
            );
          }
          editor.select(input.uid, jointIndex);
          const patch = {};
          if (input.color !== undefined) patch.color_rgb = rgbBytes(input.color);
          if (input.thickness !== undefined) patch.thickness = input.thickness;
          editor.updateSegment(patch);
          return result(
            `Restyled the part on joint ${input.handleId} of figure ${input.uid}. Every instance of that figure changes.`,
            { uid: input.uid, handleId: input.handleId, patch, project: current.id },
          );
        }
        case 'layer': {
          if (!input.layerId) throw new ToolError('Give the layer to restyle.', { code: 'missing_target' });
          if (input.color === undefined) throw new ToolError('Give the new layer colour.', { code: 'missing_value' });
          const colour = layerColour(input.color);
          editor.setLayerColor([input.layerId], colour);
          return result(`Set the colour of the layer ${input.layerId} to ${colour}.`, {
            layerId: input.layerId,
            color: colour,
            project: current.id,
          });
        }        case 'scene': {
          if (input.color === undefined) throw new ToolError('Give the new scene colour.', { code: 'missing_value' });
          const [r, g, b] = rgbBytes(input.color);
          editor.setSceneColor((0xff << 24 | (r << 16) | (g << 8) | b) >>> 0, { indices: [index] });
          return result(`Set the scene colour in keyframe ${index}.`, {
            keyframe: index,
            color: input.color,
            project: current.id,
          });
        }
        default:
          throw new ToolError(`Unknown target "${input.target}".`, { code: 'bad_action' });
      }
    },
  );
}

/** The colours a layer can take. */
const LAYER_COLORS = Object.freeze({
  blue: '#3399ee',
  violet: '#9966dd',
  rose: '#df6690',
  orange: '#d99035',
  green: '#43a878',
  teal: '#36a8b5',
});

/**
 * The palette name for a layer colour.
 *
 * A layer takes one of the app's palette colours. A name is used as it is; a
 * colour is matched to the nearest one.
 */
function layerColour(color) {
  if (typeof color === 'string' && Object.hasOwn(LAYER_COLORS, color)) return color;
  const [r, g, b] = rgbBytes(color);
  let best = null;
  let bestDistance = Infinity;
  for (const [name, hex] of Object.entries(LAYER_COLORS)) {
    const value = Number.parseInt(hex.slice(1), 16);
    const distance =
      ((value >> 16) - r) ** 2 + (((value >> 8) & 255) - g) ** 2 + ((value & 255) - b) ** 2;
    if (distance < bestDistance) {
      bestDistance = distance;
      best = name;
    }
  }
  return best;
}

/** The playback positions a figure instance appears in. */
function framesHolding(editor, uid) {
  const frames = [];
  editor.report.keyframes.forEach((frame, index) => {
    if (frame.objects.some(object => object.unique_id === uid)) frames.push(index);
  });
  return frames;
}

/** The playback ticks a figure instance is shown at. */
function ticksHolding(editor, uid, limit = 400) {
  const rows = editor.timeline;
  const ticks = [];
  const count = Math.min(rows.length, limit);
  const playhead = editor.tick;
  try {
    for (let position = 0; position < count; position += 1) {
      const frame = editor.seek(rows[position].start);
      if (frame.objects.some(object => object.unique_id === uid)) ticks.push(rows[position].start);
    }
  } finally {
    editor.seek(playhead);
  }
  return ticks;
}
