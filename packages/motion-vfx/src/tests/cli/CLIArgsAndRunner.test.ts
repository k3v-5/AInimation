import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { CLIArgs } from "../../cli/CLIArgs.js";
import { CLIRunner } from "../../cli/CLIRunner.js";

describe("Fase 27 — Capa 1: CLI Argument Parsing & Runner Tests", () => {
  it("parses CLI arguments with command, flags, input and output", () => {
    const argv = [
      "node",
      "motion-engine.js",
      "render",
      "project.json",
      "-o",
      "out.mp4",
      "--fps",
      "60",
      "--workers",
      "8",
      "--strict",
    ];

    const args = CLIArgs.parse(argv);
    assert.equal(args.command, "render");
    assert.equal(args.inputFile, "project.json");
    assert.equal(args.output, "out.mp4");
    assert.equal(args.fps, 60);
    assert.equal(args.workers, 8);
    assert.equal(args.strict, true);
  });

  it("handles --version and --help returning exit code 0", async () => {
    const codeVersion = await CLIRunner.run(["node", "bin", "--version"]);
    assert.equal(codeVersion, 0);

    const codeHelp = await CLIRunner.run(["node", "bin", "--help"]);
    assert.equal(codeHelp, 0);
  });

  it("returns exit code 1 on unknown command", async () => {
    const code = await CLIRunner.run(["node", "bin", "invalid_cmd"]);
    assert.equal(code, 1);
  });
});
