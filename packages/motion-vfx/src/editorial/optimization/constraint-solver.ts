export type ConstraintClass = "HARD" | "SOFT" | "PREFERENCE";

export interface EditorialConstraint {
  id: string;
  name: string;
  constraintClass: ConstraintClass;
  description: string;
  validator: (candidate: any) => { passed: boolean; reason?: string };
}

export interface ConstraintSolveResult {
  isFeasible: boolean;
  violatedHardConstraints: string[];
  violatedSoftConstraints: string[];
  satisfiedConstraints: string[];
  explanation: string;
}

/**
 * REQ-077: Master Editorial Constraint Solver
 * Garantiza de forma estricta que ninguna restricción dura (SAFETY, FACTUAL, LICENSE, LOCKED)
 * sea jamás violada para optimizar ritmo, estética o duración.
 */
export class EditorialConstraintSolver {
  private readonly constraints: Map<string, EditorialConstraint> = new Map();

  constructor(initialConstraints?: EditorialConstraint[]) {
    if (initialConstraints) {
      for (const c of initialConstraints) {
        this.constraints.set(c.id, c);
      }
    }
  }

  public registerConstraint(constraint: EditorialConstraint): void {
    this.constraints.set(constraint.id, constraint);
  }

  public solve(candidate: any): ConstraintSolveResult {
    const violatedHard: string[] = [];
    const violatedSoft: string[] = [];
    const satisfied: string[] = [];

    for (const constraint of this.constraints.values()) {
      const check = constraint.validator(candidate);
      if (check.passed) {
        satisfied.push(constraint.id);
      } else {
        if (constraint.constraintClass === "HARD") {
          violatedHard.push(`${constraint.id}: ${check.reason || "Hard constraint violation"}`);
        } else {
          violatedSoft.push(`${constraint.id}: ${check.reason || "Soft constraint violation"}`);
        }
      }
    }

    const isFeasible = violatedHard.length === 0;
    const explanation = isFeasible
      ? `Candidate is feasible. Satisfied ${satisfied.length} constraint(s). Soft violations: ${violatedSoft.length}.`
      : `INVIOLABLE_HARD_CONSTRAINT_FAILURE: Rejected due to ${violatedHard.length} hard constraint violation(s): ${violatedHard.join("; ")}`;

    return {
      isFeasible,
      violatedHardConstraints: violatedHard,
      violatedSoftConstraints: violatedSoft,
      satisfiedConstraints: satisfied,
      explanation,
    };
  }
}
