/**
 * Tool error reporting.
 *
 * The editor raises errors that carry a stable diagnostic English message and
 * a message key. A model can act on the message, so it is returned verbatim
 * with the key and the offending parameters attached for disambiguation.
 */

export class ToolError extends Error {
  constructor(message, { code = 'tool_error', details = null } = {}) {
    super(message);
    this.name = 'ToolError';
    this.code = code;
    this.details = details;
  }
}

/** Describe any thrown value for a model: message, key and useful context. */
export function describeError(error) {
  if (error instanceof ToolError) {
    return { message: error.message, code: error.code, details: error.details };
  }
  if (error && typeof error === 'object') {
    const message = typeof error.message === 'string' && error.message ? error.message : String(error);
    const details = {};
    if (typeof error.messageKey === 'string') details.messageKey = error.messageKey;
    if (error.messageParams && Object.keys(error.messageParams).length) details.messageParams = error.messageParams;
    if (typeof error.code === 'string') details.code = error.code;
    return { message, code: 'editor_error', details: Object.keys(details).length ? details : null };
  }
  return { message: String(error), code: 'unknown_error', details: null };
}

/**
 * Run a handler and turn a failure into an MCP tool result the model can read.
 * Errors are results, not protocol faults: the model should see the reason
 * and retry, not see the session die.
 */
export async function guard(handler) {
  try {
    return await handler();
  } catch (error) {
    const described = describeError(error);
    return {
      isError: true,
      content: [{ type: 'text', text: described.message }],
      structuredContent: { error: described },
    };
  }
}
