import { StutterFreezeSpec, StutterFreezeSpecSchema, TimeRemapKeyframe } from "./temporal-types.js";

/**
 * Motor de micro-congelamientos rítmicos percusivos (Stutter Freeze).
 */
export class StutterFreezeEngine {
  /**
   * Modifica una secuencia de keyframes de Time Remap inyectando una meseta de congelamiento temporal.
   */
  public static injectFreezeIntoKeyframes(
    keyframes: TimeRemapKeyframe[],
    specInput: StutterFreezeSpec
  ): TimeRemapKeyframe[] {
    const spec = StutterFreezeSpecSchema.parse(specInput);
    const { triggerTimeSeconds, freezeDurationSeconds, postResumeSpeedMultiplier } = spec;

    const result: TimeRemapKeyframe[] = [];
    let freezeValue: number | null = null;

    for (const kf of keyframes) {
      if (kf.timelineSeconds <= triggerTimeSeconds) {
        freezeValue = kf.sourceSeconds;
        result.push(kf);
      } else if (kf.timelineSeconds <= triggerTimeSeconds + freezeDurationSeconds) {
        // En el intervalo de freeze, el valor fuente permanece estático en el valor de disparo
        result.push({
          timelineSeconds: kf.timelineSeconds,
          sourceSeconds: freezeValue ?? kf.sourceSeconds,
        });
      } else {
        // Reanudación con multiplicador
        const elapsedSinceFreeze = kf.timelineSeconds - (triggerTimeSeconds + freezeDurationSeconds);
        const resumedSourceTime = (freezeValue ?? 0) + elapsedSinceFreeze * postResumeSpeedMultiplier;
        result.push({
          timelineSeconds: kf.timelineSeconds,
          sourceSeconds: Number(resumedSourceTime.toFixed(4)),
        });
      }
    }

    return result;
  }
}
