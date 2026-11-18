import { CaptionSerializationError } from "../../errors/index.js";
import { CaptionDocumentSchema } from "../schemas/caption.schema.js";
import { CaptionDocument } from "../types/index.js";

/**
 * Serializador y deserializador determinista para CaptionDocument v1.6.0 (Fase 16).
 */
export class CaptionSerializer {
  /**
   * Serializa un CaptionDocument a JSON con indentación determinista y esquema v1.6.0.
   */
  public static toJSON(document: CaptionDocument, pretty = false): string {
    try {
      const validated = CaptionDocumentSchema.parse({
        ...document,
        schemaVersion: document.schemaVersion ?? "1.6.0",
      });
      return JSON.stringify(validated, null, pretty ? 2 : undefined);
    } catch (err: any) {
      throw new CaptionSerializationError(
        `Failed to serialize CaptionDocument: ${err?.message ?? String(err)}`,
        { documentId: document?.id }
      );
    }
  }

  /**
   * Deserializa y valida un JSON a un CaptionDocument canónico v1.6.0.
   */
  public static fromJSON(jsonStringOrObj: string | Record<string, any>): CaptionDocument {
    let rawData: any;
    if (typeof jsonStringOrObj === "string") {
      try {
        rawData = JSON.parse(jsonStringOrObj);
      } catch (err: any) {
        throw new CaptionSerializationError(`Invalid JSON format: ${err?.message ?? String(err)}`);
      }
    } else if (typeof jsonStringOrObj === "object" && jsonStringOrObj !== null) {
      rawData = jsonStringOrObj;
    } else {
      throw new CaptionSerializationError("Input must be a valid JSON string or object.");
    }

    try {
      const parsed = CaptionDocumentSchema.parse(rawData);
      return parsed as CaptionDocument;
    } catch (err: any) {
      throw new CaptionSerializationError(
        `Caption schema validation failed: ${err?.message ?? String(err)}`,
        { rawData }
      );
    }
  }
}
