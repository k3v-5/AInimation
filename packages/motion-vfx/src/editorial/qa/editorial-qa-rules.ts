import { QAHash } from "./qa-hash.js";
import { EditorialQARegistry, EditorialQARule } from "./editorial-qa-registry.js";
import { EditorialIssue, EditorialQAContext } from "./editorial-qa-types.js";

// ============================================================================
// 1. STRUCTURE RULES
// ============================================================================

export const QA_STRUCT_001: EditorialQARule = {
  id: "QA-STRUCT-001",
  version: "1.0.0",
  category: "STRUCTURE",
  defaultSeverity: "BLOCKING",
  description: "Validar existencia de timeline principal y propiedades esenciales.",
  enabledByDefault: true,
  evaluate(ctx: EditorialQAContext): EditorialIssue[] {
    const issues: EditorialIssue[] = [];
    const irId = ctx.ir.projectId ?? (ctx.ir as any).id ?? "project";
    const tracks = ctx.ir.tracks ?? (ctx.ir as any).timeline?.tracks;
    if (!tracks) {
      issues.push({
        id: QAHash.createIssueId({ ruleId: "QA-STRUCT-001", entityIds: [irId], fingerprint: "missing_timeline" }),
        ruleId: "QA-STRUCT-001",
        severity: "BLOCKING",
        category: "STRUCTURE",
        entityIds: [irId],
        title: "Timeline Ausente",
        message: `El proyecto '${irId}' carece de estructura de pistas/timeline.`,
        confidence: 1.0,
        autoFixAvailable: false,
        fingerprint: "missing_timeline",
      });
    }
    return issues;
  },
};

export const QA_STRUCT_002: EditorialQARule = {
  id: "QA-STRUCT-002",
  version: "1.0.0",
  category: "STRUCTURE",
  defaultSeverity: "BLOCKING",
  description: "Validar existencia de pistas (tracks) en el timeline.",
  enabledByDefault: true,
  evaluate(ctx: EditorialQAContext): EditorialIssue[] {
    const issues: EditorialIssue[] = [];
    const irId = ctx.ir.projectId ?? (ctx.ir as any).id ?? "project";
    const tracks = ctx.ir.tracks ?? (ctx.ir as any).timeline?.tracks;
    if (!tracks || tracks.length === 0) {
      issues.push({
        id: QAHash.createIssueId({ ruleId: "QA-STRUCT-002", entityIds: [irId], fingerprint: "empty_tracks" }),
        ruleId: "QA-STRUCT-002",
        severity: "BLOCKING",
        category: "STRUCTURE",
        entityIds: [irId],
        title: "Pistas Ausentes",
        message: `El timeline del proyecto '${irId}' no contiene ninguna pista.`,
        confidence: 1.0,
        autoFixAvailable: false,
        fingerprint: "empty_tracks",
      });
    }
    return issues;
  },
};

export const QA_STRUCT_003: EditorialQARule = {
  id: "QA-STRUCT-003",
  version: "1.0.0",
  category: "STRUCTURE",
  defaultSeverity: "BLOCKING",
  description: "Validar unicidad de identificadores de pistas y clips.",
  enabledByDefault: true,
  evaluate(ctx: EditorialQAContext): EditorialIssue[] {
    const issues: EditorialIssue[] = [];
    const seenIds = new Set<string>();
    const tracks = ctx.ir.tracks ?? (ctx.ir as any).timeline?.tracks ?? [];

    for (const track of tracks) {
      if (seenIds.has(track.id)) {
        issues.push({
          id: QAHash.createIssueId({ ruleId: "QA-STRUCT-003", entityIds: [track.id], fingerprint: `dupe_track_${track.id}` }),
          ruleId: "QA-STRUCT-003",
          severity: "BLOCKING",
          category: "STRUCTURE",
          entityIds: [track.id],
          title: "ID de Pista Duplicado",
          message: `El track ID '${track.id}' está duplicado.`,
          confidence: 1.0,
          autoFixAvailable: false,
          fingerprint: `dupe_track_${track.id}`,
        });
      }
      seenIds.add(track.id);

      for (const clip of track.clips ?? []) {
        if (seenIds.has(clip.id)) {
          issues.push({
            id: QAHash.createIssueId({ ruleId: "QA-STRUCT-003", entityIds: [clip.id], fingerprint: `dupe_clip_${clip.id}` }),
            ruleId: "QA-STRUCT-003",
            severity: "BLOCKING",
            category: "STRUCTURE",
            entityIds: [clip.id],
            title: "ID de Clip Duplicado",
            message: `El clip ID '${clip.id}' está duplicado.`,
            confidence: 1.0,
            autoFixAvailable: false,
            fingerprint: `dupe_clip_${clip.id}`,
          });
        }
        seenIds.add(clip.id);
      }
    }
    return issues;
  },
};

