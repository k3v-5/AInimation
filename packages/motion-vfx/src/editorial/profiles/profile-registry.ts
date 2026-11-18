import {
  EditorialGenre,
  EditorialProfile,
  EditorialProfileSchema,
} from "../contracts/content-profile.types.js";
import { ProductionIntent } from "../contracts/production-intent.types.js";

/**
 * REQ-001 & REQ-002: Canonical Profiles Registry.
 * Holds deterministic, immutable default configurations for all 10 supported genres.
 */
export class EditorialProfileRegistry {
  private static readonly PROFILES: Record<EditorialGenre, EditorialProfile> = {
    VLOG: {
      genre: "VLOG",
      name: "Vlog & Creator Profile",
      description: "High retention, aggressive pacing, punch-ins, frequent B-roll and fast cuts.",
      pacing: {
        baseShotDurationSeconds: 2.2,
        pacingCurve: "AGGRESSIVE",
        wordsPerMinuteTarget: 175,
      },
      silencePolicy: {
        maxFillerSilenceSeconds: 0.25,
        preserveDramaticPauses: false,
        preserveBreaths: false,
        roomToneReplacement: false,
      },
      shotGrammarPolicy: {
        maxConsecutiveScale: 4,
        preferredProgression: "RHYTHMIC",
        enforceEyelineContinuity: false,
        allowJumpCutsOnAroll: true,
        allowDynamicPunchIn: true,
      },
      brollPolicy: {
        minTalkingHeadDurationBeforeBroll: 4.0,
        maxBrollRepetitionPerFamily: 2,
        selectionMode: "DYNAMIC_FILL",
        precedenceOverPunchIn: true,
      },
      transitionPolicy: {
        preferJCutLcut: false,
        defaultAudioLeadSeconds: 0.0,
        defaultAudioTailSeconds: 0.0,
        allowDissolves: false,
      },
      audioPolicy: {
        roomTonePreservation: false,
        dynamicDucking: true,
        targetDialogueLufs: -16,
      },
    },

    DOCUMENTARY: {
      genre: "DOCUMENTARY",
      name: "Documentary Profile",
      description: "Contemplative, evidence-first, interview pauses preserved with room tone, no jump cuts on dialogue.",
      pacing: {
        baseShotDurationSeconds: 4.5,
        pacingCurve: "CONTEMPLATIVE",
        wordsPerMinuteTarget: 135,
      },
      silencePolicy: {
        maxFillerSilenceSeconds: 0.65,
        preserveDramaticPauses: true,
        preserveBreaths: true,
        roomToneReplacement: true,
      },
      shotGrammarPolicy: {
        maxConsecutiveScale: 2,
        preferredProgression: "WIDE_TO_CLOSE",
        enforceEyelineContinuity: true,
        allowJumpCutsOnAroll: false, // Forbidden on continuous talking head
        allowDynamicPunchIn: false,  // Prohibited in serious documentary
      },
      brollPolicy: {
        minTalkingHeadDurationBeforeBroll: 8.0,
        maxBrollRepetitionPerFamily: 1,
        selectionMode: "SEMANTIC_EVIDENCE",
        precedenceOverPunchIn: true,
      },
      transitionPolicy: {
        preferJCutLcut: true,
        defaultAudioLeadSeconds: 0.45,
        defaultAudioTailSeconds: 0.35,
        allowDissolves: true,
      },
      audioPolicy: {
        roomTonePreservation: true,
        dynamicDucking: true,
        targetDialogueLufs: -20,
      },
    },

    JOURNALISM: {
      genre: "JOURNALISM",
      name: "Investigative Journalism Profile",
      description: "Evidence attribution, chronological integrity, neutral framing and on-screen citations.",
      pacing: {
        baseShotDurationSeconds: 3.5,
        pacingCurve: "MODERATE",
        wordsPerMinuteTarget: 145,
      },
      silencePolicy: {
        maxFillerSilenceSeconds: 0.45,
        preserveDramaticPauses: true,
        preserveBreaths: true,
        roomToneReplacement: true,
      },
      shotGrammarPolicy: {
        maxConsecutiveScale: 3,
        preferredProgression: "WIDE_TO_CLOSE",
        enforceEyelineContinuity: true,
        allowJumpCutsOnAroll: false,
        allowDynamicPunchIn: false,
      },
      brollPolicy: {
        minTalkingHeadDurationBeforeBroll: 6.0,
        maxBrollRepetitionPerFamily: 1,
        selectionMode: "SEMANTIC_EVIDENCE",
        precedenceOverPunchIn: true,
      },
      transitionPolicy: {
        preferJCutLcut: true,
        defaultAudioLeadSeconds: 0.30,
        defaultAudioTailSeconds: 0.20,
        allowDissolves: false,
      },
      audioPolicy: {
        roomTonePreservation: true,
        dynamicDucking: true,
        targetDialogueLufs: -18,
      },
    },

    INTERVIEW: {
      genre: "INTERVIEW",
      name: "Interview & Multi-Cam Profile",
      description: "Speaker tracking, 180-degree axis adherence, reaction shots, protected soundbites.",
      pacing: {
        baseShotDurationSeconds: 5.0,
        pacingCurve: "MODERATE",
        wordsPerMinuteTarget: 150,
      },
      silencePolicy: {
        maxFillerSilenceSeconds: 0.50,
        preserveDramaticPauses: true,
        preserveBreaths: true,
        roomToneReplacement: true,
      },
      shotGrammarPolicy: {
        maxConsecutiveScale: 2,
        preferredProgression: "FREE",
        enforceEyelineContinuity: true,
        allowJumpCutsOnAroll: false,
        allowDynamicPunchIn: false,
      },
      brollPolicy: {
        minTalkingHeadDurationBeforeBroll: 12.0,
        maxBrollRepetitionPerFamily: 1,
        selectionMode: "SEMANTIC_EVIDENCE",
        precedenceOverPunchIn: true,
      },
      transitionPolicy: {
        preferJCutLcut: true,
        defaultAudioLeadSeconds: 0.40,
        defaultAudioTailSeconds: 0.30,
        allowDissolves: false,
      },
      audioPolicy: {
        roomTonePreservation: true,
        dynamicDucking: true,
        targetDialogueLufs: -18,
      },
    },

    EDUCATIONAL: {
      genre: "EDUCATIONAL",
      name: "Educational & Tutorial Profile",
      description: "Cognitive load regulation, concept highlighting, diagrams, explanatory pauses.",
      pacing: {
        baseShotDurationSeconds: 4.0,
        pacingCurve: "MODERATE",
        wordsPerMinuteTarget: 140,
      },
      silencePolicy: {
        maxFillerSilenceSeconds: 0.40,
        preserveDramaticPauses: true,
        preserveBreaths: false,
        roomToneReplacement: true,
      },
      shotGrammarPolicy: {
        maxConsecutiveScale: 3,
        preferredProgression: "RHYTHMIC",
        enforceEyelineContinuity: false,
        allowJumpCutsOnAroll: true,
        allowDynamicPunchIn: true,
      },
      brollPolicy: {
        minTalkingHeadDurationBeforeBroll: 5.0,
        maxBrollRepetitionPerFamily: 2,
        selectionMode: "SEMANTIC_EVIDENCE",
        precedenceOverPunchIn: true,
      },
      transitionPolicy: {
        preferJCutLcut: false,
        defaultAudioLeadSeconds: 0.15,
        defaultAudioTailSeconds: 0.15,
        allowDissolves: false,
      },
      audioPolicy: {
        roomTonePreservation: false,
        dynamicDucking: true,
        targetDialogueLufs: -16,
      },
    },

    NEWS: {
      genre: "NEWS",
      name: "News & Broadcast Profile",
      description: "Fast turnaround, ticker lower-thirds, concise delivery, EBU R128 compliance.",
      pacing: {
        baseShotDurationSeconds: 3.0,
        pacingCurve: "AGGRESSIVE",
        wordsPerMinuteTarget: 165,
      },
      silencePolicy: {
        maxFillerSilenceSeconds: 0.30,
        preserveDramaticPauses: false,
        preserveBreaths: false,
        roomToneReplacement: false,
      },
      shotGrammarPolicy: {
        maxConsecutiveScale: 3,
        preferredProgression: "WIDE_TO_CLOSE",
        enforceEyelineContinuity: true,
        allowJumpCutsOnAroll: false,
        allowDynamicPunchIn: false,
      },
      brollPolicy: {
        minTalkingHeadDurationBeforeBroll: 4.0,
        maxBrollRepetitionPerFamily: 1,
        selectionMode: "DYNAMIC_FILL",
        precedenceOverPunchIn: true,
      },
      transitionPolicy: {
        preferJCutLcut: false,
        defaultAudioLeadSeconds: 0.10,
        defaultAudioTailSeconds: 0.10,
        allowDissolves: false,
      },
      audioPolicy: {
        roomTonePreservation: false,
        dynamicDucking: true,
        targetDialogueLufs: -23, // EBU R128 standard
      },
    },

    CINEMATIC: {
      genre: "CINEMATIC",
      name: "Cinematic & Narrative Short Profile",
      description: "Careful framing, 180-degree axis, match cuts, deep emotional curves, sound design beds.",
      pacing: {
        baseShotDurationSeconds: 5.5,
        pacingCurve: "DYNAMIC_WAVE",
        wordsPerMinuteTarget: 120,
      },
      silencePolicy: {
        maxFillerSilenceSeconds: 0.80,
        preserveDramaticPauses: true,
        preserveBreaths: true,
        roomToneReplacement: true,
      },
      shotGrammarPolicy: {
        maxConsecutiveScale: 2,
        preferredProgression: "WIDE_TO_CLOSE",
        enforceEyelineContinuity: true,
        allowJumpCutsOnAroll: false,
        allowDynamicPunchIn: false,
      },
      brollPolicy: {
        minTalkingHeadDurationBeforeBroll: 10.0,
        maxBrollRepetitionPerFamily: 1,
        selectionMode: "METAPHORIC",
        precedenceOverPunchIn: true,
      },
      transitionPolicy: {
        preferJCutLcut: true,
        defaultAudioLeadSeconds: 0.60,
        defaultAudioTailSeconds: 0.50,
        allowDissolves: true,
      },
      audioPolicy: {
        roomTonePreservation: true,
        dynamicDucking: true,
        targetDialogueLufs: -24,
      },
    },

    CORPORATE: {
      genre: "CORPORATE",
      name: "Corporate & Brand Profile",
      description: "Brand guidelines, polished typography, executive talking heads, professional b-roll.",
      pacing: {
        baseShotDurationSeconds: 3.8,
        pacingCurve: "MODERATE",
        wordsPerMinuteTarget: 145,
      },
      silencePolicy: {
        maxFillerSilenceSeconds: 0.40,
        preserveDramaticPauses: false,
        preserveBreaths: false,
        roomToneReplacement: true,
      },
      shotGrammarPolicy: {
        maxConsecutiveScale: 3,
        preferredProgression: "WIDE_TO_CLOSE",
        enforceEyelineContinuity: true,
        allowJumpCutsOnAroll: false,
        allowDynamicPunchIn: false,
      },
      brollPolicy: {
        minTalkingHeadDurationBeforeBroll: 6.0,
        maxBrollRepetitionPerFamily: 2,
        selectionMode: "DYNAMIC_FILL",
        precedenceOverPunchIn: true,
      },
      transitionPolicy: {
        preferJCutLcut: true,
        defaultAudioLeadSeconds: 0.25,
        defaultAudioTailSeconds: 0.25,
        allowDissolves: true,
      },
      audioPolicy: {
        roomTonePreservation: true,
        dynamicDucking: true,
        targetDialogueLufs: -18,
      },
    },

    SHORT_FORM: {
      genre: "SHORT_FORM",
      name: "Short-Form Social Profile (9:16)",
      description: "Sub-3s hook, rapid visual variety, safe-zone safe, high retention energy.",
      pacing: {
        baseShotDurationSeconds: 1.6,
        pacingCurve: "AGGRESSIVE",
        wordsPerMinuteTarget: 190,
      },
      silencePolicy: {
        maxFillerSilenceSeconds: 0.18,
        preserveDramaticPauses: false,
        preserveBreaths: false,
        roomToneReplacement: false,
      },
      shotGrammarPolicy: {
        maxConsecutiveScale: 4,
        preferredProgression: "RHYTHMIC",
        enforceEyelineContinuity: false,
        allowJumpCutsOnAroll: true,
        allowDynamicPunchIn: true,
      },
      brollPolicy: {
        minTalkingHeadDurationBeforeBroll: 2.5,
        maxBrollRepetitionPerFamily: 2,
        selectionMode: "DYNAMIC_FILL",
        precedenceOverPunchIn: true,
      },
      transitionPolicy: {
        preferJCutLcut: false,
        defaultAudioLeadSeconds: 0.0,
        defaultAudioTailSeconds: 0.0,
        allowDissolves: false,
      },
      audioPolicy: {
        roomTonePreservation: false,
        dynamicDucking: true,
        targetDialogueLufs: -14,
      },
    },

    TECHNICAL: {
      genre: "TECHNICAL",
      name: "Technical & Science Profile",
      description: "Terminology preservation, metric units, data visualizations, sober pacing.",
      pacing: {
        baseShotDurationSeconds: 4.2,
        pacingCurve: "MODERATE",
        wordsPerMinuteTarget: 135,
      },
      silencePolicy: {
        maxFillerSilenceSeconds: 0.45,
        preserveDramaticPauses: true,
        preserveBreaths: false,
        roomToneReplacement: true,
      },
      shotGrammarPolicy: {
        maxConsecutiveScale: 3,
        preferredProgression: "FREE",
        enforceEyelineContinuity: false,
        allowJumpCutsOnAroll: true,
        allowDynamicPunchIn: false,
      },
      brollPolicy: {
        minTalkingHeadDurationBeforeBroll: 6.0,
        maxBrollRepetitionPerFamily: 1,
        selectionMode: "SEMANTIC_EVIDENCE",
        precedenceOverPunchIn: true,
      },
      transitionPolicy: {
        preferJCutLcut: false,
        defaultAudioLeadSeconds: 0.20,
        defaultAudioTailSeconds: 0.20,
        allowDissolves: false,
      },
      audioPolicy: {
        roomTonePreservation: true,
        dynamicDucking: true,
        targetDialogueLufs: -18,
      },
    },
  };

