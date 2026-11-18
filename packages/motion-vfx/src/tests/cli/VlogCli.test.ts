import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { execSync } from "node:child_process";
import path from "node:path";

describe("Milestone 8 & Section 45 — Vlog CLI Executable Suite", () => {
  const cliPath = path.resolve("bin/vlog-cli.js");

  it("executes bin/vlog-cli.js with dry-run and custom arguments successfully", () => {
    const cmd = `node "${cliPath}" --dry-run --project-id=cli_test_01 --languages=es-MX,en-US --script="Prueba de ejecucion CLI"`;
    const output = execSync(cmd, { encoding: "utf-8" });

    assert.ok(output.includes("AUTONOMOUS VLOG INTELLIGENCE PRODUCTION CLI"));
    assert.ok(output.includes("Project ID:        cli_test_01"));
    assert.ok(output.includes("Target Languages:  es-MX,en-US"));
    assert.ok(output.includes("RUN SUCCESS: YES"));
    assert.ok(output.includes("VLOG PRODUCTION COMPLETED SUCCESSFULLY"));
  });
});
