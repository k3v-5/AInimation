import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { CLIRunner } from "../../cli/CLIRunner.js";

describe("Fase 27 — Capa 2: CLI Commands Execution Tests", () => {
  it("executes render command with valid exit code 0", async () => {
    const code = await CLIRunner.run(["node", "bin", "render", "test_proj.json", "-o", "output.mp4", "--fps", "30"]);
    assert.equal(code, 0);
  });

  it("executes export-ae command with valid exit code 0", async () => {
    const code = await CLIRunner.run(["node", "bin", "export-ae", "test_proj.json", "-o", "script.jsx", "--strict"]);
    assert.equal(code, 0);
  });

  it("executes export-social command with valid exit code 0", async () => {
    const code = await CLIRunner.run([
      "node",
      "bin",
      "export-social",
      "test_proj.json",
      "-o",
      "./dist/delivery",
      "--ratios",
      "9:16,16:9,1:1",
    ]);
    assert.equal(code, 0);
  });

  it("executes qa and validate commands returning standard exit codes", async () => {
    const qaCode = await CLIRunner.run(["node", "bin", "qa", "test_proj.json", "--threshold", "0.8"]);
    assert.equal(qaCode, 0);

    const valCode = await CLIRunner.run(["node", "bin", "validate", "test_proj.json"]);
    assert.equal(valCode, 0);
  });

  it("returns exit code 1 when input file is missing", async () => {
    const code = await CLIRunner.run(["node", "bin", "render"]);
    assert.equal(code, 1);
  });
});