// ============================================================================
// 2. TIMING RULES
// ============================================================================

export const QA_TIME_001: EditorialQARule = {
  id: "QA-TIME-001",
  version: "1.0.0",
  category: "TIMING",
  defaultSeverity: "BLOCKING",
  description: "Bloquear duración negativa en clips o timeline.",
  enabledByDefault: true,
  evaluate(ctx: EditorialQAContext): EditorialIssue[] {
    const issues: EditorialIssue[] = [];
    const tracks = ctx.ir.tracks ?? (ctx.ir as any).timeline?.tracks ?? [];
    for (const track of tracks) {
      for (const clip of track.clips ?? []) {
        if (clip.timelineRange && clip.timelineRange.durationSeconds <= 0) {
          issues.push({
            id: QAHash.createIssueId({ ruleId: "QA-TIME-001", entityIds: [clip.id], fingerprint: `neg_dur_${clip.id}` }),
            ruleId: "QA-TIME-001",
            severity: "BLOCKING",
            category: "TIMING",
            entityIds: [clip.id],
            timestampSeconds: clip.timelineRange.startSeconds,
            durationSeconds: clip.timelineRange.durationSeconds,
            title: "Duración Inválida",
            message: `El clip '${clip.id}' tiene duración no positiva (${clip.timelineRange.durationSeconds}s).`,
            expected: "> 0",
            actual: clip.timelineRange.durationSeconds,
            confidence: 1.0,
            autoFixAvailable: false,
            fingerprint: `neg_dur_${clip.id}`,
          });
        }
      }
    }
    return issues;
  },
};

export const QA_TIME_002: EditorialQARule = {
  id: "QA-TIME-002",
  version: "1.0.0",
  category: "TIMING",
  defaultSeverity: "BLOCKING",
  description: "Bloquear inicio negativo o huecos de inicio en pista principal continua.",
  enabledByDefault: true,
  evaluate(ctx: EditorialQAContext): EditorialIssue[] {
    const issues: EditorialIssue[] = [];
    const tracks = ctx.ir.tracks ?? (ctx.ir as any).timeline?.tracks ?? [];
    for (const track of tracks) {
      const isPrimary = (track as any).type === "VIDEO_PRIMARY" || track.id === "v_primary";
      const clips = track.clips ?? [];

      for (let i = 0; i < clips.length; i++) {
        const clip = clips[i];
        if (!clip.timelineRange) continue;

        if (clip.timelineRange.startSeconds < 0) {
          issues.push({
            id: QAHash.createIssueId({ ruleId: "QA-TIME-002", entityIds: [clip.id], fingerprint: `neg_start_${clip.id}` }),
            ruleId: "QA-TIME-002",
            severity: "BLOCKING",
            category: "TIMING",
            entityIds: [clip.id],
            timestampSeconds: clip.timelineRange.startSeconds,
            title: "Inicio Negativo de Clip",
            message: `El clip '${clip.id}' inicia en tiempo negativo (${clip.timelineRange.startSeconds}s).`,
            expected: ">= 0",
            actual: clip.timelineRange.startSeconds,
            confidence: 1.0,
            autoFixAvailable: false,
            fingerprint: `neg_start_${clip.id}`,
          });
        }

        // Head gap detection on primary track
        if (isPrimary && i === 0 && clip.timelineRange.startSeconds > 0) {
          issues.push({
            id: QAHash.createIssueId({ ruleId: "QA-TIME-002", entityIds: [clip.id], fingerprint: `head_gap_${clip.id}` }),
            ruleId: "QA-TIME-002",
            severity: "BLOCKING",
            category: "TIMING",
            entityIds: [clip.id],
            timestampSeconds: 0,
            durationSeconds: clip.timelineRange.startSeconds,
            title: "Hueco en Cabecera de Pista Principal",
            message: `Pista principal contiene un hueco no permitido de ${clip.timelineRange.startSeconds}s al inicio.`,
            expected: 0,
            actual: clip.timelineRange.startSeconds,
            confidence: 1.0,
            autoFixAvailable: true,
            fingerprint: `head_gap_${clip.id}`,
          });
        }
      }
    }
    return issues;
  },
};

