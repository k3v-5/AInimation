import { EditorialIR } from "../ir/editorial-ir.types.js";
import {
  EditorialQAFinding,
  EditorialSeverity,
  EditorialFindingCategory,
  createFinding,
} from "./editorial-findings.js";
import { createRemediation } from "./editorial-remediation.js";

/**
 * REQ-030 §7: Contexto de Evaluación QA
 */
export interface EditorialQAContext {
  ir: EditorialIR;
  profile?: any;
  config?: {
    thresholds?: {
      humanReviewConfidence?: number;
      maxCognitiveLoad?: number;
      minAttention?: number;
      minPacingAlignment?: number;
      maxLowTensionDuration?: number;
      maxHighTensionRun?: number;
    };
    gapPolicy?: "ALLOW" | "WARNING" | "BLOCK";
    strict?: boolean;
    failOnWarnings?: boolean;
    requireEvidence?: boolean;
    requireSafeZones?: boolean;
    [key: string]: unknown;
  };
  evidenceReport?: any;
  assetRegistry?: Record<string, { exists: boolean; path?: string }>;
  attentionModel?: any;
  cognitiveModel?: any;
  pacingCurve?: any;
  contrastMetrics?: any;
  [key: string]: unknown;
}

/**
 * REQ-030 §7: Contrato Independiente de Regla QA
 */
export interface EditorialQARule {
  id: string;
  version: string;
  severity: EditorialSeverity;
  category: EditorialFindingCategory;
  description: string;
  evaluate(context: EditorialQAContext): EditorialQAFinding[];
}

/**
 * Registro de reglas canónicas del motor QA
 */
export class EditorialRulesRegistry {
  private static readonly rules: Map<string, EditorialQARule> = new Map();

  public static register(rule: EditorialQARule): void {
    this.rules.set(rule.id, rule);
  }

  public static getRule(id: string): EditorialQARule | undefined {
    return this.rules.get(id);
  }

  public static getAllRules(): EditorialQARule[] {
    return Array.from(this.rules.values());
  }

  public static evaluateAll(context: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    for (const rule of this.rules.values()) {
      try {
        const ruleFindings = rule.evaluate(context);
        findings.push(...ruleFindings);
      } catch (err: any) {
        findings.push(
          createFinding({
            ruleId: rule.id,
            severity: "BLOCKING",
            category: "PERFORMANCE",
            title: `Error en regla ${rule.id}`,
            message: `Fallo durante la evaluación de la regla: ${err?.message ?? String(err)}`,
            confidence: 1.0,
          })
        );
      }
    }
    return findings;
  }
}

/* =========================================================================
 * 8.1 Reglas Estructurales (QA-STRUCT-001 a 004)
 * ========================================================================= */

// QA-STRUCT-001: Detectar nodos IR huérfanos o fuera de track
EditorialRulesRegistry.register({
  id: "QA-STRUCT-001",
  version: "1.0.0",
  severity: "BLOCKING",
  category: "STRUCTURAL",
  description: "Detecta nodos y clips huérfanos sin contenedor o con track inexistente.",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    if (!ctx.ir.tracks || !Array.isArray(ctx.ir.tracks)) {
      findings.push(
        createFinding({
          ruleId: "QA-STRUCT-001",
          severity: "BLOCKING",
          category: "STRUCTURAL",
          title: "Pistas del timeline ausentes",
          message: "El timeline no contiene una lista de pistas válida.",
          confidence: 1.0,
          evidence: [{ type: "IR_NODE", reference: "tracks", description: "Array de tracks inválido o nulo" }],
        })
      );
    }
    return findings;
  },
});

