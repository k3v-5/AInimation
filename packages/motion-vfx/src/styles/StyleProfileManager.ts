import { ColorGradePresetName } from "../effects/color/CinematicColorGradingEngine.js";

export type StylePresetId =
  | "time_editorial_impact"
  | "tiktok_retention_master"
  | "cinematic_luxury"
  | "cyberpunk_stage"
  | "johnny_harris_investigative"
  | "magnates_business_noir"
  | "veritasium_scientific_blueprint"
  | "lemmino_minimalist_cipher"
  | "ali_abdaal_productivity"
  | "iman_gadzhi_agency_luxury"
  | "mrbeast_hyper_retention"
  | "hormozi_cashflow_captions"
  | "true_crime_evidence_room"
  | "cinematic_flow_vlog"
  | "saas_tech_showcase"
  | "wall_street_finance"
  | "sports_energy_fitness"
  | "retro_synthwave_arcade"
  | "time_editorial_poster";

export interface StyleProfile {
  id: StylePresetId;
  name: string;
  description: string;
  typography: {
    fontFamily: string;
    fontWeight: number;
    primaryColor: [number, number, number];
    accentColor: [number, number, number];
    tracking: number;
    verticalStretchPct: number;
    allCaps: boolean;
  };
  colorGrading: {
    preset: ColorGradePresetName;
    vignetteIntensity: number;
    filmGrainEnabled: boolean;
  };
  motion: {
    motionBlur: boolean;
    inertiaBounce: boolean;
    transitionType: "whip" | "zoom" | "cut" | "flash";
    defaultDurationSec: number;
  };
  captions: {
    mode: "karaoke" | "pop_word" | "static";
    activeWordColor: [number, number, number];
    inactiveWordColor: [number, number, number];
    backgroundPill: boolean;
  };
  soundDesign: {
    autoDuckingDb: number;
    whooshEnabled: boolean;
    impactBoomEnabled: boolean;
    uiTicksEnabled: boolean;
  };
}

/**
 * Gestor de Perfiles de Estilo Profesionales (Autonomous MCP v2 / REQ-033).
 * Provee plantillas visuales, tipográficas y sonoras coherentes para aplicar en 1 solo paso.
 */