export const QA_TIME_004: EditorialQARule = {
  id: "QA-TIME-004",
  version: "1.0.0",
  category: "TIMING",
  defaultSeverity: "BLOCKING",
  description: "Detectar solapamiento ilegal de clips en la misma pista.",
  enabledByDefault: true,
  evaluate(ctx: EditorialQAContext): EditorialIssue[] {
    const issues: EditorialIssue[] = [];
    const tracks = ctx.ir.tracks ?? (ctx.ir as any).timeline?.tracks ?? [];
    for (const track of tracks) {
      const sortedClips = [...(track.clips ?? [])].sort(
        (a, b) => (a.timelineRange?.startSeconds ?? 0) - (b.timelineRange?.startSeconds ?? 0)
      );

      for (let i = 0; i < sortedClips.length - 1; i++) {
        const c1 = sortedClips[i];
        const c2 = sortedClips[i + 1];
        if (!c1.timelineRange || !c2.timelineRange) continue;

        const end1 = c1.timelineRange.startSeconds + c1.timelineRange.durationSeconds;
        if (end1 > c2.timelineRange.startSeconds + 1e-6) {
          issues.push({
            id: QAHash.createIssueId({ ruleId: "QA-TIME-004", entityIds: [c1.id, c2.id], fingerprint: `overlap_${c1.id}_${c2.id}` }),
            ruleId: "QA-TIME-004",
            severity: "BLOCKING",
            category: "TIMING",
            entityIds: [c1.id, c2.id],
            timestampSeconds: c2.timelineRange.startSeconds,
            title: "Solapamiento Ilegal de Clips",
            message: `Los clips '${c1.id}' y '${c2.id}' se solapan en la pista '${track.id}' (${end1.toFixed(3)}s > ${c2.timelineRange.startSeconds.toFixed(3)}s).`,
            confidence: 1.0,
            autoFixAvailable: true,
            fingerprint: `overlap_${c1.id}_${c2.id}`,
          });
        }
      }
    }
    return issues;
  },
};

// ============================================================================
// 3. MEDIA RULES
// ============================================================================

export const QA_ASSET_001: EditorialQARule = {
  id: "QA-ASSET-001",
  version: "1.0.0",
  category: "MEDIA",
  defaultSeverity: "BLOCKING",
  description: "Todo clip debe tener un assetId válido y no vacío.",
  enabledByDefault: true,
  evaluate(ctx: EditorialQAContext): EditorialIssue[] {
    const issues: EditorialIssue[] = [];
    const tracks = ctx.ir.tracks ?? (ctx.ir as any).timeline?.tracks ?? [];
    for (const track of tracks) {
      for (const clip of track.clips ?? []) {
        if (!clip.assetId || clip.assetId.trim() === "") {
          issues.push({
            id: QAHash.createIssueId({ ruleId: "QA-ASSET-001", entityIds: [clip.id], fingerprint: `empty_asset_${clip.id}` }),
            ruleId: "QA-ASSET-001",
            severity: "BLOCKING",
            category: "MEDIA",
            entityIds: [clip.id],
            title: "Asset ID Ausente",
            message: `El clip '${clip.id}' no tiene asignado un assetId válido.`,
            confidence: 1.0,
            autoFixAvailable: false,
            fingerprint: `empty_asset_${clip.id}`,
          });
        }
      }
    }
    return issues;
  },
};

