/**
 * Shared building blocks for the tool layer.
 *
 * Every tool answers the same way: a short, readable summary in the text
 * content and the full data in `structuredContent`, so a client that shows
 * only text still gets a useful answer and a client that reads structure
 * gets the data without parsing prose.
 */
import { ToolError } from '../errors.js';

/**
 * The project a call works on: the named one, or the active one.
 *
 * Using a project makes it the active one, so a short conversation never has
 * to repeat an identifier.
 */
export function project(store, input) {
  const found = store.require(input?.project);
  store.activate(found.id);
  return found;
}

/**
 * The stored pose a request names.
 *
 * A stored pose is one entry in the project's pose list. It is what the
 * keyframe tools address, because they add, remove and retime poses.
 */
export function storedIndex(editor, input) {
  if (input?.frame !== undefined && input?.frame !== null) {
    const index = Math.trunc(input.frame);
    if (!Number.isInteger(index) || index < 0 || index >= editor.report.keyframes.length) {
      throw new ToolError(
        `There is no keyframe ${index}. The project has ${editor.report.keyframes.length} keyframes ` +
          `(0 to ${editor.report.keyframes.length - 1}).`,
        { code: 'bad_frame' },
      );
    }
    return index;
  }
  return nativeIndex(editor, positionOf(editor, editor.frameIndex) ?? 0);
}

/**
 * The playback position a request names.
 *
 * A position is a place on the timeline the playhead moves through, and it is
 * what the pose and figure tools address, because they act on what the
 * animation shows. On a project with one keyframe per moment a position is
 * also the number of the stored pose it shows.
 */
export function keyframeIndex(editor, input) {
  if (input?.frame !== undefined && input?.frame !== null) {
    const position = Math.trunc(input.frame);
    if (!Number.isInteger(position) || position < 0 || position >= editor.timeline.length) {
      throw new ToolError(
        `There is no keyframe ${position}. The animation has ${editor.timeline.length} keyframes ` +
          `(0 to ${editor.timeline.length - 1}).`,
        { code: 'bad_frame' },
      );
    }
    return position;
  }
  if (input?.tick !== undefined && input?.tick !== null) {
    const tick = Math.trunc(input.tick);
    if (!Number.isInteger(tick) || tick < 0 || tick >= Math.max(1, editor.totalTicks)) {
      throw new ToolError(`Tick ${tick} is outside the animation (0 to ${Math.max(0, editor.totalTicks - 1)}).`, {
        code: 'bad_tick',
      });
    }
    return positionAtTick(editor, tick);
  }
  // The playhead's tick is the one thing that always names a place on the
  // timeline, whether the editor last moved it by a tick or by a keyframe.
  return positionAtTick(editor, editor.tick);
}

/** The position the timeline is at for a tick. */
export function positionAtTick(editor, tick) {
  let position = 0;
  editor.timeline.forEach((row, index) => {
    if (row.start <= tick) position = index;
  });
  return position;
}

/** The stored pose a playback position shows. */
export function nativeIndex(editor, position) {
  return editor.timeline[position]?.index ?? position;
}

/** The stored poses a set of playback positions shows. */
export function nativeIndices(editor, positions) {
  return positions.map(position => nativeIndex(editor, position));
}

/** The playback position that shows a stored pose. */
export function positionOf(editor, stored) {
  const position = editor.timeline.findIndex(entry => entry.index === stored);
  return position < 0 ? null : position;
}

/**
 * The range a command that works across frames should act on.
 *
 * A project with one keyframe per moment takes the stored poses. A project
 * with an advanced timeline takes the ticks the playback reaches, because that
 * is what its sheet holds.
 */
export function rangeOptions(editor, positions) {
  if (editor.report._styk?.layerSheet) {
    return {
      ticks: positions.map(position => editor.timeline[position]?.start).filter(tick => tick !== undefined),
    };
  }
  return { indices: nativeIndices(editor, positions) };
}

/** The playback tick a position starts at. */
export function keyframeTick(editor, position) {
  return editor.timeline[position]?.start ?? 0;
}

/** Move the playhead onto a position. */
export function goToKeyframe(editor, position) {
  editor.seek(keyframeTick(editor, position));
  return position;
}

/**
 * Select a figure instance and return its object.
 *
 * `uid` is the instance identity. `definitionId` picks a figure type when
 * the caller means the definition rather than an instance.
 */
export function selectObject(editor, uid, { required = true } = {}) {
  const frame = editor.selectionFrame ?? editor.frame;
  const object = frame.objects.find(entry => entry.unique_id === Number(uid));
  if (!object) {
    if (!required) return null;
    const present = frame.objects.map(entry => entry.unique_id);
    throw new ToolError(
      `No figure with the id ${uid} is in the current keyframe. Figures here: ${present.length ? present.join(', ') : 'none'}.`,
      { code: 'unknown_figure' },
    );
  }
  editor.select(object.unique_id);
  return object;
}

/** The segment index of a handle id, or null. */
export function segmentIndex(figure, handleId) {
  if (!figure) return null;
  const index = figure.segments.findIndex(segment => segment.segment_id === Number(handleId));
  return index < 0 ? null : index;
}

/** Select a joint by handle id (the native segment identity). */
export function selectJoint(editor, handleId) {
  const figure = editor.figure;
  const index = segmentIndex(figure, handleId);
  if (index === null) {
    const handles = figure?.segments?.map(segment => segment.segment_id) ?? [];
    throw new ToolError(
      `That figure has no joint with the handle id ${handleId}. Its handles: ${handles.join(', ') || 'none'}.`,
      { code: 'unknown_joint' },
    );
  }
  editor.select(editor.selectedUid, index);
  return index;
}

/** A number of degrees to radians. */
export const degrees = value => (value * Math.PI) / 180;

/** Turn `#rrggbb` or `[r,g,b]` into three RGB bytes. */
export function rgbBytes(color) {
  if (Array.isArray(color)) {
    if (color.length !== 3 || color.some(value => !Number.isInteger(value) || value < 0 || value > 255)) {
      throw new ToolError('An RGB colour needs three whole bytes between 0 and 255.', { code: 'bad_color' });
    }
    return [...color];
  }
  if (typeof color === 'string') {
    const hex = color.trim().replace(/^#/, '');
    if (!/^[0-9a-fA-F]{6}$/.test(hex)) {
      throw new ToolError(`"${color}" is not a #rrggbb colour.`, { code: 'bad_color' });
    }
    const value = Number.parseInt(hex, 16);
    return [(value >> 16) & 0xff, (value >> 8) & 0xff, value & 0xff];
  }
  throw new ToolError('Give a colour as "#rrggbb" or as three RGB bytes.', { code: 'bad_color' });
}

/** Build a tool result from data and a short human summary. */
export function result(summary, data) {
  return {
    content: [{ type: 'text', text: summary }],
    structuredContent: data,
  };
}

export { ToolError };