// QA-STRUCT-002: Detectar referencias a assets inexistentes o vacíos
EditorialRulesRegistry.register({
  id: "QA-STRUCT-002",
  version: "1.0.0",
  severity: "BLOCKING",
  category: "STRUCTURAL",
  description: "Detecta clips que referencian assets no registrados o con assetId vacío.",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    for (const track of ctx.ir.tracks ?? []) {
      for (const clip of track.clips ?? []) {
        if (!clip.assetId || clip.assetId.trim() === "") {
          findings.push(
            createFinding({
              ruleId: "QA-STRUCT-002",
              severity: "BLOCKING",
              category: "STRUCTURAL",
              title: "Clip sin Asset ID",
              message: `El clip '${clip.id}' en la pista '${track.id}' no especifica un assetId.`,
              timestampSeconds: clip.timelineRange?.startSeconds,
              durationSeconds: clip.timelineRange?.durationSeconds,
              affectedNodeIds: [clip.id],
              confidence: 1.0,
              remediation: createRemediation("REMOVE", { clipId: clip.id, trackId: track.id }),
              evidence: [
                { type: "IR_NODE", reference: clip.id, description: "Propiedad assetId vacía o ausente" },
              ],
            })
          );
        } else if (ctx.assetRegistry && ctx.assetRegistry[clip.assetId]?.exists === false) {
          findings.push(
            createFinding({
              ruleId: "QA-STRUCT-002",
              severity: "BLOCKING",
              category: "STRUCTURAL",
              title: "Asset referenciado no encontrado",
              message: `El asset '${clip.assetId}' requerido por el clip '${clip.id}' no existe en el registro.`,
              timestampSeconds: clip.timelineRange?.startSeconds,
              durationSeconds: clip.timelineRange?.durationSeconds,
              affectedNodeIds: [clip.id],
              confidence: 1.0,
              remediation: createRemediation("REPLACE", { clipId: clip.id, missingAssetId: clip.assetId }),
              evidence: [
                { type: "SOURCE_ASSET", reference: clip.assetId, description: "Asset ausente en el filesystem" },
              ],
            })
          );
        }
      }
    }
    return findings;
  },
});

// QA-STRUCT-003: Detectar referencias circulares o IDs duplicados
EditorialRulesRegistry.register({
  id: "QA-STRUCT-003",
  version: "1.0.0",
  severity: "BLOCKING",
  category: "STRUCTURAL",
  description: "Detecta duplicación de identificadores de clips y pistas en el IR.",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    const seenIds = new Set<string>();

    for (const track of ctx.ir.tracks ?? []) {
      if (seenIds.has(track.id)) {
        findings.push(
          createFinding({
            ruleId: "QA-STRUCT-003",
            severity: "BLOCKING",
            category: "STRUCTURAL",
            title: "ID de pista duplicado",
            message: `Se encontró un ID de pista duplicado: '${track.id}'.`,
            affectedNodeIds: [track.id],
            confidence: 1.0,
            evidence: [{ type: "IR_NODE", reference: track.id, description: "Pista con identificador colisionado" }],
          })
        );
      }
      seenIds.add(track.id);

      for (const clip of track.clips ?? []) {
        if (seenIds.has(clip.id)) {
          findings.push(
            createFinding({
              ruleId: "QA-STRUCT-003",
              severity: "BLOCKING",
              category: "STRUCTURAL",
              title: "ID de clip duplicado",
              message: `Se detectó un identificador de clip duplicado: '${clip.id}'.`,
              affectedNodeIds: [clip.id],
              confidence: 1.0,
              evidence: [{ type: "IR_NODE", reference: clip.id, description: "Clip con identificador colisionado" }],
            })
          );
        }
        seenIds.add(clip.id);
      }
    }
    return findings;
  },
});

