import { Composition } from "../core/composition.js";
import { Time } from "../core/types.js";
import { EvaluatedTransform, Matrix2D } from "../transform/index.js";
import { BaseElement } from "./BaseElement.js";
import { BaseElementOptions, BaseElementState, ElementType } from "./types.js";

export interface CompositionElementOptions extends BaseElementOptions {
  composition: Composition;
}

export interface EvaluatedCompositionElementState extends BaseElementState {
  type: "group"; // Se evalúa de manera análoga a un grupo precompuesto
  compositionId: string;
  elements: BaseElementState[];
}

/**
 * Elemento de Precomposición / Escena Anidada (Fase 5C).
 * Permite renderizar una composición entera como una única capa en el Scene Graph,
 * heredando transformaciones, opacidad y efectos aplicados al contenedor.
 */
export class CompositionElement extends BaseElement {
  public readonly type: ElementType = "group";
  public composition: Composition;

  constructor(options: CompositionElementOptions) {
    super({
      ...options,
      duration: options.duration ?? options.composition.duration,
    });
    this.composition = options.composition;
  }

  public clone(): CompositionElement {
    const cloned = new CompositionElement({
      name: `${this.name}_copy`,
      startTime: this.startTime,
      duration: this.duration,
      visible: this.visible,
      parentId: this.parentId,
      composition: this.composition,
    });

    cloned.transform.position.setValue(this.transform.position.getValue());
    cloned.transform.scale.setValue(this.transform.scale.getValue());
    cloned.transform.rotation.setValue(this.transform.rotation.getValue());
    cloned.transform.opacity.setValue(this.transform.opacity.getValue());
    cloned.transform.anchorPoint.setValue(this.transform.anchorPoint.getValue());

    return cloned;
  }

  public evaluate(globalTime: Time, parentTransform?: EvaluatedTransform): EvaluatedCompositionElementState {
    const active = this.isActive(globalTime);
    const localTime = this.getLocalTime(globalTime);

    const worldTransform = parentTransform
      ? {
          matrix: Matrix2D.multiply(parentTransform.matrix, this.transform.evaluateLocal(globalTime)),
          opacity: parentTransform.opacity * this.transform.evaluateOpacity(globalTime),
        }
      : this.transform.evaluate(globalTime);

    // Evaluar los elementos internos con el worldTransform del contenedor
    const innerElements = this.composition.getElements();
    const evaluatedInner = innerElements.map((el) => el.evaluate(localTime, worldTransform));

    return {
      id: this.id,
      name: this.name,
      type: "group",
      active,
      localTime,
      visible: this.visible,
      transform: worldTransform,
      compositionId: this.composition.id,
      elements: evaluatedInner,
    };
  }
}
