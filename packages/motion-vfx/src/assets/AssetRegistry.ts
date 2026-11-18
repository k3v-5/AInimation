import { AssetNotFoundError, ValidationError } from "../errors/index.js";
import { validateId } from "../validation/validators.js";
import { Asset } from "./Asset.js";
import { AssetValidator } from "./AssetValidator.js";
import { AssetType } from "./types.js";

/**
 * Catálogo central y registro de activos audiovisuales de una composición / proyecto (Fase 5A).
 */
export class AssetRegistry {
  private assets = new Map<string, Asset>();

  /**
   * Cantidad total de recursos registrados.
   */
  public get size(): number {
    return this.assets.size;
  }

  /**
   * Registra un recurso en el catálogo tras validar sus metadatos e ID único.
   */
  public add(asset: Asset): void {
    AssetValidator.validate(asset);

    if (this.assets.has(asset.id)) {
      throw new ValidationError(`Asset with id '${asset.id}' already exists in registry.`);
    }

    this.assets.set(asset.id, {
      id: asset.id,
      type: asset.type,
      ...(asset.name !== undefined ? { name: asset.name } : {}),
      source: { ...asset.source },
      metadata: asset.metadata ? { ...asset.metadata } : undefined,
      ...(asset.status !== undefined ? { status: asset.status } : {}),
    });
  }

  /**
   * Alias de conveniencia para add().
   */
  public register(asset: Asset): void {
    this.add(asset);
  }

  /**
   * Obtiene un recurso por su ID. Retorna undefined si no existe.
   */
  public get(id: string): Asset | undefined {
    const validId = validateId(id, "asset.id");
    const asset = this.assets.get(validId);
    return asset
      ? {
          id: asset.id,
          type: asset.type,
          ...(asset.name !== undefined ? { name: asset.name } : {}),
          source: { ...asset.source },
          metadata: asset.metadata ? { ...asset.metadata } : undefined,
          ...(asset.status !== undefined ? { status: asset.status } : {}),
        }
      : undefined;
  }

  /**
   * Obtiene un recurso por su ID o lanza AssetNotFoundError si no está presente.
   */
  public require(id: string): Asset {
    const asset = this.get(id);
    if (!asset) {
      throw new AssetNotFoundError(id);
    }
    return asset;
  }

  /**
   * Comprueba si un recurso está registrado.
   */
  public has(id: string): boolean {
    const validId = validateId(id, "asset.id");
    return this.assets.has(validId);
  }

  /**
   * Elimina un recurso del registro. Retorna true si fue eliminado.
   */
  public remove(id: string): boolean {
    const validId = validateId(id, "asset.id");
    return this.assets.delete(validId);
  }

  /**
   * Busca recursos por su nombre (el nombre no es la identidad principal).
   */
  public findByName(name: string): Asset[] {
    return Array.from(this.assets.values())
      .filter((a) => a.name === name || a.source.path.endsWith(name))
      .map((a) => ({
        ...a,
        source: { ...a.source },
        metadata: a.metadata ? { ...a.metadata } : undefined,
      }));
  }

  /**
   * Revincula la ruta de un asset existente sin cambiar su ID ni romper referencias.
   */
  public relink(assetId: string, newPath: string): void {
    const validId = validateId(assetId, "asset.id");
    const asset = this.assets.get(validId);
    if (!asset) {
      throw new AssetNotFoundError(assetId);
    }

    asset.source.path = newPath;
    asset.status = "ready";
  }

  /**
   * Comprueba si un asset está siendo utilizado por algún elemento de la escena.
   */
  public isAssetReferenced(assetId: string, elements: { assetId?: string }[]): boolean {
    const validId = validateId(assetId, "asset.id");
    return elements.some((el) => el.assetId === validId);
  }

  /**
   * Obtiene todos los recursos registrados de un tipo específico.
   */
  public getByType(type: AssetType): Asset[] {
    return Array.from(this.assets.values())
      .filter((a) => a.type === type)
      .map((a) => ({
        ...a,
        source: { ...a.source },
        metadata: a.metadata ? { ...a.metadata } : undefined,
      }));
  }

  /**
   * Retorna una lista con todos los activos registrados.
   */
  public list(): Asset[] {
    return Array.from(this.assets.values()).map((a) => ({
      ...a,
      source: { ...a.source },
      metadata: a.metadata ? { ...a.metadata } : undefined,
    }));
  }

  /**
   * Limpia todos los activos del registro.
   */
  public clear(): void {
    this.assets.clear();
  }
}