export const QA_MEDIA_001: EditorialQARule = {
  id: "QA-MEDIA-001",
  version: "1.0.0",
  category: "MEDIA",
  defaultSeverity: "BLOCKING",
  description: "Todo assetId utilizado debe resolver contra el registro de assets.",
  enabledByDefault: true,
  evaluate(ctx: EditorialQAContext): EditorialIssue[] {
    const issues: EditorialIssue[] = [];
    if (!ctx.assetRegistry) return issues;
    const tracks = ctx.ir.tracks ?? (ctx.ir as any).timeline?.tracks ?? [];

    for (const track of tracks) {
      for (const clip of track.clips ?? []) {
        if (clip.assetId && !ctx.assetRegistry[clip.assetId]?.exists) {
          issues.push({
            id: QAHash.createIssueId({ ruleId: "QA-MEDIA-001", entityIds: [clip.id, clip.assetId], fingerprint: `missing_asset_${clip.assetId}` }),
            ruleId: "QA-MEDIA-001",
            severity: "BLOCKING",
            category: "MEDIA",
            entityIds: [clip.id, clip.assetId],
            title: "Asset No Registrado",
            message: `El clip '${clip.id}' referencia un asset inexistente '${clip.assetId}'.`,
            confidence: 1.0,
            autoFixAvailable: false,
            fingerprint: `missing_asset_${clip.assetId}`,
          });
        }
      }
    }
    return issues;
  },
};

// ============================================================================
// 4. AUDIO RULES
// ============================================================================

export const QA_AUDIO_001: EditorialQARule = {
  id: "QA-AUDIO-001",
  version: "1.0.0",
  category: "AUDIO",
  defaultSeverity: "WARNING",
  description: "Detectar clipping acústico lógico o volumen superior a 0 dB.",
  enabledByDefault: true,
  evaluate(ctx: EditorialQAContext): EditorialIssue[] {
    const issues: EditorialIssue[] = [];
    const tracks = ctx.ir.tracks ?? (ctx.ir as any).timeline?.tracks ?? [];
    for (const track of tracks) {
      for (const clip of track.clips ?? []) {
        if (clip.volumeDb !== undefined && clip.volumeDb > 0.0) {
          issues.push({
            id: QAHash.createIssueId({ ruleId: "QA-AUDIO-001", entityIds: [clip.id], fingerprint: `clipping_${clip.id}` }),
            ruleId: "QA-AUDIO-001",
            severity: "WARNING",
            category: "AUDIO",
            entityIds: [clip.id],
            title: "Clipping de Audio Detectado",
            message: `El clip '${clip.id}' tiene volumen excesivo (+${clip.volumeDb} dB).`,
            expected: "<= 0.0 dB",
            actual: `${clip.volumeDb} dB`,
            confidence: 0.95,
            autoFixAvailable: true,
            recommendation: "Ajustar volumen a <= 0 dB para evitar distorsión digital.",
            fingerprint: `clipping_${clip.id}`,
          });
        }
      }
    }
    return issues;
  },
};

export const QA_AUDIO_005: EditorialQARule = {
  id: "QA-AUDIO-005",
  version: "1.0.0",
  category: "AUDIO",
  defaultSeverity: "WARNING",
  description: "Detectar conflicto entre voz y música sin atenuación (ducking).",
  enabledByDefault: true,
  evaluate(ctx: EditorialQAContext): EditorialIssue[] {
    const issues: EditorialIssue[] = [];
    const tracks = ctx.ir.tracks ?? (ctx.ir as any).timeline?.tracks ?? [];
    const speechClips = tracks
      .filter((t: any) => t.type === "AUDIO_DIALOGUE" || t.type === "AUDIO_VOICE" || t.type === "AUDIO_SPEECH")
      .flatMap((t: any) => t.clips ?? []);

    const musicClips = tracks
      .filter((t: any) => t.type === "AUDIO_MUSIC")
      .flatMap((t: any) => t.clips ?? []);

    for (const sc of speechClips) {
      for (const mc of musicClips) {
        if (!sc.timelineRange || !mc.timelineRange) continue;
        const scEnd = sc.timelineRange.startSeconds + sc.timelineRange.durationSeconds;
        const mcEnd = mc.timelineRange.startSeconds + mc.timelineRange.durationSeconds;
        const overlaps = Math.max(0, Math.min(scEnd, mcEnd) - Math.max(sc.timelineRange.startSeconds, mc.timelineRange.startSeconds));

        if (overlaps > 1.0 && (mc.volumeDb ?? 0) > -12.0) {
          issues.push({
            id: QAHash.createIssueId({ ruleId: "QA-AUDIO-005", entityIds: [sc.id, mc.id], fingerprint: `ducking_${sc.id}_${mc.id}` }),
            ruleId: "QA-AUDIO-005",
            severity: "WARNING",
            category: "AUDIO",
            entityIds: [sc.id, mc.id],
            timestampSeconds: sc.timelineRange.startSeconds,
            durationSeconds: overlaps,
            title: "Conflicto Voz / Música",
            message: `Música sin atenuar (${mc.volumeDb ?? 0} dB) compite con voz inteligible en el clip '${sc.id}'.`,
            confidence: 0.88,
            autoFixAvailable: true,
            recommendation: "Aplicar auto-ducking de -18 dB en pista musical durante alocución.",
            fingerprint: `ducking_${sc.id}_${mc.id}`,
          });
        }
      }
    }
    return issues;
  },
};

