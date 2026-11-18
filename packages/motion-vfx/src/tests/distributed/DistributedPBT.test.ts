import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { TaskDAG } from "../../distributed/tasks/TaskDAG.js";
import { createTaskDefinition } from "../../distributed/tasks/TaskDefinition.js";
import { ThreeWayMergeArbiter } from "../../distributed/swarm/ThreeWayMergeArbiter.js";
import { createAgentProposal } from "../../distributed/swarm/AgentProposal.js";

describe("Fase 24 — Capa 6: Property-Based Testing (fast-check) Suite", () => {
  it("PBT: TaskDAG preserves topological invariants for any valid DAG with random task IDs", () => {
    fc.assert(
      fc.property(
        fc.array(fc.string({ minLength: 1, maxLength: 10 }), { minLength: 2, maxLength: 20 }),
        (rawIds) => {
          const uniqueIds = Array.from(new Set(rawIds)).map((id, i) => `task_${i}_${id.replace(/[^a-zA-Z0-9]/g, "")}`);
          if (uniqueIds.length < 2) return true;

          const dag = new TaskDAG();
          for (let i = 0; i < uniqueIds.length; i++) {
            const deps = i > 0 ? [uniqueIds[i - 1]] : [];
            dag.addTask(
              createTaskDefinition({
                taskId: uniqueIds[i],
                jobId: "pbt_job",
                type: "render_chunk",
                dependencies: deps,
              })
            );
          }

          const order = dag.getTopologicalOrder();
          assert.equal(order.length, uniqueIds.length);

          // Invariante: cada tarea aparece después de sus dependencias
          for (let i = 1; i < uniqueIds.length; i++) {
            const prevIndex = order.indexOf(uniqueIds[i - 1]);
            const currIndex = order.indexOf(uniqueIds[i]);
            assert.ok(prevIndex < currIndex);
          }

          return true;
        }
      ),
      { numRuns: 50 }
    );
  });

  it("PBT: ThreeWayMergeArbiter is commutative when merging non-conflicting proposals", () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 20 }),
        fc.string({ minLength: 1, maxLength: 20 }),
        (valA, valB) => {
          const propA = createAgentProposal({
            proposalId: "prop_pbt_a",
            agentRole: "motion",
            baseRevisionId: "rev_0",
            changeSet: {
              changeSetId: "cs_a",
              description: "PBT change A",
              operations: [{ type: "set-property", targetId: "target_a", property: "prop_a", value: valA }],
            },
            rationale: "PBT A",
          });

          const propB = createAgentProposal({
            proposalId: "prop_pbt_b",
            agentRole: "audio",
            baseRevisionId: "rev_0",
            changeSet: {
              changeSetId: "cs_b",
              description: "PBT change B",
              operations: [{ type: "set-property", targetId: "target_b", property: "prop_b", value: valB }],
            },
            rationale: "PBT B",
          });

          const mergeAB = ThreeWayMergeArbiter.merge([propA, propB], "rev_0");
          const mergeBA = ThreeWayMergeArbiter.merge([propB, propA], "rev_0");

          // El resultado del merge debe ser idéntico sin importar el orden de los argumentos
          assert.equal(mergeAB.deterministicHash, mergeBA.deterministicHash);
          assert.equal(mergeAB.mergedChangeSet.operations.length, 2);
          assert.deepEqual(mergeAB.appliedProposals, mergeBA.appliedProposals);

          return true;
        }
      ),
      { numRuns: 50 }
    );
  });
});
