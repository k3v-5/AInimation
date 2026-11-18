import { AEExpressionValidator } from "./AEExpressionValidator.js";

export class AEExpressionBuilder {
  /**
   * Genera una expresión de wiggle estándar: wiggle(freq, amp)
   */
  public static wiggle(freq: number, amp: number, octaves?: number, ampMult?: number): string {
    if (octaves !== undefined && ampMult !== undefined) {
      return `wiggle(${freq}, ${amp}, ${octaves}, ${ampMult})`;
    }
    return `wiggle(${freq}, ${amp})`;
  }

  /**
   * Genera una expresión de bucle loopOut(type, numKeyframes)
   */
  public static loopOut(type: "cycle" | "pingpong" | "offset" | "continue" = "cycle", numKeyframes = 0): string {
    return `loopOut("${type}", ${numKeyframes})`;
  }

  /**
   * Genera una expresión de loopIn(type, numKeyframes)
   */
  public static loopIn(type: "cycle" | "pingpong" | "offset" | "continue" = "cycle", numKeyframes = 0): string {
    return `loopIn("${type}", ${numKeyframes})`;
  }

  /**
   * Genera una interpolación lineal de rango linear(t, inMin, inMax, outMin, outMax)
   */
  public static linear(
    timeVar = "time",
    inMin: number,
    inMax: number,
    outMin: number,
    outMax: number
  ): string {
    return `linear(${timeVar}, ${inMin}, ${inMax}, ${outMin}, ${outMax})`;
  }

  /**
   * Genera una interpolación suave ease(t, inMin, inMax, outMin, outMax)
   */
  public static ease(
    timeVar = "time",
    inMin: number,
    inMax: number,
    outMin: number,
    outMax: number
  ): string {
    return `ease(${timeVar}, ${inMin}, ${inMax}, ${outMin}, ${outMax})`;
  }

  /**
   * Genera una referencia a valor temporal con delay: thisComp.layer(layerName).transform.position.valueAtTime(time - delay)
   */
  public static valueAtTime(layerName: string, propertyPath = "transform.position", delaySeconds = 0.1): string {
    return `thisComp.layer("${layerName}").${propertyPath}.valueAtTime(time - ${delaySeconds})`;
  }

  /**
   * Genera una expresión de inercia y rebote físico determinista (Bounce/Inertia Decay)
   */
  public static inertiaBounce(amp = 0.05, freq = 4.0, decay = 2.0): string {
    return [
      "var n = 0;",
      "if (numKeys > 0) {",
      "  n = nearestKey(time).index;",
      "  if (key(n).time > time) n--;",
      "}",
      "if (n === 0) {",
      "  value;",
      "} else {",
      "  var t = time - key(n).time;",
      "  var amp = " + amp + ";",
      "  var freq = " + freq + ";",
      "  var decay = " + decay + ";",
      "  var v = velocityAtTime(key(n).time - thisComp.frameDuration/10);",
      "  value + v * amp * Math.sin(freq * t * 2 * Math.PI) / Math.exp(decay * t);",
      "}",
    ].join("\n");
  }

  /**
   * Genera una expresión de clamping
   */
  public static clamp(expr: string, min: number, max: number): string {
    return `clamp(${expr}, ${min}, ${max})`;
  }
}