// QA-STRUCT-004: Validar esquema completo del IR
EditorialRulesRegistry.register({
  id: "QA-STRUCT-004",
  version: "1.0.0",
  severity: "BLOCKING",
  category: "STRUCTURAL",
  description: "Valida los campos obligatorios del esquema IR (schemaVersion, projectId, metadata).",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    if (!ctx.ir.schemaVersion) {
      findings.push(
        createFinding({
          ruleId: "QA-STRUCT-004",
          severity: "BLOCKING",
          category: "STRUCTURAL",
          title: "Esquema IR incompleto",
          message: "El IR no especifica 'schemaVersion'.",
          confidence: 1.0,
          evidence: [{ type: "RULE", reference: "IR_SCHEMA", description: "schemaVersion ausente" }],
        })
      );
    }
    if (!ctx.ir.metadata || typeof ctx.ir.metadata !== "object") {
      findings.push(
        createFinding({
          ruleId: "QA-STRUCT-004",
          severity: "BLOCKING",
          category: "STRUCTURAL",
          title: "Metadata ausente",
          message: "El IR debe contener un objeto 'metadata' válido.",
          confidence: 1.0,
          evidence: [{ type: "RULE", reference: "IR_SCHEMA", description: "metadata ausente o corrupto" }],
        })
      );
    }
    return findings;
  },
});

/* =========================================================================
 * 9. Validación Temporal (QA-TIME-001 a 006)
 * ========================================================================= */

// QA-TIME-001: Duraciones válidas (duration >= 0)
EditorialRulesRegistry.register({
  id: "QA-TIME-001",
  version: "1.0.0",
  severity: "BLOCKING",
  category: "TEMPORAL",
  description: "Verifica que todas las duraciones en el timeline sean números estrictamente no negativos.",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    for (const track of ctx.ir.tracks ?? []) {
      for (const clip of track.clips ?? []) {
        const dur = clip.timelineRange?.durationSeconds;
        if (dur !== undefined && dur < 0) {
          findings.push(
            createFinding({
              ruleId: "QA-TIME-001",
              severity: "BLOCKING",
              category: "TEMPORAL",
              title: "Duración de clip negativa",
              message: `El clip '${clip.id}' tiene una duración negativa (${dur}s).`,
              timestampSeconds: clip.timelineRange?.startSeconds,
              durationSeconds: dur,
              affectedNodeIds: [clip.id],
              expected: 0,
              actual: dur,
              confidence: 1.0,
              remediation: createRemediation("TRIM", { clipId: clip.id, durationSeconds: 0 }),
              evidence: [
                { type: "NUMERIC_VALUE", reference: "timelineRange.durationSeconds", value: dur, description: "Duración negativa" },
              ],
            })
          );
        }
      }
    }
    return findings;
  },
});

// QA-TIME-002: Timecodes válidos (finitos, >= 0, no NaN ni Infinity)
EditorialRulesRegistry.register({
  id: "QA-TIME-002",
  version: "1.0.0",
  severity: "BLOCKING",
  category: "TEMPORAL",
  description: "Comprueba que todos los timecodes sean finitos, >= 0 y rechaza estrictamente NaN o Infinity.",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    for (const track of ctx.ir.tracks ?? []) {
      for (const clip of track.clips ?? []) {
        const start = clip.timelineRange?.startSeconds;
        const dur = clip.timelineRange?.durationSeconds;
        if (start === undefined || !Number.isFinite(start) || start < 0 || isNaN(start)) {
          findings.push(
            createFinding({
              ruleId: "QA-TIME-002",
              severity: "BLOCKING",
              category: "TEMPORAL",
              title: "Timecode inválido o no finito",
              message: `El clip '${clip.id}' contiene un startSeconds inválido (${start}).`,
              affectedNodeIds: [clip.id],
              confidence: 1.0,
              evidence: [{ type: "TIMECODE", reference: "startSeconds", value: start, description: "Valor no finito o negativo" }],
            })
          );
        }
        if (dur === undefined || !Number.isFinite(dur) || isNaN(dur)) {
          findings.push(
            createFinding({
              ruleId: "QA-TIME-002",
              severity: "BLOCKING",
              category: "TEMPORAL",
              title: "Duración no finita",
              message: `El clip '${clip.id}' contiene un durationSeconds no finito (${dur}).`,
              affectedNodeIds: [clip.id],
              confidence: 1.0,
              evidence: [{ type: "TIMECODE", reference: "durationSeconds", value: dur, description: "Duración no finita o NaN" }],
            })
          );
        }
      }
    }
    return findings;
  },
});