export class StyleProfileManager {
  private static readonly PROFILES: Record<StylePresetId, StyleProfile> = {
    time_editorial_impact: {
      id: "time_editorial_impact",
      name: "TIME Magazine Editorial Impact",
      description: "Estilo maestro de poster: Tipografía Impact estirada 130%, rojo carmesí #FF1424, blanco puro, ticks vectoriales y motion blur.",
      typography: {
        fontFamily: "Impact",
        fontWeight: 900,
        primaryColor: [1.0, 0.08, 0.14], // Crimson Red
        accentColor: [1.0, 0.78, 0.10], // Gold
        tracking: -15,
        verticalStretchPct: 130,
        allCaps: true,
      },
      colorGrading: {
        preset: "clean_commercial",
        vignetteIntensity: 25,
        filmGrainEnabled: false,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: true,
        transitionType: "whip",
        defaultDurationSec: 0.35,
      },
      captions: {
        mode: "karaoke",
        activeWordColor: [1.0, 0.78, 0.10],
        inactiveWordColor: [0.98, 0.98, 0.98],
        backgroundPill: true,
      },
      soundDesign: {
        autoDuckingDb: -3.5,
        whooshEnabled: true,
        impactBoomEnabled: true,
        uiTicksEnabled: true,
      },
    },

    tiktok_retention_master: {
      id: "tiktok_retention_master",
      name: "TikTok & Reels Retention Master",
      description: "Estilo viral de alta energía con pop-ins elásticos, colores fluorescentes y SFX en cada corte.",
      typography: {
        fontFamily: "Arial Black",
        fontWeight: 900,
        primaryColor: [1.0, 1.0, 0.0], // Neon Yellow
        accentColor: [0.0, 1.0, 0.8], // Cyan
        tracking: -10,
        verticalStretchPct: 110,
        allCaps: true,
      },
      colorGrading: {
        preset: "teal_orange",
        vignetteIntensity: 15,
        filmGrainEnabled: false,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: true,
        transitionType: "zoom",
        defaultDurationSec: 0.25,
      },
      captions: {
        mode: "karaoke",
        activeWordColor: [1.0, 1.0, 0.0],
        inactiveWordColor: [1.0, 1.0, 1.0],
        backgroundPill: true,
      },
      soundDesign: {
        autoDuckingDb: -4.0,
        whooshEnabled: true,
        impactBoomEnabled: true,
        uiTicksEnabled: true,
      },
    },

    cinematic_luxury: {
      id: "cinematic_luxury",
      name: "Cinematic Luxury Commercial",
      description: "Look de película 35mm con negros levantados, cortes elegantes y tipografía minimalista.",
      typography: {
        fontFamily: "Helvetica Neue",
        fontWeight: 700,
        primaryColor: [0.95, 0.95, 0.95],
        accentColor: [0.85, 0.75, 0.55], // Muted Gold
        tracking: 25,
        verticalStretchPct: 100,
        allCaps: false,
      },
      colorGrading: {
        preset: "kodak_35mm",
        vignetteIntensity: 30,
        filmGrainEnabled: true,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: false,
        transitionType: "cut",
        defaultDurationSec: 0.5,
      },
      captions: {
        mode: "pop_word",
        activeWordColor: [1.0, 1.0, 1.0],
        inactiveWordColor: [0.7, 0.7, 0.7],
        backgroundPill: false,
      },
      soundDesign: {
        autoDuckingDb: -2.5,
        whooshEnabled: false,
        impactBoomEnabled: true,
        uiTicksEnabled: false,
      },
    },

    cyberpunk_stage: {
      id: "cyberpunk_stage",
      name: "Cyberpunk Stage & Concert",
      description: "Estética de concierto nocturno con luces rojas/moradas, speed ramping agresivo y resplandor óptico.",
      typography: {
        fontFamily: "Impact",
        fontWeight: 900,
        primaryColor: [1.0, 0.08, 0.14],
        accentColor: [0.8, 0.1, 0.9], // Magenta
        tracking: -5,
        verticalStretchPct: 125,
        allCaps: true,
      },
      colorGrading: {
        preset: "cyberpunk_crimson",
        vignetteIntensity: 45,
        filmGrainEnabled: true,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: true,
        transitionType: "whip",
        defaultDurationSec: 0.3,
      },
      captions: {
        mode: "karaoke",
        activeWordColor: [1.0, 0.08, 0.14],
        inactiveWordColor: [0.9, 0.9, 0.9],
        backgroundPill: true,
      },
      soundDesign: {
        autoDuckingDb: -4.5,
        whooshEnabled: true,
        impactBoomEnabled: true,
        uiTicksEnabled: true,
      },
    },

    johnny_harris_investigative: {
      id: "johnny_harris_investigative",
      name: "The Investigative Cartographer (Johnny Harris / Vox)",
      description: "Mapas 3D topográficos, recortes de documentos históricos con chinchetas, resaltadores analógicos y trazado de rutas vectoriales.",
      typography: {
        fontFamily: "Playfair Display",
        fontWeight: 900,
        primaryColor: [0.102, 0.102, 0.102], // Ink Black
        accentColor: [1.0, 0.898, 0.0], // Highlighter Yellow
        tracking: -5,
        verticalStretchPct: 100,
        allCaps: false,
      },
      colorGrading: {
        preset: "clean_commercial",
        vignetteIntensity: 20,
        filmGrainEnabled: true,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: true,
        transitionType: "whip",
        defaultDurationSec: 0.4,
      },
      captions: {
        mode: "pop_word",
        activeWordColor: [1.0, 0.898, 0.0],
        inactiveWordColor: [0.102, 0.102, 0.102],
        backgroundPill: true,
      },
      soundDesign: {
        autoDuckingDb: -3.5,
        whooshEnabled: true,
        impactBoomEnabled: true,
        uiTicksEnabled: true,
      },
    },

    magnates_business_noir: {
      id: "magnates_business_noir",
      name: "Dark Noir Business Empire (MagnatesMedia / Neo)",
      description: "Documental dramático de negocios, efecto 3D Parallax en fotos, destello anamórfico sobre títulos dorados y viñeta oscura.",
      typography: {
        fontFamily: "Cinzel",
        fontWeight: 900,
        primaryColor: [0.831, 0.686, 0.216], // Metallic Gold
        accentColor: [0.62, 0.106, 0.106], // Crimson Blood
        tracking: 15,
        verticalStretchPct: 105,
        allCaps: true,
      },
      colorGrading: {
        preset: "kodak_35mm",
        vignetteIntensity: 45,
        filmGrainEnabled: true,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: false,
        transitionType: "cut",
        defaultDurationSec: 0.5,
      },
      captions: {
        mode: "pop_word",
        activeWordColor: [0.831, 0.686, 0.216],
        inactiveWordColor: [0.98, 0.98, 0.98],
        backgroundPill: false,
      },
      soundDesign: {
        autoDuckingDb: -4.0,
        whooshEnabled: false,
        impactBoomEnabled: true,
        uiTicksEnabled: true,
      },
    },

    veritasium_scientific_blueprint: {
      id: "veritasium_scientific_blueprint",
      name: "Scientific Blueprint & 3D Isometric (Veritasium / Kurzgesagt)",
      description: "Cuadrículas isométricas, cotas de medición vectorial, resplandor cian y fórmulas matemáticas animadas.",
      typography: {
        fontFamily: "Inter",
        fontWeight: 700,
        primaryColor: [0.024, 0.714, 0.831], // Cyan Neon
        accentColor: [0.976, 0.451, 0.086], // Laser Orange
        tracking: 5,
        verticalStretchPct: 100,
        allCaps: false,
      },
      colorGrading: {
        preset: "clean_commercial",
        vignetteIntensity: 15,
        filmGrainEnabled: false,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: false,
        transitionType: "zoom",
        defaultDurationSec: 0.35,
      },
      captions: {
        mode: "pop_word",
        activeWordColor: [0.024, 0.714, 0.831],
        inactiveWordColor: [1.0, 1.0, 1.0],
        backgroundPill: true,
      },
      soundDesign: {
        autoDuckingDb: -3.0,
        whooshEnabled: true,
        impactBoomEnabled: false,
        uiTicksEnabled: true,
      },
    },

    lemmino_minimalist_cipher: {
      id: "lemmino_minimalist_cipher",
      name: "The Minimalist Cipher (Lemmino / ColdFusion)",
      description: "Overlays de coordenadas GPS, líneas láser de escaneo vertical y tipografía delgada espacial.",
      typography: {
        fontFamily: "DIN",
        fontWeight: 300,
        primaryColor: [0.22, 0.741, 0.973], // Ice Blue
        accentColor: [0.133, 0.773, 0.369], // Radar Green
        tracking: 35,
        verticalStretchPct: 100,
        allCaps: true,
      },
      colorGrading: {
        preset: "kodak_35mm",
        vignetteIntensity: 50,
        filmGrainEnabled: true,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: false,
        transitionType: "cut",
        defaultDurationSec: 0.6,
      },
      captions: {
        mode: "static",
        activeWordColor: [0.22, 0.741, 0.973],
        inactiveWordColor: [0.941, 0.941, 0.941],
        backgroundPill: false,
      },
      soundDesign: {
        autoDuckingDb: -4.0,
        whooshEnabled: false,
        impactBoomEnabled: true,
        uiTicksEnabled: true,
      },
    },

    ali_abdaal_productivity: {
      id: "ali_abdaal_productivity",
      name: "Productivity Papercraft (Ali Abdaal / Thomas Frank)",
      description: "Tarjetas flotantes estilo Notion, texturas de papel, animación con resorte elástico y resaltadores pastel.",
      typography: {
        fontFamily: "Plus Jakarta Sans",
        fontWeight: 600,
        primaryColor: [0.15, 0.15, 0.15], // Pencil Graphite
        accentColor: [0.996, 0.902, 0.541], // Notion Yellow
        tracking: -5,
        verticalStretchPct: 100,
        allCaps: false,
      },
      colorGrading: {
        preset: "clean_commercial",
        vignetteIntensity: 10,
        filmGrainEnabled: false,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: true,
        transitionType: "zoom",
        defaultDurationSec: 0.25,
      },
      captions: {
        mode: "pop_word",
        activeWordColor: [0.996, 0.902, 0.541],
        inactiveWordColor: [0.15, 0.15, 0.15],
        backgroundPill: true,
      },
      soundDesign: {
        autoDuckingDb: -3.0,
        whooshEnabled: true,
        impactBoomEnabled: false,
        uiTicksEnabled: true,
      },
    },

    iman_gadzhi_agency_luxury: {
      id: "iman_gadzhi_agency_luxury",
      name: "High-End Agency & Luxury Monocromo (Iman Gadzhi)",
      description: "Estilo revista de alta moda, marcos de negativo fotográfico 16mm/35mm, tipografía Bodoni y flash frames monocromáticos.",
      typography: {
        fontFamily: "Bodoni MT",
        fontWeight: 700,
        primaryColor: [0.98, 0.98, 0.98], // Pure White
        accentColor: [0.063, 0.725, 0.506], // Emerald Green
        tracking: 20,
        verticalStretchPct: 105,
        allCaps: true,
      },
      colorGrading: {
        preset: "kodak_35mm",
        vignetteIntensity: 35,
        filmGrainEnabled: true,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: false,
        transitionType: "whip",
        defaultDurationSec: 0.35,
      },
      captions: {
        mode: "pop_word",
        activeWordColor: [0.063, 0.725, 0.506],
        inactiveWordColor: [0.98, 0.98, 0.98],
        backgroundPill: false,
      },
      soundDesign: {
        autoDuckingDb: -4.0,
        whooshEnabled: true,
        impactBoomEnabled: true,
        uiTicksEnabled: true,
      },
    },

    mrbeast_hyper_retention: {
      id: "mrbeast_hyper_retention",
      name: "Hyper-Retention Beast (MrBeast / Ryan Trahan)",
      description: "Títulos 3D gigantes con borde negro de 14px, flechas dinámicas de rebote sinusoidal y stickers vectoriales.",
      typography: {
        fontFamily: "Impact",
        fontWeight: 900,
        primaryColor: [0.98, 0.8, 0.082], // Beast Yellow
        accentColor: [0.937, 0.267, 0.267], // Beast Red
        tracking: -5,
        verticalStretchPct: 120,
        allCaps: true,
      },
      colorGrading: {
        preset: "clean_commercial",
        vignetteIntensity: 10,
        filmGrainEnabled: false,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: true,
        transitionType: "zoom",
        defaultDurationSec: 0.2,
      },
      captions: {
        mode: "karaoke",
        activeWordColor: [0.98, 0.8, 0.082],
        inactiveWordColor: [1.0, 1.0, 1.0],
        backgroundPill: true,
      },
      soundDesign: {
        autoDuckingDb: -4.5,
        whooshEnabled: true,
        impactBoomEnabled: true,
        uiTicksEnabled: true,
      },
    },

    hormozi_cashflow_captions: {
      id: "hormozi_cashflow_captions",
      name: "Cashflow Direct-to-Camera (Alex Hormozi)",
      description: "Subtítulos reactivos de alta retención, cajas adaptativas split-box, resaltado en amarillo/verde y punch zooms súbitos.",
      typography: {
        fontFamily: "The Bold Font",
        fontWeight: 900,
        primaryColor: [1.0, 1.0, 1.0],
        accentColor: [0.918, 0.702, 0.031], // Neon Yellow
        tracking: -5,
        verticalStretchPct: 115,
        allCaps: true,
      },
      colorGrading: {
        preset: "clean_commercial",
        vignetteIntensity: 15,
        filmGrainEnabled: false,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: true,
        transitionType: "zoom",
        defaultDurationSec: 0.2,
      },
      captions: {
        mode: "karaoke",
        activeWordColor: [0.918, 0.702, 0.031],
        inactiveWordColor: [1.0, 1.0, 1.0],
        backgroundPill: true,
      },
      soundDesign: {
        autoDuckingDb: -3.5,
        whooshEnabled: true,
        impactBoomEnabled: true,
        uiTicksEnabled: true,
      },
    },

    true_crime_evidence_room: {
      id: "true_crime_evidence_room",
      name: "True Crime & Cold Case Evidence Room",
      description: "Pizarra de corcho con fotos Polaroid conectadas por hilos rojos, expedientes clasificados y sellos de máxima confidencialidad.",
      typography: {
        fontFamily: "Courier Prime",
        fontWeight: 700,
        primaryColor: [0.94, 0.93, 0.9], // Polaroid White
        accentColor: [0.85, 0.12, 0.12], // Evidence Red
        tracking: 5,
        verticalStretchPct: 100,
        allCaps: false,
      },
      colorGrading: {
        preset: "kodak_35mm",
        vignetteIntensity: 55,
        filmGrainEnabled: true,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: false,
        transitionType: "cut",
        defaultDurationSec: 0.6,
      },
      captions: {
        mode: "static",
        activeWordColor: [0.85, 0.12, 0.12],
        inactiveWordColor: [0.94, 0.93, 0.9],
        backgroundPill: true,
      },
      soundDesign: {
        autoDuckingDb: -4.5,
        whooshEnabled: false,
        impactBoomEnabled: true,
        uiTicksEnabled: true,
      },
    },

    cinematic_flow_vlog: {
      id: "cinematic_flow_vlog",
      name: "Cinematic Flow Vlogging (Sam Kolder)",
      description: "Speed ramping orgánico, transiciones de máscara de cielo (Sky Mask), Teal & Orange cinematográfico y títulos 3D en el horizonte.",
      typography: {
        fontFamily: "Futura",
        fontWeight: 700,
        primaryColor: [1.0, 1.0, 1.0],
        accentColor: [0.98, 0.75, 0.4], // Warm Gold
        tracking: 15,
        verticalStretchPct: 100,
        allCaps: true,
      },
      colorGrading: {
        preset: "teal_orange",
        vignetteIntensity: 25,
        filmGrainEnabled: true,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: true,
        transitionType: "whip",
        defaultDurationSec: 0.4,
      },
      captions: {
        mode: "pop_word",
        activeWordColor: [0.98, 0.75, 0.4],
        inactiveWordColor: [1.0, 1.0, 1.0],
        backgroundPill: false,
      },
      soundDesign: {
        autoDuckingDb: -3.0,
        whooshEnabled: true,
        impactBoomEnabled: false,
        uiTicksEnabled: true,
      },
    },

    saas_tech_showcase: {
      id: "saas_tech_showcase",
      name: "SaaS & Tech Interface Showcase",
      description: "Maquetas 3D con Glassmorphism, cursores interactivos con ondas de clic expansivas y degradados de software estilo Stripe.",
      typography: {
        fontFamily: "Inter",
        fontWeight: 600,
        primaryColor: [0.12, 0.16, 0.24], // Slate Text
        accentColor: [0.545, 0.361, 0.965], // Stripe Purple
        tracking: 0,
        verticalStretchPct: 100,
        allCaps: false,
      },
      colorGrading: {
        preset: "clean_commercial",
        vignetteIntensity: 8,
        filmGrainEnabled: false,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: true,
        transitionType: "zoom",
        defaultDurationSec: 0.25,
      },
      captions: {
        mode: "pop_word",
        activeWordColor: [0.545, 0.361, 0.965],
        inactiveWordColor: [0.12, 0.16, 0.24],
        backgroundPill: true,
      },
      soundDesign: {
        autoDuckingDb: -2.5,
        whooshEnabled: true,
        impactBoomEnabled: false,
        uiTicksEnabled: true,
      },
    },

    wall_street_finance: {
      id: "wall_street_finance",
      name: "Wall Street Quantum Finance",
      description: "Velas de trading japonesas animadas, tickers bursátiles numéricos vertiginosos y beeps financieros.",
      typography: {
        fontFamily: "Consolas",
        fontWeight: 700,
        primaryColor: [0.063, 0.725, 0.506], // Bullish Green
        accentColor: [0.937, 0.267, 0.267], // Bearish Red
        tracking: 5,
        verticalStretchPct: 100,
        allCaps: true,
      },
      colorGrading: {
        preset: "clean_commercial",
        vignetteIntensity: 20,
        filmGrainEnabled: false,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: false,
        transitionType: "cut",
        defaultDurationSec: 0.3,
      },
      captions: {
        mode: "pop_word",
        activeWordColor: [0.063, 0.725, 0.506],
        inactiveWordColor: [1.0, 1.0, 1.0],
        backgroundPill: true,
      },
      soundDesign: {
        autoDuckingDb: -3.5,
        whooshEnabled: false,
        impactBoomEnabled: true,
        uiTicksEnabled: true,
      },
    },

    sports_energy_fitness: {
      id: "sports_energy_fitness",
      name: "Sports Energy & Fitness Adrenaline",
      description: "Cronómetros de milisegundos ardiendo, destellos anamórficos, Depth Sandwich freeze-frames y tipografía Teko ultra-pesada.",
      typography: {
        fontFamily: "Teko",
        fontWeight: 700,
        primaryColor: [0.8, 1.0, 0.0], // Volt Yellow
        accentColor: [1.0, 0.34, 0.13], // Blaze Orange
        tracking: 0,
        verticalStretchPct: 130,
        allCaps: true,
      },
      colorGrading: {
        preset: "cyberpunk_crimson",
        vignetteIntensity: 30,
        filmGrainEnabled: true,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: true,
        transitionType: "whip",
        defaultDurationSec: 0.2,
      },
      captions: {
        mode: "karaoke",
        activeWordColor: [0.8, 1.0, 0.0],
        inactiveWordColor: [1.0, 1.0, 1.0],
        backgroundPill: true,
      },
      soundDesign: {
        autoDuckingDb: -4.0,
        whooshEnabled: true,
        impactBoomEnabled: true,
        uiTicksEnabled: true,
      },
    },

    retro_synthwave_arcade: {
      id: "retro_synthwave_arcade",
      name: "Retro Synthwave & Arcade 80s",
      description: "Rejilla de neón en perspectiva hacia un sol retro, aberración cromática RGB Split, tracking VHS y gated reverb snare.",
      typography: {
        fontFamily: "Impact",
        fontWeight: 900,
        primaryColor: [1.0, 0.0, 0.43], // Neon Magenta
        accentColor: [0.0, 0.95, 1.0], // Electric Cyan
        tracking: 10,
        verticalStretchPct: 110,
        allCaps: true,
      },
      colorGrading: {
        preset: "cyberpunk_crimson",
        vignetteIntensity: 40,
        filmGrainEnabled: true,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: false,
        transitionType: "flash",
        defaultDurationSec: 0.5,
      },
      captions: {
        mode: "pop_word",
        activeWordColor: [0.0, 0.95, 1.0],
        inactiveWordColor: [1.0, 0.0, 0.43],
        backgroundPill: false,
      },
      soundDesign: {
        autoDuckingDb: -4.0,
        whooshEnabled: true,
        impactBoomEnabled: true,
        uiTicksEnabled: true,
      },
    },

    time_editorial_poster: {
      id: "time_editorial_poster",
      name: "The TIME Editorial News Poster (Estilo Insignia Maestro)",
      description: "Tipografía Impact ultra-condensada estirada al 140%, marco rojo carmesí #FF1424, interletraje negativo, diales vectoriales y motion blur total.",
      typography: {
        fontFamily: "Impact",
        fontWeight: 900,
        primaryColor: [1.0, 1.0, 1.0], // Pure White
        accentColor: [1.0, 0.078, 0.141], // Crimson Red
        tracking: -5,
        verticalStretchPct: 140,
        allCaps: true,
      },
      colorGrading: {
        preset: "kodak_35mm",
        vignetteIntensity: 35,
        filmGrainEnabled: true,
      },
      motion: {
        motionBlur: true,
        inertiaBounce: true,
        transitionType: "whip",
        defaultDurationSec: 0.3,
      },
      captions: {
        mode: "pop_word",
        activeWordColor: [1.0, 0.078, 0.141],
        inactiveWordColor: [1.0, 1.0, 1.0],
        backgroundPill: true,
      },
      soundDesign: {
        autoDuckingDb: -3.5,
        whooshEnabled: true,
        impactBoomEnabled: true,
        uiTicksEnabled: true,
      },
    },
  };

  public static getProfile(id: StylePresetId): StyleProfile {
    return this.PROFILES[id] ?? this.PROFILES.time_editorial_impact;
  }

  public static getAllProfiles(): StyleProfile[] {
    return Object.values(this.PROFILES);
  }
}
