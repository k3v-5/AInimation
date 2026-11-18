import { Time } from "../../core/types.js";
import { ValidationError } from "../../errors/index.js";
import { Mask, MaskPath, MaskPoint, RotoMask, Vec2 } from "../types/index.js";

/**
 * Interpolador temporal de rotoscopia para máscaras animadas (Fase 5G).
 */
export class MaskInterpolator {
  public static interpolateVec2(a: Vec2, b: Vec2, t: number): Vec2 {
    return {
      x: a.x + (b.x - a.x) * t,
      y: a.y + (b.y - a.y) * t,
    };
  }

  public static interpolatePoint(p1: MaskPoint, p2: MaskPoint, progress: number): MaskPoint {
    const pt: MaskPoint = {
      position: this.interpolateVec2(p1.position, p2.position, progress),
    };

    if (p1.inTangent && p2.inTangent) {
      pt.inTangent = this.interpolateVec2(p1.inTangent, p2.inTangent, progress);
    }
    if (p1.outTangent && p2.outTangent) {
      pt.outTangent = this.interpolateVec2(p1.outTangent, p2.outTangent, progress);
    }

    return pt;
  }

  public static interpolatePath(pathA: MaskPath, pathB: MaskPath, progress: number): MaskPath {
    if (pathA.points.length !== pathB.points.length) {
      throw new ValidationError(
        `INCOMPATIBLE_MASK_PATHS: Cannot interpolate paths with different point counts (${pathA.points.length} vs ${pathB.points.length}).`
      );
    }

    const t = Math.max(0, Math.min(1, progress));
    const points: MaskPoint[] = [];

    for (let i = 0; i < pathA.points.length; i++) {
      points.push(this.interpolatePoint(pathA.points[i], pathB.points[i], t));
    }

    return {
      closed: pathA.closed && pathB.closed,
      points,
    };
  }

  public static evaluateRotoMask(roto: RotoMask, time: Time): Mask {
    if (roto.frames.length === 0) {
      throw new ValidationError("RotoMask must have at least one frame.");
    }

    // Ordenar frames por tiempo
    const sorted = [...roto.frames].sort((a, b) => a.time - b.time);

    let evaluatedPath: MaskPath;

    if (time <= sorted[0].time) {
      evaluatedPath = sorted[0].path;
    } else if (time >= sorted[sorted.length - 1].time) {
      evaluatedPath = sorted[sorted.length - 1].path;
    } else {
      // Buscar el intervalo [f1, f2]
      let f1 = sorted[0];
      let f2 = sorted[1];
      for (let i = 0; i < sorted.length - 1; i++) {
        if (time >= sorted[i].time && time <= sorted[i + 1].time) {
          f1 = sorted[i];
          f2 = sorted[i + 1];
          break;
        }
      }

      const duration = f2.time - f1.time;
      const progress = duration > 0 ? (time - f1.time) / duration : 0;
      evaluatedPath = this.interpolatePath(f1.path, f2.path, progress);
    }

    return {
      id: roto.id,
      type: roto.type,
      mode: roto.mode,
      feather: roto.feather,
      expansion: roto.expansion,
      opacity: roto.opacity,
      path: evaluatedPath,
    };
  }
}
