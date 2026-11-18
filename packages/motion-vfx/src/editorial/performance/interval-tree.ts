/**
 * REQ-039: Augmented AVL Interval Tree & Temporal Indexer
 * Proporciona consultas de colisión temporal en O(log N + K) frente a O(N) de búsqueda lineal.
 */

export interface IntervalItem<T = unknown> {
  id: string;
  low: number;
  high: number;
  data?: T;
}

class IntervalNode<T> {
  public id: string;
  public low: number;
  public high: number;
  public maxHigh: number;
  public height: number;
  public data?: T;
  public left: IntervalNode<T> | null = null;
  public right: IntervalNode<T> | null = null;

  constructor(id: string, low: number, high: number, data?: T) {
    this.id = id;
    this.low = low;
    this.high = high;
    this.maxHigh = high;
    this.height = 1;
    this.data = data;
  }
}

export class IntervalTree<T = unknown> {
  private root: IntervalNode<T> | null = null;
  private count = 0;
  private readonly idToNode = new Map<string, { low: number; high: number }>();

  public size(): number {
    return this.count;
  }

  public clear(): void {
    this.root = null;
    this.count = 0;
    this.idToNode.clear();
  }

  private height(node: IntervalNode<T> | null): number {
    return node ? node.height : 0;
  }

  private max(a: number, b: number, c: number): number {
    return Math.max(a, Math.max(b, c));
  }

  private updateMax(node: IntervalNode<T>): void {
    let max = node.high;
    if (node.left) max = Math.max(max, node.left.maxHigh);
    if (node.right) max = Math.max(max, node.right.maxHigh);
    node.maxHigh = max;
    node.height = 1 + Math.max(this.height(node.left), this.height(node.right));
  }

  private getBalance(node: IntervalNode<T> | null): number {
    return node ? this.height(node.left) - this.height(node.right) : 0;
  }

  private rotateRight(y: IntervalNode<T>): IntervalNode<T> {
    const x = y.left!;
    const t2 = x.right;

    x.right = y;
    y.left = t2;

    this.updateMax(y);
    this.updateMax(x);

    return x;
  }

  private rotateLeft(x: IntervalNode<T>): IntervalNode<T> {
    const y = x.right!;
    const t2 = y.left;

    y.left = x;
    x.right = t2;

    this.updateMax(x);
    this.updateMax(y);

    return y;
  }

  /**
   * Inserta un intervalo [low, high] en O(log N)
   */
  public insert(id: string, low: number, high: number, data?: T): void {
    if (low > high) {
      const tmp = low;
      low = high;
      high = tmp;
    }

    if (this.idToNode.has(id)) {
      this.remove(id);
    }

    this.root = this.insertRec(this.root, id, low, high, data);
    this.count++;
    this.idToNode.set(id, { low, high });
  }

  private insertRec(
    node: IntervalNode<T> | null,
    id: string,
    low: number,
    high: number,
    data?: T
  ): IntervalNode<T> {
    if (!node) {
      return new IntervalNode(id, low, high, data);
    }

    if (low < node.low || (low === node.low && id < node.id)) {
      node.left = this.insertRec(node.left, id, low, high, data);
    } else {
      node.right = this.insertRec(node.right, id, low, high, data);
    }

    this.updateMax(node);

    const balance = this.getBalance(node);

    // Left Left
    if (balance > 1 && (low < node.left!.low || (low === node.left!.low && id < node.left!.id))) {
      return this.rotateRight(node);
    }

    // Right Right
    if (balance < -1 && (low > node.right!.low || (low === node.right!.low && id > node.right!.id))) {
      return this.rotateLeft(node);
    }

    // Left Right
    if (balance > 1 && (low > node.left!.low || (low === node.left!.low && id > node.left!.id))) {
      node.left = this.rotateLeft(node.left!);
      return this.rotateRight(node);
    }

    // Right Left
    if (balance < -1 && (low < node.right!.low || (low === node.right!.low && id < node.right!.id))) {
      node.right = this.rotateRight(node.right!);
      return this.rotateLeft(node);
    }

    return node;
  }

  /**
   * Elimina un intervalo por su ID en O(log N)
   */
  public remove(id: string): boolean {
    const existing = this.idToNode.get(id);
    if (!existing) return false;

    let removed = false;
    this.root = this.removeRec(this.root, id, existing.low, () => {
      removed = true;
    });

    if (removed) {
      this.count--;
      this.idToNode.delete(id);
    }
    return removed;
  }

