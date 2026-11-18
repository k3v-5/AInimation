import { Property } from "../core/property.js";
import { Color, Time } from "../core/types.js";
import { EvaluatedTransform } from "../transform/index.js";
import { BaseElement } from "./BaseElement.js";
import { BaseElementOptions, ElementType, EvaluatedTextState, TextStyle } from "./types.js";

export interface TextElementOptions extends BaseElementOptions {
  text?: string;
  style?: Partial<TextStyle>;
}

export const DEFAULT_TEXT_STYLE: TextStyle = {
  fontFamily: "Inter",
  fontSize: 48,
  fontWeight: 400,
  color: { r: 1, g: 1, b: 1, a: 1 },
  lineHeight: 1.2,
  letterSpacing: 0,
  textAlign: "center",
};

/**
 * Elemento descriptivo de texto y tipografía para Motion Graphics.
 */
export class TextElement extends BaseElement {
  public readonly type: ElementType = "text";
  public text: Property<string>;
  public style: TextStyle;

  constructor(options: TextElementOptions = {}) {
    super(options);
    this.text = new Property<string>(options.text ?? "Text");
    this.style = {
      ...DEFAULT_TEXT_STYLE,
      ...options.style,
      color: options.style?.color ? { ...options.style.color } : { ...DEFAULT_TEXT_STYLE.color },
    };
  }

  public clone(): TextElement {
    const cloned = new TextElement({
      name: `${this.name}_copy`,
      startTime: this.startTime,
      duration: this.duration,
      visible: this.visible,
      parentId: this.parentId,
      text: this.text.getValue(),
      style: {
        ...this.style,
        color: { ...this.style.color },
      },
    });

    // Clonar transform
    cloned.transform.position.setValue(this.transform.position.getValue());
    cloned.transform.scale.setValue(this.transform.scale.getValue());
    cloned.transform.rotation.setValue(this.transform.rotation.getValue());
    cloned.transform.opacity.setValue(this.transform.opacity.getValue());
    cloned.transform.anchorPoint.setValue(this.transform.anchorPoint.getValue());

    return cloned;
  }

  public evaluate(globalTime: Time, parentTransform?: EvaluatedTransform): EvaluatedTextState {
    const active = this.isActive(globalTime);
    const localTime = this.getLocalTime(globalTime);
    const textVal = this.text.evaluate(globalTime);

    // Calcular transform con parent
    const transformEval = parentTransform
      ? {
          matrix: import_Matrix2D_multiply(parentTransform.matrix, this.transform.evaluateLocal(globalTime)),
          opacity: parentTransform.opacity * this.transform.evaluateOpacity(globalTime),
        }
      : this.transform.evaluate(globalTime);

    return {
      id: this.id,
      name: this.name,
      type: "text",
      active,
      localTime,
      visible: this.visible,
      text: textVal,
      style: {
        ...this.style,
        color: { ...this.style.color },
      },
      transform: transformEval,
    };
  }
}

function import_Matrix2D_multiply(a: import("../transform/index.js").Matrix2D, b: import("../transform/index.js").Matrix2D) {
  return {
    a: a.a * b.a + a.c * b.b,
    b: a.b * b.a + a.d * b.b,
    c: a.a * b.c + a.c * b.d,
    d: a.b * b.c + a.d * b.d,
    tx: a.a * b.tx + a.c * b.ty + a.tx,
    ty: a.b * b.tx + a.d * b.ty + a.ty,
  };
}
