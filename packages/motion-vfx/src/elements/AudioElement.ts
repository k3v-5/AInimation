import { Property } from "../core/property.js";
import { Time } from "../core/types.js";
import { validateId, validateTime } from "../validation/validators.js";
import { BaseElement } from "./BaseElement.js";
import { BaseElementOptions, ElementType, EvaluatedAudioState } from "./types.js";

export interface AudioElementOptions extends BaseElementOptions {
  assetId: string;
  sourceStartTime?: Time;
  volume?: number;
}

/**
 * Elemento de audio con control de volumen animable (Property<number>) y mapeo de tiempo fuente.
 */
export class AudioElement extends BaseElement {
  public readonly type: ElementType = "audio";
  public assetId: string;
  public sourceStartTime: Time;
  public volume: Property<number>;

  constructor(options: AudioElementOptions) {
    super(options);
    this.assetId = validateId(options.assetId, "assetId");
    this.sourceStartTime = options.sourceStartTime !== undefined ? validateTime(options.sourceStartTime) : 0;
    this.volume = new Property<number>(options.volume ?? 1);
  }

  public getSourceTime(globalTime: Time): Time {
    const localTime = this.getLocalTime(globalTime);
    return this.sourceStartTime + localTime;
  }

  public clone(): AudioElement {
    const cloned = new AudioElement({
      name: `${this.name}_copy`,
      startTime: this.startTime,
      duration: this.duration,
      visible: this.visible,
      parentId: this.parentId,
      assetId: this.assetId,
      sourceStartTime: this.sourceStartTime,
      volume: this.volume.getValue(),
    });

    return cloned;
  }

  public evaluate(globalTime: Time): EvaluatedAudioState {
    const active = this.isActive(globalTime);
    const localTime = this.getLocalTime(globalTime);
    const sourceTime = this.getSourceTime(globalTime);
    const vol = Math.max(0, this.volume.evaluate(globalTime));

    return {
      id: this.id,
      name: this.name,
      type: "audio",
      active,
      localTime,
      visible: this.visible,
      assetId: this.assetId,
      sourceTime,
      volume: vol,
    };
  }
}
