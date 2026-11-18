import assert from "node:assert/strict";
import { describe, it, beforeEach } from "node:test";
import {
  ProductionMCPContext,
  handleCancelWorkflow,
  handleCreateProject,
  handleCreateRevision,
  handleDiffRevisions,
  handleGetProject,
  handleGetRevision,
  handleGetWorkflowStatus,
  handleListProjects,
  handleListRevisions,
  handleOpenProject,
  handleRestoreRevision,
  handleResumeWorkflow,
  handleRunWorkflow,
  handleSaveProject,
  handleUndoRevision,
  handleValidateProject,
} from "../../mcp/tools/phase18-tools.js";
import { Phase18Resources } from "../../mcp/resources/phase18-resources.js";
import { StepRegistry } from "../../workflows/WorkflowStep.js";

describe("Fase 18 — MCP Production Tools & Resources Tests", () => {
  beforeEach(() => {
    ProductionMCPContext.reset();
  });

  it("manages the complete project lifecycle across the 16 MCP tools", async () => {
    // 1. create_project
    const createRes = await handleCreateProject({
      projectId: "proj_mcp_prod",
      name: "Viral Video Production",
      description: "Automated video pipeline",
      author: "agent-director",
      width: 1080,
      height: 1920,
      fps: 30,
      duration: 15,
      initialElements: [{ id: "l1", name: "Headline", text: "Big Hook" }],
    });

    assert.equal(createRes.projectId, "proj_mcp_prod");
    assert.ok(createRes.headRevisionId.startsWith("rev_"));

    const rev0 = createRes.headRevisionId;

    // 2. open_project
    const openRes = await handleOpenProject({ projectId: "proj_mcp_prod" });
    assert.equal(openRes.projectId, "proj_mcp_prod");
    assert.equal(openRes.summary.elementsCount, 1);

    // 3. get_project
    const getRes = await handleGetProject({ projectId: "proj_mcp_prod" });
    assert.equal(getRes.projectId, "proj_mcp_prod");
    assert.equal(getRes.revisionId, rev0);

    // 4. create_revision
    const rev1Res = await handleCreateRevision({
      projectId: "proj_mcp_prod",
      message: "Add subtitle",
      projectData: {
        composition: { duration: 15, fps: 30 },
        elements: [
          { id: "l1", name: "Headline", text: "Big Hook" },
          { id: "l2", name: "Subtitle", text: "Supporting point" },
        ],
        assets: [],
      },
    });

    assert.ok(rev1Res.revisionId.startsWith("rev_"));
    const rev1 = rev1Res.revisionId;

    // 5. diff_revisions
    const diffRes = await handleDiffRevisions({
      projectId: "proj_mcp_prod",
      fromRevisionId: rev0,
      toRevisionId: rev1,
    });
    assert.equal(diffRes.summary.added, 1);

    // 6. get_revision
    const getRevRes = await handleGetRevision({
      projectId: "proj_mcp_prod",
      revisionId: rev1,
    });
    assert.equal(getRevRes.revisionId, rev1);

    // 7. list_revisions
    const listRevRes = await handleListRevisions({ projectId: "proj_mcp_prod" });
    assert.equal(listRevRes.totalCount, 2);

    // 8. undo_revision
    const undoRes = await handleUndoRevision({
      projectId: "proj_mcp_prod",
      targetRevisionId: rev1,
      message: "Undo subtitle addition",
    });
    assert.equal(undoRes.status, "undone");
    assert.ok(undoRes.newHeadRevisionId.startsWith("rev_"));

    // 9. restore_revision
    const restoreRes = await handleRestoreRevision({
      projectId: "proj_mcp_prod",
      targetRevisionId: rev1,
      message: "Restore rev1 state",
    });
    assert.equal(restoreRes.status, "restored");

    // 10. validate_project
    const valRes = await handleValidateProject({ projectId: "proj_mcp_prod" });
    assert.equal(valRes.valid, true);

    // 11. save_project
    const saveRes = await handleSaveProject({
      projectId: "proj_mcp_prod",
      message: "Save checkpoint",
    });
    assert.equal(saveRes.saved, true);

    // 12. list_projects
    const listProjRes = await handleListProjects({ limit: 10 });
    assert.equal(listProjRes.totalCount, 1);
    assert.equal(listProjRes.projects[0].projectId, "proj_mcp_prod");
  });

  it("executes and controls workflows via MCP workflow tools", async () => {
    // Setup a project first
    await handleCreateProject({
      projectId: "proj_wf_mcp",
      name: "Workflow Test MCP",
      duration: 10,
    });

    StepRegistry.register("MCP_STEP_1", async (ctx) => {
      ctx.set("out_1", "step 1 success");
      return { step1: "done" };
    });

    StepRegistry.register("MCP_STEP_2", async (ctx) => {
      return { prev: ctx.get("out_1"), step2: "done" };
    });

    const engine = ProductionMCPContext.getWorkflowEngine();
    engine.registerWorkflow({
      id: "wf_mcp_pipeline",
      version: "1.0.0",
      steps: [
        { id: "s1", type: "MCP_STEP_1", dependsOn: [], retryPolicy: { maxAttempts: 1, strategy: "none", intervalMs: 0 }, idempotent: true },
        { id: "s2", type: "MCP_STEP_2", dependsOn: ["s1"], retryPolicy: { maxAttempts: 1, strategy: "none", intervalMs: 0 }, idempotent: true },
      ],
    });

    // run_workflow
    const runRes = await handleRunWorkflow({
      workflowId: "wf_mcp_pipeline",
      projectId: "proj_wf_mcp",
    });

    assert.equal(runRes.status, "completed");
    assert.deepEqual(runRes.completedSteps, ["s1", "s2"]);

    // get_workflow_status
    const statusRes = await handleGetWorkflowStatus({ workflowId: "wf_mcp_pipeline" });
    assert.equal(statusRes.state, "completed");
    assert.equal(statusRes.checkpointCount, 2);

    // cancel_workflow
    const cancelRes = await handleCancelWorkflow({ workflowId: "wf_mcp_pipeline", reason: "Stop" });
    assert.equal(cancelRes.status, "cancellation_requested");
  });

  it("provides declarative MCP resources for project inspection", async () => {
    await handleCreateProject({
      projectId: "proj_resource_test",
      name: "Resource Project",
    });

    // projects://
    const listRes = await Phase18Resources.listProjectsResource();
    assert.equal(listRes.contents[0].uri, "projects://");
    assert.ok(listRes.contents[0].text.includes("proj_resource_test"));

    // projects://{id}
    const projRes = await Phase18Resources.readProjectResource("proj_resource_test");
    assert.equal(projRes.contents[0].uri, "projects://proj_resource_test");

    // projects://{id}/revisions
    const revsRes = await Phase18Resources.listProjectRevisionsResource("proj_resource_test");
    assert.equal(revsRes.contents[0].uri, "projects://proj_resource_test/revisions");
  });
});