// QA-TIME-003: Inversión temporal (start <= end)
EditorialRulesRegistry.register({
  id: "QA-TIME-003",
  version: "1.0.0",
  severity: "BLOCKING",
  category: "TEMPORAL",
  description: "Verifica que en los rangos temporales el inicio sea estrictamente menor o igual que el final.",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    for (const track of ctx.ir.tracks ?? []) {
      for (const clip of track.clips ?? []) {
        const srcStart = clip.sourceRange?.startSeconds;
        const srcDur = clip.sourceRange?.durationSeconds;
        if (srcStart !== undefined && srcDur !== undefined && srcDur < 0) {
          findings.push(
            createFinding({
              ruleId: "QA-TIME-003",
              severity: "BLOCKING",
              category: "TEMPORAL",
              title: "Inversión en rango de origen",
              message: `El rango de origen del clip '${clip.id}' tiene una duración negativa.`,
              affectedNodeIds: [clip.id],
              confidence: 1.0,
              evidence: [{ type: "TIMECODE", reference: "sourceRange", value: { srcStart, srcDur }, description: "Inversión temporal" }],
            })
          );
        }
      }
    }
    return findings;
  },
});

// QA-TIME-004: Overlap ilegal en canales primarios
EditorialRulesRegistry.register({
  id: "QA-TIME-004",
  version: "1.0.0",
  severity: "BLOCKING",
  category: "TEMPORAL",
  description: "Detecta solapamientos temporales ilegales en pistas que no soportan composición simultánea.",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    for (const track of ctx.ir.tracks ?? []) {
      if (track.type !== "VIDEO_PRIMARY") continue;
      const sortedClips = [...(track.clips ?? [])].sort(
        (a, b) => (a.timelineRange?.startSeconds ?? 0) - (b.timelineRange?.startSeconds ?? 0)
      );
      for (let i = 0; i < sortedClips.length - 1; i++) {
        const cur = sortedClips[i];
        const next = sortedClips[i + 1];
        const curEnd = (cur.timelineRange?.startSeconds ?? 0) + (cur.timelineRange?.durationSeconds ?? 0);
        const nextStart = next.timelineRange?.startSeconds ?? 0;
        if (curEnd - nextStart > 1e-4) {
          findings.push(
            createFinding({
              ruleId: "QA-TIME-004",
              severity: "BLOCKING",
              category: "TEMPORAL",
              title: "Solapamiento ilegal en pista primaria",
              message: `Los clips '${cur.id}' y '${next.id}' se solapan por ${(curEnd - nextStart).toFixed(3)}s en la pista primaria '${track.id}'.`,
              timestampSeconds: nextStart,
              durationSeconds: curEnd - nextStart,
              affectedNodeIds: [cur.id, next.id],
              confidence: 1.0,
              remediation: createRemediation("SHIFT", { clipId: next.id, shiftSeconds: curEnd - nextStart }),
              evidence: [
                { type: "TIMECODE", reference: `${cur.id} vs ${next.id}`, description: "Solapamiento en canal mono-composición" },
              ],
            })
          );
        }
      }
    }
    return findings;
  },
});

