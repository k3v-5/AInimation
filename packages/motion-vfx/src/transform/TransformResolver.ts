import { Time } from "../core/types.js";
import { HierarchyCycleError } from "../errors/index.js";
import { Matrix2D } from "./Matrix2D.js";
import { Transform } from "./Transform.js";
import { Bounds, EvaluatedTransform, Transformable } from "./types.js";

/**
 * Resolver jerárquico de transformaciones espaciales y opacidades para elementos anidados.
 */
export class TransformResolver {
  /**
   * Resuelve la matriz local de un elemento en el tiempo `time`.
   */
  public static resolveLocal(transform: Transform, bounds: Bounds | undefined, time: Time): Matrix2D {
    return transform.evaluateLocal(time, bounds);
  }

  /**
   * Resuelve la matriz mundial completa de un elemento, recorriendo la cadena de padres hasta la raíz.
   * Incluye detección estricta de ciclos en la jerarquía.
   */
  public static resolveWorld(element: Transformable, time: Time): Matrix2D {
    const chain = this.getHierarchyChain(element);

    let worldMatrix = Matrix2D.identity();
    for (const node of chain) {
      const localMatrix = node.transform.evaluateLocal(time, node.bounds);
      worldMatrix = Matrix2D.multiply(worldMatrix, localMatrix);
    }

    return worldMatrix;
  }

  /**
   * Resuelve la opacidad compuesta del elemento multiplicando la opacidad de todos sus ancestros.
   */
  public static resolveOpacity(element: Transformable, time: Time): number {
    const chain = this.getHierarchyChain(element);

    let totalOpacity = 1.0;
    for (const node of chain) {
      totalOpacity *= node.transform.evaluateOpacity(time);
    }

    return Math.max(0, Math.min(1, totalOpacity));
  }

  /**
   * Resuelve el estado evaluado completo (matriz mundial y opacidad mundial).
   */
  public static resolveEvaluated(element: Transformable, time: Time): EvaluatedTransform {
    return {
      matrix: this.resolveWorld(element, time),
      opacity: this.resolveOpacity(element, time),
    };
  }

  /**
   * Obtiene la cadena de nodos desde la raíz hacia el elemento hoja (Root -> ... -> Parent -> Element).
   * Lanza HierarchyCycleError si se detecta un ciclo.
   */
  private static getHierarchyChain(element: Transformable): Transformable[] {
    const chain: Transformable[] = [];
    const visited = new Set<string>();

    let current: Transformable | undefined = element;
    while (current) {
      if (visited.has(current.id)) {
        const cycleIds = [...chain.map((n) => n.id), current.id].join(" -> ");
        throw new HierarchyCycleError(`Parenting cycle detected in hierarchy: ${cycleIds}`);
      }
      visited.add(current.id);
      chain.unshift(current); // Insertar al inicio para que el orden sea Root -> Element
      current = current.parent;
    }

    return chain;
  }
}
