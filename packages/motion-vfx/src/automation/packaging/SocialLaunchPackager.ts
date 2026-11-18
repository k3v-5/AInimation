import { MotionEngineError } from "../../errors/index.js";

export class PackagingError extends MotionEngineError {
  constructor(message: string, public readonly context?: Record<string, any>) {
    super(`Packaging Error: ${message}`);
  }
}

export interface TitleCandidate {
  variant: "A_CuriosityGap" | "B_ShockValue" | "C_ActionOutcome";
  title: string;
  characterCount: number;
  hookFormula: string;
  estimatedCTRBoostPct: number;
}

export interface YouTubeChapter {
  title: string;
  startTimeSec: number;
}

export interface YouTubeLaunchPackage {
  titleCandidates: TitleCandidate[];
  recommendedTitle: string;
  descriptionWithTimestamps: string;
  tags: string[];
  category: string;
  thumbnailPrompt: {
    heroText: string;
    focalDescription: string;
    contrastColors: [string, string]; // ej. ["#FF1424", "#FFFFFF"]
  };
}

export interface TikTokLaunchPackage {
  captionText: string;
  hashtags: string[];
  callToAction: string;
  soundRecommendation: string;
}

/**
 * Empaquetador determinista de Metadatos, SEO, Capítulos y Títulos High-CTR (Suite de Automatización).
 */
export class SocialLaunchPackager {
  /**
   * Genera 3 variantes de títulos de alto CTR a partir de la temática central y palabras clave.
   */
  public static generateHighCTRTitles(topic: string, keywords: string[] = []): TitleCandidate[] {
    if (!topic || topic.trim().length === 0) {
      throw new PackagingError("Topic cannot be empty.");
    }

    const cleanTopic = topic.trim().toUpperCase();
    const kw = keywords.length > 0 ? keywords[0].toUpperCase() : "ESTO";

    return [
      {
        variant: "A_CuriosityGap",
        title: `EL SECRETO DE ${cleanTopic} QUE NADIE TE CUENTA`,
        characterCount: `EL SECRETO DE ${cleanTopic} QUE NADIE TE CUENTA`.length,
        hookFormula: "Secret / Hidden Truth Gap",
        estimatedCTRBoostPct: 18.5,
      },
      {
        variant: "B_ShockValue",
        title: `POR QUÉ EL 99% FALLA EN ${cleanTopic} (Y CÓMO EVITARLO)`,
        characterCount: `POR QUÉ EL 99% FALLA EN ${cleanTopic} (Y CÓMO EVITARLO)`.length,
        hookFormula: "Negative Bias / Avoid Pain",
        estimatedCTRBoostPct: 24.0,
      },
      {
        variant: "C_ActionOutcome",
        title: `CÓMO DOMINAR ${cleanTopic} EN MENOS DE 10 MINUTOS`,
        characterCount: `CÓMO DOMINAR ${cleanTopic} EN MENOS DE 10 MINUTOS`.length,
        hookFormula: "Direct Benefit / Fast Speed",
        estimatedCTRBoostPct: 15.0,
      },
    ];
  }

  /**
   * Genera el paquete completo de publicación para YouTube con capítulos y descripción SEO.
   */
  public static generateYouTubePackage(
    projectName: string,
    topic: string,
    chapters: YouTubeChapter[],
    customTags: string[] = []
  ): YouTubeLaunchPackage {
    const titleCandidates = this.generateHighCTRTitles(topic, customTags);
    const recommendedTitle = titleCandidates[1].title; // B_ShockValue suele tener mayor retención

    // Formatear timestamps para la descripción
    const timestampLines = chapters.map(ch => {
      const mins = Math.floor(ch.startTimeSec / 60);
      const secs = Math.floor(ch.startTimeSec % 60);
      const timeStr = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
      return `${timeStr} - ${ch.title}`;
    });

    const description = [
      `🔥 ${recommendedTitle}`,
      ``,
      `En este video exploramos a fondo todo sobre ${topic}. Descubre los detalles, secretos y análisis paso a paso.`,
      ``,
      `⏱️ MARCAS DE TIEMPO / CAPÍTULOS:`,
      ...timestampLines,
      ``,
      `📌 SUSCRÍBETE para más contenido exclusivo y activa la campana de notificaciones.`,
      ``,
      `#${topic.replace(/\s+/g, "")} #Documental #Viral #YouTube2026`,
    ].join("\n");

    const defaultTags = [
      topic.toLowerCase(),
      "documental",
      "edicion profesional",
      "after effects",
      "motion graphics",
      ...customTags.map(t => t.toLowerCase()),
    ];

    return {
      titleCandidates,
      recommendedTitle,
      descriptionWithTimestamps: description,
      tags: Array.from(new Set(defaultTags)),
      category: "Film & Animation",
      thumbnailPrompt: {
        heroText: topic.toUpperCase(),
        focalDescription: "Sujeto centrado con alto contraste, recorte de silueta y resplandor perimetral.",
        contrastColors: ["#FF1424", "#FFFFFF"], // TIME Crimson + Pure White
      },
    };
  }

  /**
   * Genera el paquete de publicación para TikTok / Reels / Shorts.
   */
  public static generateTikTokPackage(
    topic: string,
    viralHookText: string,
    nicheTags: string[] = []
  ): TikTokLaunchPackage {
    const hashtags = [
      `#${topic.replace(/\s+/g, "").toLowerCase()}`,
      "#fyp",
      "#parati",
      "#viral",
      "#shorts",
      "#aprendeentiktok",
      ...nicheTags.map(t => `#${t.replace(/\s+/g, "").toLowerCase()}`),
    ];

    return {
      captionText: `⚠️ ${viralHookText} ¿Tú qué opinas? Déjalo en los comentarios 👇`,
      hashtags: Array.from(new Set(hashtags)),
      callToAction: "Comenta y sígueme para la Parte 2",
      soundRecommendation: "Trending Phonk / Dramatic Suspense Bass",
    };
  }
}