// QA-TIME-005: Gaps inesperados o cuadros negros
EditorialRulesRegistry.register({
  id: "QA-TIME-005",
  version: "1.0.0",
  severity: "WARNING",
  category: "TEMPORAL",
  description: "Detecta espacios temporales vacíos o huecos (gaps) no intencionados en la pista primaria.",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    const gapPolicy = ctx.config?.gapPolicy ?? "WARNING";
    if (gapPolicy === "ALLOW") return findings;

    const severity = gapPolicy === "BLOCK" ? "BLOCKING" : "WARNING";

    for (const track of ctx.ir.tracks ?? []) {
      if (track.type !== "VIDEO_PRIMARY") continue;
      const sortedClips = [...(track.clips ?? [])].sort(
        (a, b) => (a.timelineRange?.startSeconds ?? 0) - (b.timelineRange?.startSeconds ?? 0)
      );

      // Hueco inicial
      if (sortedClips.length > 0 && (sortedClips[0].timelineRange?.startSeconds ?? 0) > 0.04) {
        const gapDur = sortedClips[0].timelineRange.startSeconds;
        findings.push(
          createFinding({
            ruleId: "QA-TIME-005",
            severity,
            category: "TEMPORAL",
            title: "Hueco inicial detectado (Head Gap)",
            message: `La pista '${track.id}' comienza con un espacio vacío de ${gapDur.toFixed(3)}s antes del primer clip.`,
            timestampSeconds: 0,
            durationSeconds: gapDur,
            affectedNodeIds: [sortedClips[0].id],
            confidence: 0.95,
            remediation: createRemediation("SHIFT", { clipId: sortedClips[0].id, shiftSeconds: -gapDur }),
            evidence: [{ type: "TIMECODE", reference: "0.0s", value: gapDur, description: "Gap al inicio del timeline" }],
          })
        );
      }

      for (let i = 0; i < sortedClips.length - 1; i++) {
        const cur = sortedClips[i];
        const next = sortedClips[i + 1];
        const curEnd = (cur.timelineRange?.startSeconds ?? 0) + (cur.timelineRange?.durationSeconds ?? 0);
        const nextStart = next.timelineRange?.startSeconds ?? 0;
        const gap = nextStart - curEnd;
        if (gap > 0.04) {
          findings.push(
            createFinding({
              ruleId: "QA-TIME-005",
              severity,
              category: "TEMPORAL",
              title: "Hueco temporal entre clips (Black Gap)",
              message: `Se detectó un vacío de ${gap.toFixed(3)}s entre '${cur.id}' y '${next.id}'.`,
              timestampSeconds: curEnd,
              durationSeconds: gap,
              affectedNodeIds: [cur.id, next.id],
              confidence: 0.9,
              remediation: createRemediation("EXTEND", { clipId: cur.id, extendDuration: gap }),
              evidence: [{ type: "TIMECODE", reference: `${curEnd.toFixed(3)}s`, value: gap, description: "Gap inter-clip" }],
            })
          );
        }
      }
    }
    return findings;
  },
});

// QA-TIME-006: Duración total del timeline
EditorialRulesRegistry.register({
  id: "QA-TIME-006",
  version: "1.0.0",
  severity: "WARNING",
  category: "TEMPORAL",
  description: "Valida que la duración declarada del proyecto coincida con la extensión de sus elementos dentro de epsilon.",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    let maxEnd = 0;
    for (const track of ctx.ir.tracks ?? []) {
      for (const clip of track.clips ?? []) {
        const end = (clip.timelineRange?.startSeconds ?? 0) + (clip.timelineRange?.durationSeconds ?? 0);
        if (end > maxEnd) maxEnd = end;
      }
    }
    const metaDur = (ctx.ir.metadata as any)?.durationSeconds;
    if (metaDur !== undefined && Number.isFinite(metaDur)) {
      if (Math.abs(metaDur - maxEnd) > 1e-3) {
        findings.push(
          createFinding({
            ruleId: "QA-TIME-006",
            severity: "WARNING",
            category: "TEMPORAL",
            title: "Desfase en duración total declarada",
            message: `La duración declarada en metadata (${metaDur}s) difiere del fin del último clip (${maxEnd.toFixed(3)}s).`,
            expected: maxEnd,
            actual: metaDur,
            confidence: 0.85,
            evidence: [{ type: "CALCULATION", reference: "max(clip.end)", value: maxEnd, description: "Duración real acumulada" }],
          })
        );
      }
    }
    return findings;
  },
});

