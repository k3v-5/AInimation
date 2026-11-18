import { z } from "zod";

export const AgentRoleSchema = z.enum([
  "director",
  "editor",
  "motion",
  "audio",
  "qa_critic",
]);

export type AgentRole = z.infer<typeof AgentRoleSchema>;
