import { Time } from "../core/types.js";
import { DuplicateLayerError, HierarchyCycleError, ValidationError } from "../errors/index.js";
import { EvaluatedTransform, Matrix2D } from "../transform/index.js";
import { validateId } from "../validation/validators.js";
import { BaseElement } from "./BaseElement.js";
import { BaseElementOptions, BaseElementState, ElementType, EvaluatedGroupState } from "./types.js";

export interface GroupElementOptions extends BaseElementOptions {
  children?: BaseElement[];
}

/**
 * Contenedor jerárquico de elementos para transformaciones y organizaciones compuestas.
 */
export class GroupElement extends BaseElement {
  public readonly type: ElementType = "group";
  private children: BaseElement[] = [];

  constructor(options: GroupElementOptions = {}) {
    super(options);
    if (options.children) {
      for (const child of options.children) {
        this.addChild(child);
      }
    }
  }

  /**
   * Agrega un elemento hijo al grupo, asignándole parentId y evitando ciclos y duplicados.
   */
  public addChild(element: BaseElement): void {
    if (!element || !(element instanceof BaseElement)) {
      throw new ValidationError("Group child must be an instance of BaseElement.");
    }

    if (element.id === this.id) {
      throw new HierarchyCycleError(`Cannot add group '${this.id}' as a child of itself.`);
    }

    if (this.children.some((c) => c.id === element.id)) {
      throw new DuplicateLayerError(element.id);
    }

    element.parentId = this.id;
    this.children.push(element);
  }

  /**
   * Elimina un elemento hijo del grupo por su ID.
   */
  public removeChild(id: string): boolean {
    const validId = validateId(id, "child.id");
    const index = this.children.findIndex((c) => c.id === validId);
    if (index === -1) {
      return false;
    }
    this.children[index].parentId = undefined;
    this.children.splice(index, 1);
    return true;
  }

  /**
   * Obtiene un elemento hijo directo por su ID.
   */
  public getChild(id: string): BaseElement | undefined {
    const validId = validateId(id, "child.id");
    return this.children.find((c) => c.id === validId);
  }

  /**
   * Retorna una copia de la lista de elementos hijos directos.
   */
  public getChildren(): BaseElement[] {
    return [...this.children];
  }

  public clone(): GroupElement {
    const cloned = new GroupElement({
      name: `${this.name}_copy`,
      startTime: this.startTime,
      duration: this.duration,
      visible: this.visible,
      parentId: this.parentId,
    });

    cloned.transform.position.setValue(this.transform.position.getValue());
    cloned.transform.scale.setValue(this.transform.scale.getValue());
    cloned.transform.rotation.setValue(this.transform.rotation.getValue());
    cloned.transform.opacity.setValue(this.transform.opacity.getValue());
    cloned.transform.anchorPoint.setValue(this.transform.anchorPoint.getValue());

    for (const child of this.children) {
      const clonedChild = child.clone();
      cloned.addChild(clonedChild);
    }

    return cloned;
  }

  public evaluate(globalTime: Time, parentTransform?: EvaluatedTransform): EvaluatedGroupState {
    const active = this.isActive(globalTime);
    const localTime = this.getLocalTime(globalTime);

    const groupTransformEval: EvaluatedTransform = parentTransform
      ? {
          matrix: Matrix2D.multiply(parentTransform.matrix, this.transform.evaluateLocal(globalTime)),
          opacity: parentTransform.opacity * this.transform.evaluateOpacity(globalTime),
        }
      : this.transform.evaluate(globalTime);

    const evaluatedChildren: BaseElementState[] = this.children.map((child) =>
      child.evaluate(globalTime, groupTransformEval)
    );

    return {
      id: this.id,
      name: this.name,
      type: "group",
      active,
      localTime,
      visible: this.visible,
      transform: groupTransformEval,
      children: evaluatedChildren,
    };
  }
}