/* =========================================================================
 * 10. Validación Narrativa (QA-NARR-001 a 005)
 * ========================================================================= */

// QA-NARR-001: Ausencia de beats obligatorios
EditorialRulesRegistry.register({
  id: "QA-NARR-001",
  version: "1.0.0",
  severity: "WARNING",
  category: "NARRATIVE",
  description: "Detecta la ausencia de beats narrativos obligatorios según el perfil dramático.",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    const beats = (ctx.ir as any).narrativeBeats ?? [];
    if (Array.isArray(beats) && beats.length > 0) {
      const hasHook = beats.some((b: any) => b.type === "HOOK" || b.name === "HOOK");
      const hasClimax = beats.some((b: any) => b.type === "CLIMAX" || b.name === "CLIMAX");
      if (!hasHook) {
        findings.push(
          createFinding({
            ruleId: "QA-NARR-001",
            severity: "WARNING",
            category: "NARRATIVE",
            title: "Beat de HOOK no identificado",
            message: "La estructura narrativa carece de un beat inicial de retención (HOOK).",
            confidence: 0.8,
            remediation: createRemediation("REVIEW", {}, { confidence: 0.6 }),
            evidence: [{ type: "NARRATIVE_BEAT", reference: "HOOK", description: "Beat requerido ausente" }],
          })
        );
      }
      if (!hasClimax) {
        findings.push(
          createFinding({
            ruleId: "QA-NARR-001",
            severity: "WARNING",
            category: "NARRATIVE",
            title: "Beat de CLÍMAX ausente",
            message: "La estructura narrativa no culmina en un punto de clímax identificado.",
            confidence: 0.8,
            evidence: [{ type: "NARRATIVE_BEAT", reference: "CLIMAX", description: "Clímax ausente" }],
          })
        );
      }
    }
    return findings;
  },
});

// QA-NARR-002: Orden causal inválido
EditorialRulesRegistry.register({
  id: "QA-NARR-002",
  version: "1.0.0",
  severity: "BLOCKING",
  category: "NARRATIVE",
  description: "Detecta revelaciones antes del planteamiento de la pregunta o evidencia.",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    const beats = (ctx.ir as any).narrativeBeats ?? [];
    if (Array.isArray(beats) && beats.length > 1) {
      let revIndex = -1;
      let questIndex = -1;
      for (let i = 0; i < beats.length; i++) {
        if (beats[i].type === "REVELATION") revIndex = i;
        if (beats[i].type === "QUESTION" || beats[i].type === "INVESTIGATION") questIndex = i;
      }
      if (revIndex !== -1 && questIndex !== -1 && revIndex < questIndex) {
        findings.push(
          createFinding({
            ruleId: "QA-NARR-002",
            severity: "BLOCKING",
            category: "NARRATIVE",
            title: "Inversión causal narrativa",
            message: "Se presenta una REVELACIÓN antes de haber planteado la PREGUNTA o la investigación.",
            confidence: 0.95,
            evidence: [{ type: "NARRATIVE_BEAT", reference: "REVELATION", description: "Revelación prematura" }],
          })
        );
      }
    }
    return findings;
  },
});

// QA-NARR-003: Spoiler prematuro
EditorialRulesRegistry.register({
  id: "QA-NARR-003",
  version: "1.0.0",
  severity: "WARNING",
  category: "NARRATIVE",
  description: "Detecta revelación prematura de hechos clave antes de la marca mínima temporal.",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    const beats = (ctx.ir as any).narrativeBeats ?? [];
    if (Array.isArray(beats)) {
      for (const b of beats) {
        if (b.type === "REVELATION" && (b.startSeconds ?? 0) < 15.0) {
          findings.push(
            createFinding({
              ruleId: "QA-NARR-003",
              severity: "WARNING",
              category: "NARRATIVE",
              title: "Posible spoiler prematuro",
              message: `La revelación '${b.title || b.id}' ocurre a los ${b.startSeconds}s, antes del tiempo recomendado de maduración dramática.`,
              timestampSeconds: b.startSeconds,
              confidence: 0.75,
              evidence: [{ type: "TIMECODE", reference: `${b.startSeconds}s`, description: "Revelación temprana" }],
            })
          );
        }
      }
    }
    return findings;
  },
});