// ============================================================================
// 5. EVIDENCE RULES
// ============================================================================

export const QA_EVIDENCE_001: EditorialQARule = {
  id: "QA-EVIDENCE-001",
  version: "1.0.0",
  category: "EVIDENCE",
  defaultSeverity: "BLOCKING",
  description: "Toda afirmación verificable debe poseer evidencia asociada válida.",
  enabledByDefault: true,
  evaluate(ctx: EditorialQAContext): EditorialIssue[] {
    const issues: EditorialIssue[] = [];

    // Check evidenceReport from evaluation context
    const evReport = (ctx as any).evidenceReport;
    if (evReport && Array.isArray(evReport.audits)) {
      for (const audit of evReport.audits) {
        if (audit.blockingIssue || audit.status === "MISSING_SOURCE" || (!audit.hasEvidence && audit.requiresCitation)) {
          issues.push({
            id: QAHash.createIssueId({ ruleId: "QA-EVIDENCE-001", entityIds: [audit.claimId], fingerprint: `unsupported_audit_${audit.claimId}` }),
            ruleId: "QA-EVIDENCE-001",
            severity: "BLOCKING",
            category: "EVIDENCE",
            entityIds: [audit.claimId],
            title: "Afirmación Factual Sin Evidencia",
            message: `El claim '${audit.claimId}' ('${audit.claimText}') carece de fuentes de evidencia respaldadas.`,
            confidence: audit.confidence ?? 1.0,
            autoFixAvailable: false,
            fingerprint: `unsupported_audit_${audit.claimId}`,
          });
        }
      }
    }

    // Also check claims directly on IR
    const claims = (ctx.ir as any).claims ?? [];
    for (const claim of claims) {
      if (claim.isVerifiable && (!claim.evidenceIds || claim.evidenceIds.length === 0)) {
        issues.push({
          id: QAHash.createIssueId({ ruleId: "QA-EVIDENCE-001", entityIds: [claim.id], fingerprint: `unsupported_claim_${claim.id}` }),
          ruleId: "QA-EVIDENCE-001",
          severity: "BLOCKING",
          category: "EVIDENCE",
          entityIds: [claim.id],
          title: "Afirmación Factual Sin Evidencia",
          message: `El claim '${claim.id}' ('${claim.statement}') carece de fuentes de evidencia respaldadas.`,
          confidence: 1.0,
          autoFixAvailable: false,
          fingerprint: `unsupported_claim_${claim.id}`,
        });
      }
    }
    return issues;
  },
};

// ============================================================================
// 6. COGNITIVE LOAD RULES
// ============================================================================

