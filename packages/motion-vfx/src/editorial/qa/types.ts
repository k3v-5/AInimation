export * from "./schemas.js";

export class EditorialQAError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "EditorialQAError";
  }
}

export class EditorialDiffError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "EditorialDiffError";
  }
}

export class HumanReviewValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "HumanReviewValidationError";
  }
}

export class ChecksumMismatchError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ChecksumMismatchError";
  }
}