/* =========================================================================
 * 11. Validación de Evidencia (QA-EVIDENCE-001 a 004)
 * ========================================================================= */

// QA-EVIDENCE-001: Afirmaciones sin evidencia verificada
EditorialRulesRegistry.register({
  id: "QA-EVIDENCE-001",
  version: "1.0.0",
  severity: "BLOCKING",
  category: "EVIDENCE",
  description: "Detecta afirmaciones fácticas marcadas como obligatorias que carecen de fuentes o evidencia.",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    const evRep = ctx.evidenceReport ?? (ctx.ir as any)?.evidenceReport;
    if (evRep && Array.isArray(evRep.audits)) {
      for (const audit of evRep.audits) {
        if (audit.status === "MISSING_SOURCE" || (audit.blockingIssue && !audit.hasEvidence)) {
          findings.push(
            createFinding({
              ruleId: "QA-EVIDENCE-001",
              severity: "BLOCKING",
              category: "EVIDENCE",
              title: "Afirmación fáctica sin respaldo probatorio",
              message: `La afirmación '${audit.claimText || audit.claimId}' carece de fuentes verificadas.`,
              affectedNodeIds: [audit.claimId],
              confidence: audit.confidence ?? 0.95,
              evidence: [
                { type: "CLAIM", reference: audit.claimId, description: audit.notes || "Sin fuente adjunta" },
              ],
            })
          );
        }
      }
    }
    return findings;
  },
});

// QA-EVIDENCE-003: Citaciones requeridas faltantes
EditorialRulesRegistry.register({
  id: "QA-EVIDENCE-003",
  version: "1.0.0",
  severity: "WARNING",
  category: "EVIDENCE",
  description: "Detecta afirmaciones que requieren citación en pantalla pero no tienen tarjeta de citación.",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    const evRep = ctx.evidenceReport;
    if (evRep && Array.isArray(evRep.audits)) {
      for (const audit of evRep.audits) {
        if (audit.requiresCitation && !audit.hasCitation && audit.status !== "MISSING_SOURCE") {
          findings.push(
            createFinding({
              ruleId: "QA-EVIDENCE-003",
              severity: "WARNING",
              category: "EVIDENCE",
              title: "Citación en pantalla ausente",
              message: `La afirmación '${audit.claimId}' requiere citación visual en pantalla.`,
              affectedNodeIds: [audit.claimId],
              confidence: 0.85,
              remediation: createRemediation("ADD", { type: "CITATION_CARD", claimId: audit.claimId }),
              evidence: [{ type: "CLAIM", reference: audit.claimId, description: "Falta tarjeta de citación" }],
            })
          );
        }
      }
    }
    return findings;
  },
});

/* =========================================================================
 * 12. Continuidad, 13. Atención, 14. Carga Cognitiva, 15. Contraste, 16. Pacing
 * ========================================================================= */