  /**
   * Retrieves a canonical profile by genre.
   */
  public static getProfile(genre: EditorialGenre): EditorialProfile {
    const profile = this.PROFILES[genre];
    if (!profile) {
      throw new Error(`Unsupported editorial genre: ${genre}`);
    }
    // Validate schema guarantee
    return EditorialProfileSchema.parse(profile);
  }

  /**
   * Resolves the profile based on a ProductionIntent.
   * If format is "AUTO", infers the best matching profile from audience and platform.
   */
  public static resolveProfile(intent: ProductionIntent): EditorialProfile {
    if (intent.format !== "AUTO") {
      return this.getProfile(intent.format);
    }

    // Heuristic inference when format is AUTO
    if (intent.platform === "VERTICAL_SOCIAL") {
      return this.getProfile("SHORT_FORM");
    }
    if (intent.primaryObjective === "DOCUMENT") {
      return this.getProfile("DOCUMENTARY");
    }
    if (intent.primaryObjective === "EDUCATE") {
      return this.getProfile("EDUCATIONAL");
    }
    if (intent.audience === "BUSINESS") {
      return this.getProfile("CORPORATE");
    }
    if (intent.audience === "ACADEMIC") {
      return this.getProfile("TECHNICAL");
    }

    // Default to VLOG for general creator content
    return this.getProfile("VLOG");
  }

  /**
   * Returns all 10 canonical profiles.
   */
  public static getAllProfiles(): EditorialProfile[] {
    return Object.values(this.PROFILES).map((p) => EditorialProfileSchema.parse(p));
  }
}
