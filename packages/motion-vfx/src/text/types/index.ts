import { AnimationNode } from "../../animation/AnimationNode.js";
import { BaseElement } from "../../elements/BaseElement.js";
import { TextElement } from "../../elements/TextElement.js";

export type TextScope = "element" | "line" | "word" | "character";

export type TextOrder = "forward" | "reverse" | "random" | "center" | "edges";

export interface TextCharacterToken {
  index: number;
  grapheme: string;
  isWhitespace: boolean;
  wordIndex: number;
  lineIndex: number;
  start: number;
  end: number;
}

export interface TextWordToken {
  index: number;
  text: string;
  characterIndices: number[];
  lineIndex: number;
  start: number;
  end: number;
}

export interface TextLineToken {
  index: number;
  text: string;
  wordIndices: number[];
  characterIndices: number[];
}

export interface TextLayoutData {
  rawText: string;
  characters: TextCharacterToken[];
  words: TextWordToken[];
  lines: TextLineToken[];
}

export interface TextStaggerConfig {
  delay?: number;
  wordDelay?: number;
  characterDelay?: number;
}

export interface TextSelectorConfig {
  scope: TextScope;
  order?: TextOrder;
  range?: {
    start?: number;
    end?: number;
  };
  seed?: number;
  excludeWhitespace?: boolean;
}

export interface SelectedTextTarget {
  targetId: string;
  elementId: string;
  scope: TextScope;
  index: number;
  total: number;
  delay: number;
  tokenText: string;
}

export type TextAnimationFactory = (target: { id: string }, options?: Record<string, unknown>) => AnimationNode;

export interface TextAnimationOptions {
  scope?: TextScope;
  order?: TextOrder;
  range?: { start?: number; end?: number };
  seed?: number;
  stagger?: TextStaggerConfig | number;
  animation: TextAnimationFactory | AnimationNode | Record<string, unknown>;
  id?: string;
  delay?: number;
  priority?: number;
}
