import { BasicAnimation } from "../../animation/BasicAnimation.js";
import { ParallelAnimation } from "../../animation/ParallelAnimation.js";
import { fadeIn } from "../../animation/primitives/fade.js";
import { TextElement } from "../../elements/TextElement.js";
import { TextSegmenter } from "../segmenter/TextSegmenter.js";

export interface TypewriterOptions {
  duration?: number;
  charDuration?: number;
  delay?: number;
  cursor?: boolean;
}

/**
 * Genera una animación de máquina de escribir (typewriter) revelando caracteres secuencialmente.
 */
export function typewriter(
  target: TextElement | { id: string; text?: string | { getValue(): string } },
  options: TypewriterOptions = {}
): ParallelAnimation {
  const elementId = target.id;
  let rawText = "";
  if ("text" in target && target.text) {
    if (typeof target.text === "string") {
      rawText = target.text;
    } else if (typeof (target.text as any).getValue === "function") {
      rawText = (target.text as any).getValue();
    }
  }
  const layout = TextSegmenter.segment(rawText);
  const totalChars = layout.characters.length;

  const totalDuration = options.duration ?? (options.charDuration ? options.charDuration * totalChars : totalChars * 0.05);
  const stepDuration = totalChars > 0 ? totalDuration / totalChars : 0.05;
  const baseDelay = options.delay ?? 0;

  const children: BasicAnimation[] = [];

  layout.characters.forEach((char, index) => {
    const charTarget = { id: `${elementId}:char:${char.index}` };
    const charAnim = fadeIn(charTarget as any, {
      duration: 0.001, // Aparición instantánea escalonada
      delay: baseDelay + index * stepDuration,
    });
    children.push(charAnim);
  });

  return new ParallelAnimation({
    id: `typewriter_${elementId}`,
    delay: 0,
    children,
  });
}
