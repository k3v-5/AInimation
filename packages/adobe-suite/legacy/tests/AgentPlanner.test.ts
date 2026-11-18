import { test, expect, describe } from 'vitest';
import { AgentPlanner, ILLMProvider, LLMResponse } from '../src/ai/AgentPlanner.js';

class MockLLM implements ILLMProvider {
  public responses: LLMResponse[] = [];
  public callCount = 0;

  async prompt(messages: { role: string; content: string }[]): Promise<LLMResponse> {
    const response = this.responses[this.callCount] || { type: 'message', content: 'No mock response configured' };
    this.callCount++;
    return response;
  }
}

describe('AgentPlanner (Cognitive Layer)', () => {
  test('AC-16: Successfully translates natural language and calls tool', async () => {
    const llm = new MockLLM();
    llm.responses = [
      {
        type: 'tool_call',
        tool_name: 'execute_intent',
        tool_payload: { id: 'valid_intent' }
      }
    ];

    let engineCalled = false;
    const engineMock = async (payload: any) => {
      engineCalled = true;
      expect(payload.id).toBe('valid_intent');
      return { status: 'SUCCESS', artifacts: [{ local_path: '/out.mp4' }] };
    };

    const planner = new AgentPlanner(llm, engineMock);
    const result = await planner.handleUserRequest("Render an animation");

    expect(engineCalled).toBe(true);
    expect(result).toContain('/out.mp4');
  });

  test('AC-17: Self-reflects and heals upon Engine (Zod) validation error', async () => {
    const llm = new MockLLM();
    // 1st Attempt: LLM sends bad payload
    // 2nd Attempt: LLM sends fixed payload
    llm.responses = [
      {
        type: 'tool_call',
        tool_name: 'execute_intent',
        tool_payload: { id: 'bad_intent' }
      },
      {
        type: 'tool_call',
        tool_name: 'execute_intent',
        tool_payload: { id: 'fixed_intent' }
      }
    ];

    let executionCount = 0;
    const engineMock = async (payload: any) => {
      executionCount++;
      if (executionCount === 1) {
        return { status: 'FAILED', message: 'ZodError: Missing parameter' };
      }
      return { status: 'SUCCESS', artifacts: [{ local_path: '/out.mp4' }] };
    };

    const planner = new AgentPlanner(llm, engineMock);
    const result = await planner.handleUserRequest("Render an animation");

    expect(executionCount).toBe(2);
    expect(result).toContain('/out.mp4');
  });

  test('AC-18: Asks for clarification without calling the tool', async () => {
    const llm = new MockLLM();
    // LLM detects missing path and asks the user directly instead of calling the tool
    llm.responses = [
      {
        type: 'message',
        content: 'Please provide the path to the audio file.'
      }
    ];

    let engineCalled = false;
    const engineMock = async () => {
      engineCalled = true;
      return { status: 'SUCCESS' };
    };

    const planner = new AgentPlanner(llm, engineMock);
    const result = await planner.handleUserRequest("Make the character speak");

    expect(engineCalled).toBe(false);
    expect(result).toBe('Please provide the path to the audio file.');
  });
});
