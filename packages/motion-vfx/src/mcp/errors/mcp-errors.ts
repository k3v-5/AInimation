import { MotionEngineError, ValidationError } from "../../errors/index.js";

export class McpError extends MotionEngineError {
  constructor(message: string, public readonly code = "MCP_ERROR", public readonly details?: Record<string, any>) {
    super(`[${code}] ${message}`);
  }
}

export class McpValidationError extends McpError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, "MCP_VALIDATION_ERROR", details);
  }
}

export class McpToolNotFoundError extends McpError {
  constructor(toolName: string) {
    super(`Tool '${toolName}' was not found in MCP registry.`, "MCP_TOOL_NOT_FOUND", { toolName });
  }
}

export class McpProjectNotFoundError extends McpError {
  constructor(projectId: string, revisionId?: string) {
    super(
      `Project '${projectId}'${revisionId ? ` (revision '${revisionId}')` : ""} was not found in project store.`,
      "MCP_PROJECT_NOT_FOUND",
      { projectId, revisionId }
    );
  }
}

export class McpResourceLimitError extends McpError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, "RESOURCE_LIMIT_EXCEEDED", details);
  }
}
