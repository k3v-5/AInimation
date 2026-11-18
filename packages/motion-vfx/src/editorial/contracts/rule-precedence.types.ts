import { z } from "zod";

/**
 * REQ-076: Universal Rule Precedence Hierarchy.
 * When constraints conflict, higher-precedence rules strictly override lower-precedence ones.
 */
export const RulePriorityTierSchema = z.enum([
  "SAFETY",          // Safe zones, photosensitivity, hardware limits
  "LEGAL_FACTUAL",   // Defamation, verified evidence, factual claims, licensing
  "EDITOR_LOCK",     // Human locked edits and explicit locks
  "NARRATIVE",       // Story causality, narrative anchors, climax timing
  "CONTINUITY",      // 180-degree axis, screen direction, eyelines
  "AUDIO",           // Intelligibility, dialogue loudness, clipping prevention
  "VISUAL",          // Shot grammar, scale progression, B-Roll freshness
  "STYLE",           // Style bible preferences, color themes, decorative typography
  "OPTIMIZATION",    // Duration matching, speedups, minor pacing trims
]);

export type RulePriorityTier = z.infer<typeof RulePriorityTierSchema>;

/**
 * Numeric rank ordering: higher number = higher priority.
 */
export const RULE_PRIORITY_RANKS: Record<RulePriorityTier, number> = {
  SAFETY: 900,
  LEGAL_FACTUAL: 800,
  EDITOR_LOCK: 700,
  NARRATIVE: 600,
  CONTINUITY: 500,
  AUDIO: 400,
  VISUAL: 300,
  STYLE: 200,
  OPTIMIZATION: 100,
};

/**
 * Utility to compare two tiers according to REQ-076.
 * Returns > 0 if tierA has higher priority than tierB.
 */
export function compareRulePrecedence(tierA: RulePriorityTier, tierB: RulePriorityTier): number {
  return RULE_PRIORITY_RANKS[tierA] - RULE_PRIORITY_RANKS[tierB];
}

/**
 * Validates if rule A can override rule B.
 */
export function canOverrideRule(tierCandidate: RulePriorityTier, tierExisting: RulePriorityTier): boolean {
  return RULE_PRIORITY_RANKS[tierCandidate] > RULE_PRIORITY_RANKS[tierExisting];
}
