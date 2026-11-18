import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { RuntimeMCPResources } from "../../mcp/resources/runtime-resources.js";
import { handleCloseProject } from "../../mcp/tools/close-project.js";
import { handleCreateProject } from "../../mcp/tools/create-project.js";
import { handleDiffProjectRevisions } from "../../mcp/tools/diff-project-revisions.js";
import { handleGetProjectStatus } from "../../mcp/tools/get-project-status.js";
import { handleListProjectRevisions } from "../../mcp/tools/list-project-revisions.js";
import { handleOpenProject } from "../../mcp/tools/open-project.js";
import { handleRestoreProjectRevision } from "../../mcp/tools/restore-project-revision.js";
import { handleSaveProject } from "../../mcp/tools/save-project.js";
import { handleValidateProject } from "../../mcp/tools/validate-project.js";
import { MemoryStorageAdapter } from "../../runtime/persistence/MemoryStorageAdapter.js";
import { ProjectRuntime } from "../../runtime/ProjectRuntime.js";

describe("Fase 18 — MCP Runtime Tools & Resources Integration Tests", () => {
  it("executes the full MCP runtime lifecycle across all tools and resources", async () => {
    const storage = new MemoryStorageAdapter();
    const runtime = new ProjectRuntime({ storageRoot: ":memory:" }, storage);

    // 1. create_project
    const createRes = await handleCreateProject(runtime, {
      name: "Viral Video Project",
      width: 1080,
      height: 1920,
      fps: 30,
      duration: 15,
    });

    assert.equal(createRes.status, "created");
    assert.ok(createRes.projectId.startsWith("proj_"));
    assert.equal(createRes.revisionId, "rev_000001");
    const projectId = createRes.projectId;

    // 2. save_project (genera rev_000002)
    const saveRes = await handleSaveProject(runtime, {
      projectId,
      description: "Added initial title scene",
    });
    assert.equal(saveRes.revisionId, "rev_000002");

    // 3. get_project_status
    const statusRes = await handleGetProjectStatus(runtime, { projectId });
    assert.equal(statusRes.projectId, projectId);
    assert.equal(statusRes.revisionId, "rev_000002");
    assert.equal(statusRes.healthStatus, "healthy");

    // 4. list_project_revisions
    const revList = await handleListProjectRevisions(runtime, { projectId });
    assert.equal(revList.totalRevisions, 2);

    // 5. diff_project_revisions
    const diffRes = await handleDiffProjectRevisions(runtime, {
      projectId,
      fromRevisionId: "rev_000001",
      toRevisionId: "rev_000002",
    });
    assert.equal(diffRes.projectId, projectId);

    // 6. restore_project_revision (rev_000001 -> crea rev_000003)
    const restoreRes = await handleRestoreProjectRevision(runtime, {
      projectId,
      targetRevisionId: "rev_000001",
    });
    assert.equal(restoreRes.newRevisionId, "rev_000003");

    // 7. validate_project
    const valRes = await handleValidateProject(runtime, { projectId });
    assert.equal(valRes.status, "healthy");

    // 8. close_project
    const closeRes = await handleCloseProject(runtime, { projectId });
    assert.equal(closeRes.status, "closed");

    // 9. MCP Resources
    const healthResource = await RuntimeMCPResources.getResourceContent(runtime, "runtime://health");
    assert.ok(healthResource.includes("healthy"));

    const capsResource = await RuntimeMCPResources.getResourceContent(runtime, "capabilities://runtime");
    assert.ok(capsResource.includes("persistence"));
  });
});