export const QA_LOAD_001: EditorialQARule = {
  id: "QA-LOAD-001",
  version: "1.0.0",
  category: "COGNITIVE_LOAD",
  defaultSeverity: "WARNING",
  description: "Detectar sobrecarga cognitiva sostenida C(t) >= 0.85 durante >= 3 segundos.",
  enabledByDefault: true,
  evaluate(ctx: EditorialQAContext): EditorialIssue[] {
    const issues: EditorialIssue[] = [];
    const maxLoad = ctx.config?.thresholds?.maxCognitiveLoad ?? 0.85;
    const cognitiveSamples = (ctx.ir as any).metrics?.cognitiveLoadSamples ?? [];

    let overloadStart: number | null = null;

    for (const sample of cognitiveSamples) {
      if (sample.load >= maxLoad) {
        if (overloadStart === null) overloadStart = sample.t;
      } else {
        if (overloadStart !== null) {
          const duration = sample.t - overloadStart;
          if (duration >= 3.0) {
            const irId = ctx.ir.projectId ?? (ctx.ir as any).id ?? "proj";
            issues.push({
              id: QAHash.createIssueId({ ruleId: "QA-LOAD-001", entityIds: [irId], timestampSeconds: overloadStart, fingerprint: `load_${overloadStart}` }),
              ruleId: "QA-LOAD-001",
              severity: "WARNING",
              category: "COGNITIVE_LOAD",
              entityIds: [irId],
              timestampSeconds: overloadStart,
              durationSeconds: duration,
              title: "Sobrecarga Cognitiva Sostenida",
              message: `Carga cognitiva C(t) >= ${maxLoad} sostenida durante ${duration.toFixed(1)}s en t=${overloadStart}s.`,
              expected: { maxLoad },
              actual: { load: maxLoad, durationSeconds: duration },
              confidence: 0.9,
              autoFixAvailable: true,
              recommendation: "Insertar plano de respiro o reducir densidad visual.",
              fingerprint: `load_${overloadStart}`,
            });
          }
          overloadStart = null;
        }
      }
    }
    return issues;
  },
};

// ============================================================================
// 7. PACING RULES
// ============================================================================

export const QA_PACE_001: EditorialQARule = {
  id: "QA-PACE-001",
  version: "1.0.0",
  category: "PACING",
  defaultSeverity: "WARNING",
  description: "Detectar desalineación de ritmo editorial respecto a la curva objetivo.",
  enabledByDefault: true,
  evaluate(ctx: EditorialQAContext): EditorialIssue[] {
    const issues: EditorialIssue[] = [];
    const minAlignment = ctx.config?.thresholds?.minPacingAlignment ?? 0.65;
    const currentScore = (ctx.ir as any).metrics?.pacingAlignmentScore;

    if (currentScore !== undefined && currentScore < minAlignment) {
      const irId = ctx.ir.projectId ?? (ctx.ir as any).id ?? "proj";
      issues.push({
        id: QAHash.createIssueId({ ruleId: "QA-PACE-001", entityIds: [irId], fingerprint: `pacing_${currentScore}` }),
        ruleId: "QA-PACE-001",
        severity: "WARNING",
        category: "PACING",
        entityIds: [irId],
        title: "Desalineación de Ritmo Editorial",
        message: `El ritmo editorial tiene un alignmentScore de ${currentScore.toFixed(2)}, por debajo del umbral mínimo (${minAlignment}).`,
        expected: `>= ${minAlignment}`,
        actual: currentScore,
        confidence: 0.85,
        autoFixAvailable: true,
        recommendation: "Ajustar duración de planos para sincronizar con la curva de tensión.",
        fingerprint: `pacing_${currentScore}`,
      });
    }
    return issues;
  },
};

// ============================================================================
// REGISTRO DE TODAS LAS REGLAS CANÓNICAS
// ============================================================================

export function registerAllRules(): void {
  EditorialQARegistry.register(QA_STRUCT_001);
  EditorialQARegistry.register(QA_STRUCT_002);
  EditorialQARegistry.register(QA_STRUCT_003);
  EditorialQARegistry.register(QA_TIME_001);
  EditorialQARegistry.register(QA_TIME_002);
  EditorialQARegistry.register(QA_TIME_004);
  EditorialQARegistry.register(QA_ASSET_001);
  EditorialQARegistry.register(QA_MEDIA_001);
  EditorialQARegistry.register(QA_AUDIO_001);
  EditorialQARegistry.register(QA_AUDIO_005);
  EditorialQARegistry.register(QA_EVIDENCE_001);
  EditorialQARegistry.register(QA_LOAD_001);
  EditorialQARegistry.register(QA_PACE_001);
}

// Auto-register upon load
registerAllRules();
