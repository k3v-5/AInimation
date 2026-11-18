import {
  TTSProviderError,
  UnsupportedLocaleError,
} from "../contracts/errors.js";
import { SupportedLocale } from "../contracts/language.types.js";
import { TTSProvider } from "../contracts/voiceover.types.js";
import { SUPPORTED_LOCALES } from "../contracts/vlog.constants.js";

/**
 * Registro y Gestor Central de Proveedores TTS (Milestone 4-02).
 * Desacopla la selección del motor de síntesis, resuelve proveedores por locale
 * y prohíbe selecciones mágicas o fallbacks no autorizados.
 */
export class TTSProviderRegistry {
  private static instance: TTSProviderRegistry;
  private providers = new Map<string, TTSProvider>();

  public static getInstance(): TTSProviderRegistry {
    if (!TTSProviderRegistry.instance) {
      TTSProviderRegistry.instance = new TTSProviderRegistry();
    }
    return TTSProviderRegistry.instance;
  }

  public registerProvider(provider: TTSProvider): void {
    if (!provider || !provider.id) {
      throw new TTSProviderError("unknown", "Invalid TTS provider instance: missing id");
    }
    this.providers.set(provider.id, provider);
  }

  public unregisterProvider(providerId: string): void {
    this.providers.delete(providerId);
  }

  public getProvider(providerId: string): TTSProvider | undefined {
    return this.providers.get(providerId);
  }

  public getAllProviders(): TTSProvider[] {
    return Array.from(this.providers.values());
  }

  public clear(): void {
    this.providers.clear();
  }

  /**
   * Resuelve el proveedor adecuado para un locale y preferencia opcional.
   */
  public resolveProvider(locale: SupportedLocale, preferredProviderId?: string): TTSProvider {
    if (!SUPPORTED_LOCALES.includes(locale)) {
      throw new UnsupportedLocaleError(locale, SUPPORTED_LOCALES);
    }

    // 1. Si se solicita un proveedor específico, verificar que exista y soporte el locale
    if (preferredProviderId) {
      const provider = this.providers.get(preferredProviderId);
      if (!provider) {
        throw new TTSProviderError(preferredProviderId, `Preferred TTS provider '${preferredProviderId}' is not registered`);
      }
      if (!provider.getSupportedLocales().includes(locale)) {
        throw new TTSProviderError(preferredProviderId, `Provider '${preferredProviderId}' does not support locale '${locale}'`);
      }
      return provider;
    }

    // 2. Buscar cualquier proveedor registrado que soporte el locale
    for (const provider of this.providers.values()) {
      if (provider.getSupportedLocales().includes(locale)) {
        return provider;
      }
    }

    throw new TTSProviderError(
      "registry",
      `No registered TTS provider supports locale '${locale}'. Registered: [${Array.from(this.providers.keys()).join(", ")}]`
    );
  }
}
