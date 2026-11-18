import { SYSTEM_PROMPT } from './system_prompt.js';
export interface LLMResponse {
  type: 'message' | 'tool_call';
  content?: string;
  tool_name?: string;
  tool_payload?: any;
}

export interface ILLMProvider {
  prompt(messages: { role: string, content: string }[]): Promise<LLMResponse>;
}

export class AgentPlanner {
  private llm: ILLMProvider;
  private maxReflections = 3;
  private mcpEngineExecuteCallback: (payload: any) => Promise<any>;

  constructor(llmProvider: ILLMProvider, engineCallback: (payload: any) => Promise<any>) {
    this.llm = llmProvider;
    this.mcpEngineExecuteCallback = engineCallback;
  }

  public async handleUserRequest(userInput: string): Promise<string> {
    const messages = [
      { role: 'system', content: SYSTEM_PROMPT },
      { role: 'user', content: userInput }
    ];

    let attempts = 0;

    while (attempts < this.maxReflections) {
      const response = await this.llm.prompt(messages);

      if (response.type === 'message') {
         return response.content || 'I need more information.';
      }

      if (response.type === 'tool_call') {
         if (response.tool_name === 'execute_intent') {
            try {
              const engineResult = await this.mcpEngineExecuteCallback(response.tool_payload);

              if (engineResult.status === 'FAILED') {
                messages.push({ role: 'assistant', content: `Attempted to call ${response.tool_name} with payload: ${JSON.stringify(response.tool_payload)}` });
                messages.push({ role: 'user', content: `TOOL ERROR: The engine rejected the payload. Fix the error and retry. Details: ${engineResult.message}` });
                attempts++;
                console.log(`[Agent] Reflection attempt ${attempts} due to engine error.`);
                continue;
              }

              const path = engineResult.artifacts?.[0]?.local_path || 'unknown';
              return `Animation complete! Output saved at: ${path}`;
            } catch (e: any) {
              messages.push({ role: 'user', content: `SYSTEM CRASH: ${e.message}` });
              attempts++;
            }
         } else {
            // Handle LLM hallucinating a non-existent tool to prevent infinite loops
            messages.push({ role: 'assistant', content: `Attempted to call ${response.tool_name}` });
            messages.push({ role: 'user', content: `ERROR: The tool ${response.tool_name} does not exist. Please use 'execute_intent'.` });
            attempts++;
         }
      }
    }

    return "Agent failed to resolve the request after maximum reflections.";
  }
}