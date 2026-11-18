import { AssetRegistry } from "../../assets/AssetRegistry.js";
import { Time } from "../../core/types.js";
import { FrameCache } from "../cache/FrameCache.js";
import { Frame, FrameProvider } from "../types/index.js";

/**
 * Gestor de recursos y decodificación en tiempo de ejecución (Fase 5A).
 */
export class ResourceManager {
  private registry: AssetRegistry;
  private cache: FrameCache;
  private customProviders = new Map<string, FrameProvider>();

  constructor(registry: AssetRegistry, maxCacheFrames = 120) {
    this.registry = registry;
    this.cache = new FrameCache(maxCacheFrames);
  }

  /**
   * Registra un proveedor de fotogramas específico para un asset o tipo.
   */
  public registerProvider(assetId: string, provider: FrameProvider): void {
    this.customProviders.set(assetId, provider);
  }

  /**
   * Solicita un fotograma para un asset en el tiempo especificado.
   * Si está en caché lo retorna inmediatamente; de lo contrario, lo genera/decodifica y lo almacena.
   */
  public getFrame(assetId: string, time: Time): Frame {
    // 1. Consultar caché
    const cached = this.cache.get(assetId, time);
    if (cached) {
      return cached;
    }

    // 2. Verificar existencia del activo en el registro
    const asset = this.registry.require(assetId);

    // 3. Obtener del proveedor personalizado o crear fotograma sintético/proxy
    let frame: Frame;
    const provider = this.customProviders.get(assetId);

    if (provider) {
      frame = provider.getFrame(assetId, time);
    } else {
      const width = (asset.metadata as any)?.width ?? 1920;
      const height = (asset.metadata as any)?.height ?? 1080;
      frame = {
        width,
        height,
        format: "rgba8",
        timestamp: time,
      };
    }

    // 4. Guardar en caché y retornar
    this.cache.set(assetId, time, frame);
    return frame;
  }

  public clearCache(): void {
    this.cache.clear();
  }

  public get cacheSize(): number {
    return this.cache.size;
  }
}
