import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { HierarchyCycleError } from "../../errors/index.js";
import { Matrix2D } from "../../transform/Matrix2D.js";
import { Transform } from "../../transform/Transform.js";
import { TransformResolver } from "../../transform/TransformResolver.js";
import { Transformable } from "../../transform/types.js";

describe("Fase 2A — TransformResolver & Hierarchy Tests", () => {
  it("resolves world transform for parent and child with translation and scale", () => {
    const parent: Transformable = {
      id: "parent_node",
      transform: new Transform({ position: { x: 100, y: 100 }, scale: { x: 2, y: 2 } }),
    };

    const child: Transformable = {
      id: "child_node",
      transform: new Transform({ position: { x: 50, y: 0 } }),
      parent,
    };

    const worldMatrix = TransformResolver.resolveWorld(child, 0);
    const originWorld = Matrix2D.transformPoint(worldMatrix, { x: 0, y: 0 });

    // 100 + 2 * 50 = 200
    assert.strictEqual(originWorld.x, 200);
    assert.strictEqual(originWorld.y, 100);
  });

  it("resolves multi-level nested hierarchy: A -> B -> C -> Leaf", () => {
    const nodeA: Transformable = {
      id: "node_a",
      transform: new Transform({ position: { x: 100, y: 0 } }),
    };

    const nodeB: Transformable = {
      id: "node_b",
      transform: new Transform({ position: { x: 50, y: 0 } }),
      parent: nodeA,
    };

    const nodeC: Transformable = {
      id: "node_c",
      transform: new Transform({ position: { x: 25, y: 0 } }),
      parent: nodeB,
    };

    const leaf: Transformable = {
      id: "leaf_node",
      transform: new Transform({ position: { x: 10, y: 0 } }),
      parent: nodeC,
    };

    const worldMatrix = TransformResolver.resolveWorld(leaf, 0);
    const originWorld = Matrix2D.transformPoint(worldMatrix, { x: 0, y: 0 });

    // 100 + 50 + 25 + 10 = 185
    assert.strictEqual(originWorld.x, 185);
    assert.strictEqual(originWorld.y, 0);
  });

  it("compounds opacities hierarchically down the tree", () => {
    const parent: Transformable = {
      id: "parent_fade",
      transform: new Transform({ opacity: 0.5 }),
    };

    const child: Transformable = {
      id: "child_fade",
      transform: new Transform({ opacity: 0.5 }),
      parent,
    };

    const totalOpacity = TransformResolver.resolveOpacity(child, 0);
    assert.strictEqual(totalOpacity, 0.25);
  });

  it("DETECTS CYCLES in hierarchy and throws HierarchyCycleError", () => {
    const nodeA: any = {
      id: "node_a",
      transform: new Transform(),
    };

    const nodeB: any = {
      id: "node_b",
      transform: new Transform(),
      parent: nodeA,
    };

    // Crear ciclo intencional A -> B -> A
    nodeA.parent = nodeB;

    assert.throws(() => {
      TransformResolver.resolveWorld(nodeA, 0);
    }, HierarchyCycleError);
  });
});
