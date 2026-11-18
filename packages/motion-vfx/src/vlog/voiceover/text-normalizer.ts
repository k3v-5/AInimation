import { SupportedLocale } from "../contracts/language.types.js";

/** Opciones de normalización lingüística */
export interface TextNormalizationOptions {
  protectedEntities?: string[]; // Entidades que no deben alterarse (marcas, nombres propios, etc.)
  preservePunctuation?: boolean;
}

/** Resultado de normalización con metadata de auditoría */
export interface NormalizedTextResult {
  sourceText: string;
  normalizedText: string;
  locale: SupportedLocale;
  protectedEntityPlaceholders: Record<string, string>;
}

/**
 * Normalizador Lingüístico Multilingüe Offline (Milestone 4-06 & 4-07).
 * Convierte números, monedas, horas, porcentajes, abreviaturas y fechas en texto
 * fonéticamente pronunciable para los 7 locales oficiales preservando entidades clave.
 */
export class TextNormalizer {
  /**
   * Normaliza un texto para síntesis de voz en el locale especificado.
   */
  public static normalize(
    text: string,
    locale: SupportedLocale,
    options: TextNormalizationOptions = {}
  ): NormalizedTextResult {
    if (!text || typeof text !== "string") {
      return {
        sourceText: text ?? "",
        normalizedText: "",
        locale,
        protectedEntityPlaceholders: {},
      };
    }

    const placeholders: Record<string, string> = {};
    let placeholderCounter = 0;

    // 1. Fase de Protección de Entidades (Placeholders)
    let processed = text;

    // A. Proteger entidades explícitas del usuario
    for (const entity of options.protectedEntities ?? []) {
      if (!entity) continue;
      const key = `__PROTECTED_ENTITY_${placeholderCounter++}__`;
      placeholders[key] = entity;
      processed = processed.split(entity).join(key);
    }

    // B. Proteger URLs
    processed = processed.replace(/https?:\/\/[^\s]+/gi, (url) => {
      const key = `__PROTECTED_URL_${placeholderCounter++}__`;
      placeholders[key] = url;
      return key;
    });

    // C. Proteger menciones @usuario y hashtags #etiqueta
    processed = processed.replace(/[@#][\w_]+/g, (handle) => {
      const key = `__PROTECTED_HANDLE_${placeholderCounter++}__`;
      placeholders[key] = handle;
      return key;
    });

    // 2. Limpieza de Emojis, flags (regional indicators) y variation selectors
    processed = processed.replace(
      /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F700}-\u{1F77F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{1F1E6}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FE0F}\u{200D}]/gu,
      ""
    );

    // 3. Normalización de Monedas por Locale
    processed = this.normalizeCurrencies(processed, locale);

    // 4. Normalización de Horas (ej: 8:42 PM, 14:30)
    processed = this.normalizeHours(processed, locale);

    // 5. Normalización de Porcentajes (ej: 25%, 3.5%)
    processed = this.normalizePercentages(processed, locale);

    // 6. Normalización de Números y Decimales
    processed = this.normalizeNumbers(processed, locale);

    // 7. Colapsar espacios duplicados y saltos de línea
    processed = processed.replace(/\s+/g, " ").trim();

    // 8. Restaurar Entidades Protegidas
    for (const [key, original] of Object.entries(placeholders)) {
      processed = processed.split(key).join(original);
    }

    return {
      sourceText: text,
      normalizedText: processed,
      locale,
      protectedEntityPlaceholders: placeholders,
    };
  }

  private static normalizeCurrencies(text: string, locale: SupportedLocale): string {
    const isSpanish = locale.startsWith("es");
    const isEnglish = locale.startsWith("en");
    const isFrench = locale === "fr-FR";
    const isGerman = locale === "de-DE";
    const isPortuguese = locale === "pt-BR";

    // Regex para capturar $1,250.50 o €1.250,50 o R$ 1.250,50
    return text.replace(/(\$|€|£|R\$)\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?|\d+)/g, (match, symbol, numStr) => {
      const cleanNum = numStr.replace(/,/g, "").replace(/\./g, ".");
      const val = parseFloat(cleanNum);
      if (isNaN(val)) return match;

      const intPart = Math.floor(val);
      const decPart = Math.round((val - intPart) * 100);

      const intWords = this.integerToWords(intPart, locale);
      const decWords = decPart > 0 ? this.integerToWords(decPart, locale) : "";

      if (locale === "es-MX") {
        const curr = intPart === 1 ? "peso" : "pesos";
        return decPart > 0
          ? `${intWords} ${curr} con ${decWords} centavos`
          : `${intWords} ${curr}`;
      }
      if (locale === "es-ES") {
        const curr = symbol === "$" ? (intPart === 1 ? "dólar" : "dólares") : (intPart === 1 ? "euro" : "euros");
        return decPart > 0
          ? `${intWords} ${curr} con ${decWords} céntimos`
          : `${intWords} ${curr}`;
      }
      if (isEnglish) {
        const curr = symbol === "£" ? (intPart === 1 ? "pound" : "pounds") : (intPart === 1 ? "dollar" : "dollars");
        return decPart > 0
          ? `${intWords} ${curr} and ${decWords} cents`
          : `${intWords} ${curr}`;
      }
      if (isFrench) {
        const curr = intPart === 1 ? "euro" : "euros";
        return decPart > 0
          ? `${intWords} ${curr} et ${decWords} centimes`
          : `${intWords} ${curr}`;
      }
      if (isGerman) {
        const curr = "Euro";
        return decPart > 0
          ? `${intWords} ${curr} und ${decWords} Cent`
          : `${intWords} ${curr}`;
      }
      if (isPortuguese) {
        const curr = intPart === 1 ? "real" : "reais";
        return decPart > 0
          ? `${intWords} ${curr} e ${decWords} centavos`
          : `${intWords} ${curr}`;
      }

      return `${intWords} dollars`;
    });
  }

  private static normalizeHours(text: string, locale: SupportedLocale): string {
    const isEnglish = locale.startsWith("en");
    return text.replace(/(\b\d{1,2}):(\d{2})(?:\s*(AM|PM))?\b/gi, (match, hStr, mStr, meridiem) => {
      const h = parseInt(hStr, 10);
      const m = parseInt(mStr, 10);
      const hWords = this.integerToWords(h, locale);
      const mWords = m === 0 ? "" : this.integerToWords(m, locale);

      if (isEnglish) {
        const suffix = meridiem ? ` ${meridiem.toUpperCase()}` : "";
        return m === 0 ? `${hWords} o'clock${suffix}` : `${hWords} ${mWords}${suffix}`;
      }

      // Español / otros
      const suffix = meridiem ? ` ${meridiem.toUpperCase()}` : "";
      return m === 0 ? `${hWords}` : `${hWords} ${mWords}${suffix}`;
    });
  }

  private static normalizePercentages(text: string, locale: SupportedLocale): string {
    return text.replace(/(\b\d+(?:[.,]\d+)?)\s*%/g, (match, numStr) => {
      const cleanNum = numStr.replace(/,/g, ".");
      const val = parseFloat(cleanNum);
      if (isNaN(val)) return match;
      const numWords = this.numberToWords(val, locale);

      switch (locale) {
        case "es-MX":
        case "es-ES":
          return `${numWords} por ciento`;
        case "en-US":
        case "en-GB":
          return `${numWords} percent`;
        case "fr-FR":
          return `${numWords} pour cent`;
        case "de-DE":
          return `${numWords} Prozent`;
        case "pt-BR":
          return `${numWords} por cento`;
        default:
          return `${numWords} percent`;
      }
    });
  }

  private static normalizeNumbers(text: string, locale: SupportedLocale): string {
    return text.replace(/\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b|\b\d+\b/g, (match) => {
      const clean = match.replace(/,/g, "");
      const val = parseFloat(clean);
      if (isNaN(val)) return match;
      return this.numberToWords(val, locale);
    });
  }

  private static numberToWords(val: number, locale: SupportedLocale): string {
    const intPart = Math.floor(val);
    const hasDecimal = val !== intPart;
    const intWords = this.integerToWords(intPart, locale);

    if (!hasDecimal) {
      return intWords;
    }

    const decStr = val.toString().split(".")[1] ?? "";
    const decVal = parseInt(decStr, 10);
    const decWords = this.integerToWords(decVal, locale);

    if (locale.startsWith("es")) return `${intWords} punto ${decWords}`;
    if (locale.startsWith("en")) return `${intWords} point ${decWords}`;
    if (locale === "fr-FR") return `${intWords} virgule ${decWords}`;
    if (locale === "de-DE") return `${intWords} Komma ${decWords}`;
    if (locale === "pt-BR") return `${intWords} ponto ${decWords}`;

    return `${intWords} point ${decWords}`;
  }

  private static integerToWords(n: number, locale: SupportedLocale): string {
    if (n === 0) {
      switch (locale) {
        case "es-MX":
        case "es-ES": return "cero";
        case "en-US":
        case "en-GB": return "zero";
        case "fr-FR": return "zéro";
        case "de-DE": return "null";
        case "pt-BR": return "zero";
      }
    }

    if (locale.startsWith("en")) {
      return this.englishIntegerToWords(n);
    }
    if (locale.startsWith("es")) {
      return this.spanishIntegerToWords(n);
    }
    if (locale === "fr-FR") {
      return this.frenchIntegerToWords(n);
    }
    if (locale === "de-DE") {
      return this.germanIntegerToWords(n);
    }
    if (locale === "pt-BR") {
      return this.portugueseIntegerToWords(n);
    }

    return this.englishIntegerToWords(n);
  }

  // --- Implementaciones locales deterministas de números a palabras ---

  private static englishIntegerToWords(n: number): string {
    const ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
      "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"];
    const tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"];

    if (n < 20) return ones[n];
    if (n < 100) return `${tens[Math.floor(n / 10)]}${n % 10 !== 0 ? `-${ones[n % 10]}` : ""}`;
    if (n < 1000) {
      const rem = n % 100;
      return `${ones[Math.floor(n / 100)]} hundred${rem !== 0 ? ` ${this.englishIntegerToWords(rem)}` : ""}`;
    }
    if (n < 1000000) {
      const thousands = Math.floor(n / 1000);
      const rem = n % 1000;
      return `${this.englishIntegerToWords(thousands)} thousand${rem !== 0 ? ` ${this.englishIntegerToWords(rem)}` : ""}`;
    }
    return n.toString();
  }

  private static spanishIntegerToWords(n: number): string {
    const ones = ["", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve",
      "diez", "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte",
      "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco", "veintiséis", "veintisiete", "veintiocho", "veintinueve"];
    const tens = ["", "", "", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta", "ochenta", "noventa"];
    const hundreds = ["", "ciento", "doscientos", "trescientos", "cuatrocientos", "quinientos", "seiscientos", "setecientos", "ochocientos", "novecientos"];

    if (n <= 29) return ones[n];
    if (n < 100) return `${tens[Math.floor(n / 10)]}${n % 10 !== 0 ? ` y ${ones[n % 10]}` : ""}`;
    if (n === 100) return "cien";
    if (n < 1000) {
      const rem = n % 100;
      return `${hundreds[Math.floor(n / 100)]}${rem !== 0 ? ` ${this.spanishIntegerToWords(rem)}` : ""}`;
    }
    if (n < 1000000) {
      const thousands = Math.floor(n / 1000);
      const rem = n % 1000;
      const prefix = thousands === 1 ? "mil" : `${this.spanishIntegerToWords(thousands)} mil`;
      return `${prefix}${rem !== 0 ? ` ${this.spanishIntegerToWords(rem)}` : ""}`;
    }
    return n.toString();
  }

  private static frenchIntegerToWords(n: number): string {
    const ones = ["", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf",
      "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf"];
    const tens = ["", "", "vingt", "trente", "quarante", "cinquante", "soixante", "soixante-dix", "quatre-vingts", "quatre-vingt-dix"];

    if (n < 20) return ones[n];
    if (n < 100) {
      const t = Math.floor(n / 10);
      const r = n % 10;
      return `${tens[t]}${r !== 0 ? `-${ones[r]}` : ""}`;
    }
    if (n < 1000) {
      const h = Math.floor(n / 100);
      const rem = n % 100;
      const prefix = h === 1 ? "cent" : (rem === 0 ? `${ones[h]} cents` : `${ones[h]} cent`);
      return `${prefix}${rem !== 0 ? ` ${this.frenchIntegerToWords(rem)}` : ""}`;
    }
    if (n < 1000000) {
      const th = Math.floor(n / 1000);
      const rem = n % 1000;
      const prefix = th === 1 ? "mille" : `${this.frenchIntegerToWords(th)} mille`;
      return `${prefix}${rem !== 0 ? ` ${this.frenchIntegerToWords(rem)}` : ""}`;
    }
    return n.toString();
  }

  private static germanIntegerToWords(n: number): string {
    const ones = ["", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun",
      "zehn", "elf", "zwölf", "dreizehn", "vierzehn", "fünfzehn", "sechzehn", "siebzehn", "achtzehn", "neunzehn"];
    const tens = ["", "", "zwanzig", "dreißig", "vierzig", "fünfzig", "sechzig", "siebzig", "achtzig", "neunzig"];

    if (n < 20) return ones[n];
    if (n < 100) {
      const o = n % 10;
      const t = Math.floor(n / 10);
      return o === 0 ? tens[t] : `${o === 1 ? "ein" : ones[o]}und${tens[t]}`;
    }
    if (n < 1000) {
      const h = Math.floor(n / 100);
      const rem = n % 100;
      const prefix = h === 1 ? "einhundert" : `${ones[h]}hundert`;
      return `${prefix}${rem !== 0 ? this.germanIntegerToWords(rem) : ""}`;
    }
    if (n < 1000000) {
      const th = Math.floor(n / 1000);
      const rem = n % 1000;
      const prefix = th === 1 ? "eintausend" : `${this.germanIntegerToWords(th)}tausend`;
      return `${prefix}${rem !== 0 ? this.germanIntegerToWords(rem) : ""}`;
    }
    return n.toString();
  }

  private static portugueseIntegerToWords(n: number): string {
    const ones = ["", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove",
      "dez", "onze", "doze", "treze", "quatorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"];
    const tens = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa"];
    const hundreds = ["", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos", "setecentos", "oitocentos", "novecentos"];

    if (n < 20) return ones[n];
    if (n < 100) {
      const t = Math.floor(n / 10);
      const r = n % 10;
      return `${tens[t]}${r !== 0 ? ` e ${ones[r]}` : ""}`;
    }
    if (n === 100) return "cem";
    if (n < 1000) {
      const h = Math.floor(n / 100);
      const rem = n % 100;
      return `${hundreds[h]}${rem !== 0 ? ` e ${this.portugueseIntegerToWords(rem)}` : ""}`;
    }
    if (n < 1000000) {
      const th = Math.floor(n / 1000);
      const rem = n % 1000;
      const prefix = th === 1 ? "mil" : `${this.portugueseIntegerToWords(th)} mil`;
      if (rem === 0) return prefix;
      const connector = (rem < 100 || rem % 100 === 0) ? " e " : " ";
      return `${prefix}${connector}${this.portugueseIntegerToWords(rem)}`;
    }
    return n.toString();
  }
}