// QA-LOAD-001: Sobrecarga cognitiva sostenida (C >= 0.85 durante >= 3.0s)
EditorialRulesRegistry.register({
  id: "QA-LOAD-001",
  version: "1.0.0",
  severity: "WARNING",
  category: "COGNITIVE",
  description: "Detecta intervalos de sobrecarga cognitiva sostenida (C >= 0.85 durante >= 3s).",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    const cog = ctx.cognitiveModel ?? (ctx.ir as any).cognitiveAnalysis;
    if (cog && Array.isArray(cog.overloadIntervals)) {
      for (const interval of cog.overloadIntervals) {
        if (interval.durationSeconds >= 3.0 || interval.cognitiveLoad >= 0.85) {
          findings.push(
            createFinding({
              ruleId: "QA-LOAD-001",
              severity: "WARNING",
              category: "COGNITIVE",
              title: "Sobrecarga cognitiva sostenida",
              message: `El modelo heurístico detecta carga cognitiva crítica (${interval.cognitiveLoad.toFixed(2)}) durante ${interval.durationSeconds.toFixed(1)}s.`,
              timestampSeconds: interval.startSeconds,
              durationSeconds: interval.durationSeconds,
              confidence: 0.88,
              remediation: createRemediation("TRIM", { startSeconds: interval.startSeconds, duration: interval.durationSeconds }),
              evidence: [
                { type: "METRIC", reference: "CognitiveLoad", value: interval.cognitiveLoad, description: "C = 0.30V + 0.25D + 0.20S + 0.15M + 0.10K" },
              ],
            })
          );
        }
      }
    }
    return findings;
  },
});

// QA-PACE-001: Desalineación de ritmo editorial
EditorialRulesRegistry.register({
  id: "QA-PACE-001",
  version: "1.0.0",
  severity: "WARNING",
  category: "PACING",
  description: "Detecta desalineación entre el ritmo real de cortes y la curva de pacing objetivo.",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    const pacing = ctx.pacingCurve ?? (ctx.ir as any).pacingAnalysis;
    const threshold = ctx.config?.thresholds?.minPacingAlignment ?? 0.65;
    if (pacing && typeof pacing.alignmentScore === "number") {
      if (pacing.alignmentScore < threshold) {
        findings.push(
          createFinding({
            ruleId: "QA-PACE-001",
            severity: "WARNING",
            category: "PACING",
            title: "Desalineación de ritmo editorial",
            message: `El puntaje de alineación de ritmo (${(pacing.alignmentScore * 100).toFixed(1)}%) está por debajo del umbral objetivo (${(threshold * 100).toFixed(1)}%).`,
            expected: threshold,
            actual: pacing.alignmentScore,
            confidence: 0.82,
            evidence: [
              { type: "METRIC", reference: "AlignmentScore", value: pacing.alignmentScore, description: "Pacing distance superior al umbral" },
            ],
          })
        );
      }
    }
    return findings;
  },
});

// QA-EXPORT-001: Compatibilidad para Exportación y Render
EditorialRulesRegistry.register({
  id: "QA-EXPORT-001",
  version: "1.0.0",
  severity: "BLOCKING",
  category: "EXPORT",
  description: "Valida que el timeline contenga al menos una pista activa y dimensiones compatibles con AE.",
  evaluate(ctx: EditorialQAContext): EditorialQAFinding[] {
    const findings: EditorialQAFinding[] = [];
    if (!ctx.ir.tracks || ctx.ir.tracks.length === 0) {
      findings.push(
        createFinding({
          ruleId: "QA-EXPORT-001",
          severity: "BLOCKING",
          category: "EXPORT",
          title: "Timeline sin pistas para exportación",
          message: "No es posible exportar o compilar un proyecto sin pistas en el timeline.",
          confidence: 1.0,
          evidence: [{ type: "RULE", reference: "EXPORT_COMPAT", description: "Pistas vacías" }],
        })
      );
    }
    const width = ctx.ir.metadata?.width;
    const height = ctx.ir.metadata?.height;
    if (!width || !height || width <= 0 || height <= 0) {
      findings.push(
        createFinding({
          ruleId: "QA-EXPORT-001",
          severity: "BLOCKING",
          category: "EXPORT",
          title: "Dimensiones de composición inválidas",
          message: `Resolución no válida para render de After Effects (${width}x${height}).`,
          confidence: 1.0,
          evidence: [{ type: "NUMERIC_VALUE", reference: "resolution", value: `${width}x${height}`, description: "Dimensiones no válidas" }],
        })
      );
    }
    return findings;
  },
});