  private removeRec(
    node: IntervalNode<T> | null,
    id: string,
    low: number,
    onRemoved: () => void
  ): IntervalNode<T> | null {
    if (!node) return null;

    if (low < node.low || (low === node.low && id < node.id)) {
      node.left = this.removeRec(node.left, id, low, onRemoved);
    } else if (low > node.low || (low === node.low && id > node.id)) {
      node.right = this.removeRec(node.right, id, low, onRemoved);
    } else {
      // Encontrado
      onRemoved();
      if (!node.left || !node.right) {
        node = node.left ? node.left : node.right;
      } else {
        const temp = this.minValueNode(node.right);
        node.id = temp.id;
        node.low = temp.low;
        node.high = temp.high;
        node.data = temp.data;
        node.right = this.removeRec(node.right, temp.id, temp.low, () => {});
      }
    }

    if (!node) return null;

    this.updateMax(node);

    const balance = this.getBalance(node);

    // Balance rotations
    if (balance > 1 && this.getBalance(node.left) >= 0) {
      return this.rotateRight(node);
    }
    if (balance > 1 && this.getBalance(node.left) < 0) {
      node.left = this.rotateLeft(node.left!);
      return this.rotateRight(node);
    }
    if (balance < -1 && this.getBalance(node.right) <= 0) {
      return this.rotateLeft(node);
    }
    if (balance < -1 && this.getBalance(node.right) > 0) {
      node.right = this.rotateRight(node.right!);
      return this.rotateLeft(node);
    }

    return node;
  }

  private minValueNode(node: IntervalNode<T>): IntervalNode<T> {
    let current = node;
    while (current.left) {
      current = current.left;
    }
    return current;
  }

  /**
   * Consulta de solapamiento en O(log N + K): encuentra todos los intervalos que solapan con [low, high]
   */
  public overlapQuery(low: number, high: number): IntervalItem<T>[] {
    const results: IntervalItem<T>[] = [];
    if (low > high) {
      const tmp = low;
      low = high;
      high = tmp;
    }
    this.searchOverlap(this.root, low, high, results);
    return results.sort((a, b) => a.low - b.low || a.high - b.high || a.id.localeCompare(b.id));
  }

  private searchOverlap(
    node: IntervalNode<T> | null,
    low: number,
    high: number,
    results: IntervalItem<T>[]
  ): void {
    if (!node) return;

    // Si maxHigh es menor que low, ningún nodo en este subárbol puede solapar
    if (node.maxHigh < low) return;

    // Explorar subárbol izquierdo si puede contener solapamiento
    if (node.left && node.left.maxHigh >= low) {
      this.searchOverlap(node.left, low, high, results);
    }

    // Comprobar si el nodo actual solapa: [node.low, node.high] y [low, high]
    // Solapan si node.low <= high && node.high >= low
    if (node.low <= high && node.high >= low) {
      results.push({
        id: node.id,
        low: node.low,
        high: node.high,
        data: node.data,
      });
    }

    // Explorar subárbol derecho si el inicio del nodo es menor o igual a high
    if (node.low <= high && node.right) {
      this.searchOverlap(node.right, low, high, results);
    }
  }

  /**
   * Consulta de rango en O(log N + K): encuentra intervalos contenidos totalmente dentro de [low, high]
   */
  public rangeQuery(low: number, high: number): IntervalItem<T>[] {
    return this.overlapQuery(low, high).filter((item) => item.low >= low && item.high <= high);
  }

  /**
   * Consulta puntual en O(log N + K): encuentra todos los intervalos que cubren un timestamp exacto
   */
  public pointQuery(point: number): IntervalItem<T>[] {
    return this.overlapQuery(point, point);
  }

  /**
   * Fallback lineal O(N) para verificación comparativa de integridad y golden tests
   */
  public linearFallbackQuery(low: number, high: number): IntervalItem<T>[] {
    const allItems: IntervalItem<T>[] = [];
    this.traverseInOrder(this.root, allItems);
    return allItems
      .filter((item) => item.low <= high && item.high >= low)
      .sort((a, b) => a.low - b.low || a.high - b.high || a.id.localeCompare(b.id));
  }

  private traverseInOrder(node: IntervalNode<T> | null, list: IntervalItem<T>[]): void {
    if (!node) return;
    this.traverseInOrder(node.left, list);
    list.push({ id: node.id, low: node.low, high: node.high, data: node.data });
    this.traverseInOrder(node.right, list);
  }
}
