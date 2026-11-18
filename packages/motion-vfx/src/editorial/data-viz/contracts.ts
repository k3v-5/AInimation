import { z } from "zod";
export * from "../contracts/data-viz.types.js";

/**
 * REQ-025 §4: Esquemas de Validación Zod para Datasets Estadísticos
 */

export const DataSourceReferenceSchema = z.object({
  type: z.enum(["EVIDENCE", "STATIC", "URL"]),
  citationId: z.string().optional(),
  uri: z.string().optional(),
  description: z.string().optional(),
});

export const DatasetValueSchema = z.object({
  label: z.string().min(1, "La etiqueta es obligatoria"),
  value: z.number().refine((v) => Number.isFinite(v), "El valor debe ser un número finito"),
  timestamp: z.number().optional(),
  category: z.string().optional(),
  sourceRef: z.string().optional(),
});

export const DatasetSchema = z.object({
  id: z.string().min(1, "El identificador del dataset no puede estar vacío"),
  title: z.string().optional(),
  description: z.string().optional(),
  source: DataSourceReferenceSchema.optional(),
  unit: z.string().optional(),
  values: z.array(DatasetValueSchema).min(1, "El dataset no puede estar vacío"),
  metadata: z.record(z.unknown()).optional(),
});
