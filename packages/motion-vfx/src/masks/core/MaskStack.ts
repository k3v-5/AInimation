import { ValidationError } from "../../errors/index.js";
import { Mask, Matte } from "../types/index.js";
import { MatteGenerator } from "./MatteGenerator.js";

/**
 * Pila ordenada de máscaras con operaciones booleanas combinadas (Fase 5G).
 */
export class MaskStack {
  private _masks: Mask[] = [];

  constructor(masks: Mask[] = []) {
    for (const m of masks) {
      this.addMask(m);
    }
  }

  public get masks(): Mask[] {
    return [...this._masks];
  }

  public get size(): number {
    return this._masks.length;
  }

  public addMask(mask: Mask): this {
    if (!mask || !mask.id) {
      throw new ValidationError("Mask must have a valid id.");
    }
    this._masks.push({ ...mask });
    return this;
  }

  public removeMask(id: string): boolean {
    const idx = this._masks.findIndex((m) => m.id === id);
    if (idx !== -1) {
      this._masks.splice(idx, 1);
      return true;
    }
    return false;
  }

  public getMask(id: string): Mask | undefined {
    return this._masks.find((m) => m.id === id);
  }

  public evaluateMatte(width: number, height: number): Matte {
    return MatteGenerator.generateCompositeMatte(this._masks, width, height);
  }

  public toJSON(): Mask[] {
    return this._masks.map((m) => ({
      ...m,
      path: {
        ...m.path,
        points: m.path.points.map((p) => ({
          position: { ...p.position },
          inTangent: p.inTangent ? { ...p.inTangent } : undefined,
          outTangent: p.outTangent ? { ...p.outTangent } : undefined,
        })),
      },
    }));
  }

  public static fromJSON(masks: any[]): MaskStack {
    return new MaskStack(masks);
  }
}
