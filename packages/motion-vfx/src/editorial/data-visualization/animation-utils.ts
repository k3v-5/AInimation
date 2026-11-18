import {
  EasingType,
  KeyframedProperty,
  Keyframe,
  NumberFormat,
} from "./types.js";
import { VisualizationCompilationError } from "./errors.js";

/**
 * REQ-025 §10, §16, §17, §23, §35, §45, §46, §47: Utilidades deterministas de animación y formato numérico.
 */

export function validateKeyframeMonotonicity(keyframes: Keyframe[], totalDuration: number): void {
  let prevTime = -1;
  for (const kf of keyframes) {
    if (kf.timeSeconds < 0 || kf.timeSeconds > totalDuration + 1e-4) {
      throw new VisualizationCompilationError(
        `Keyframe en t=${kf.timeSeconds}s excede la duración total de ${totalDuration}s.`
      );
    }
    if (kf.timeSeconds < prevTime) {
      throw new VisualizationCompilationError(
        `Keyframes no están ordenados cronológicamente: ${kf.timeSeconds}s < ${prevTime}s.`
      );
    }
    prevTime = kf.timeSeconds;
  }
}

export function createGrowAnimation(
  property: string,
  targetValue: number,
  startTime: number,
  duration: number,
  easing: EasingType = "EASE_OUT"
): KeyframedProperty {
  const kfs: Keyframe[] = [
    { timeSeconds: Number(startTime.toFixed(4)), value: 0, easing },
    { timeSeconds: Number((startTime + duration).toFixed(4)), value: targetValue, easing },
  ];
  return { property, keyframes: kfs };
}

export function createCounterAnimation(
  targetValue: number,
  startTime: number,
  duration: number,
  easing: EasingType = "EASE_OUT"
): KeyframedProperty {
  const kfs: Keyframe[] = [
    { timeSeconds: Number(startTime.toFixed(4)), value: 0, easing },
    { timeSeconds: Number((startTime + duration).toFixed(4)), value: targetValue, easing },
  ];
  return { property: "counterValue", keyframes: kfs };
}

export function createStrokeWriteOnAnimation(
  startTime: number,
  duration: number,
  easing: EasingType = "EASE_OUT"
): KeyframedProperty {
  const kfs: Keyframe[] = [
    { timeSeconds: Number(startTime.toFixed(4)), value: 0.0, easing },
    { timeSeconds: Number((startTime + duration).toFixed(4)), value: 1.0, easing },
  ];
  return { property: "trimPathEnd", keyframes: kfs };
}

export function createOpacityEntranceExit(
  startTime: number,
  entranceDur: number,
  exitDur: number,
  totalDur: number
): KeyframedProperty {
  const t0 = Math.max(0, startTime);
  const t1 = Math.min(totalDur, t0 + entranceDur);
  const t3 = totalDur;
  const t2 = Math.max(t1, t3 - exitDur);

  const keyframes: Keyframe[] = [
    { timeSeconds: Number(t0.toFixed(4)), value: 0, easing: "EASE_OUT" },
    { timeSeconds: Number(t1.toFixed(4)), value: 1, easing: "EASE_OUT" },
    { timeSeconds: Number(t2.toFixed(4)), value: 1, easing: "EASE_IN" },
    { timeSeconds: Number(t3.toFixed(4)), value: 0, easing: "EASE_IN" },
  ];

  return { property: "opacity", keyframes };
}

export function formatNumberDeterministic(
  value: number,
  format: NumberFormat = "DECIMAL",
  decimals: number = 2,
  prefix: string = "",
  suffix: string = ""
): string {
  if (!Number.isFinite(value)) return "0";

  let formattedNum = "";

  switch (format) {
    case "INTEGER": {
      const rounded = Math.round(value);
      formattedNum = addThousandsSeparators(rounded.toString());
      break;
    }
    case "PERCENTAGE": {
      const dec = Math.max(0, decimals);
      const fixed = value.toFixed(dec);
      const numPart = addThousandsSeparators(fixed);
      formattedNum = suffix && suffix.startsWith("%") ? numPart : `${numPart}%`;
      break;
    }
    case "CURRENCY": {
      const dec = Math.max(0, decimals);
      const fixed = value.toFixed(dec);
      const numPart = addThousandsSeparators(fixed);
      formattedNum = prefix && prefix.includes("$") ? numPart : `$${numPart}`;
      break;
    }
    case "DECIMAL":
    case "CUSTOM":
    default: {
      const dec = Math.max(0, decimals);
      const fixed = value.toFixed(dec);
      formattedNum = addThousandsSeparators(fixed);
      break;
    }
  }

  return `${prefix}${formattedNum}${suffix}`;
}

function addThousandsSeparators(numStr: string): string {
  const parts = numStr.split(".");
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return parts.join(".");
}
