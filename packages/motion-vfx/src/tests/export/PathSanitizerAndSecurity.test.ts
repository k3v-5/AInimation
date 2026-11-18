import { describe, it } from "node:test";
import assert from "node:assert/strict";
import * as path from "path";
import { PathSanitizer, SecurityPathError } from "../../exporters/common/PathSanitizer.js";

describe("Fase 17 — PathSanitizer & Security Sandbox Tests", () => {
  const allowedSandbox = path.resolve("F:/Dev/after-effects-mcp/exports");

  it("sanitizes valid export file paths within allowed directory", () => {
    const validPath = "F:/Dev/after-effects-mcp/exports/output.jsx";
    const sanitized = PathSanitizer.sanitizeOutputPath(validPath, allowedSandbox);
    assert.equal(sanitized, path.resolve(validPath));
  });

  it("rejects path traversal attempts (../, ..\\, %2e%2e)", () => {
    const traversalPayloads = [
      "F:/Dev/after-effects-mcp/exports/../../secret.jsx",
      "F:/Dev/after-effects-mcp/exports/%2e%2e/secret.jsx",
      "exports/../../../windows/system32/cmd.jsx",
      "F:/Dev/after-effects-mcp/exports/file\0.jsx",
    ];

    for (const payload of traversalPayloads) {
      assert.throws(
        () => {
          PathSanitizer.sanitizeOutputPath(payload, allowedSandbox);
        },
        (err: any) => err instanceof SecurityPathError
      );
    }
  });

  it("rejects dangerous executable extensions (.exe, .bat, .sh, .ps1)", () => {
    const dangerousPaths = [
      "F:/Dev/after-effects-mcp/exports/script.exe",
      "F:/Dev/after-effects-mcp/exports/payload.bat",
      "F:/Dev/after-effects-mcp/exports/attack.sh",
      "F:/Dev/after-effects-mcp/exports/install.ps1",
    ];

    for (const badPath of dangerousPaths) {
      assert.throws(
        () => {
          PathSanitizer.sanitizeOutputPath(badPath, allowedSandbox);
        },
        /forbidden|not in allowed/
      );
    }
  });
});
