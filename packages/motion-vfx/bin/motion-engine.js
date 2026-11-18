#!/usr/bin/env node

import { CLIRunner } from "../build/cli/CLIRunner.js";

CLIRunner.run(process.argv)
  .then((exitCode) => {
    process.exit(exitCode);
  })
  .catch((err) => {
    console.error("Fatal CLI execution error:", err);
    process.exit(1);
  });
