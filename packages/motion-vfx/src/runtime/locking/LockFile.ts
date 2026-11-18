export interface LockMetadata {
  projectId: string;
  owner: string;
  pid: number;
  createdAt: number;
  expiresAt: number;
}

/**
 * Representación del archivo de bloqueo de concurrencia (Fase 18).
 */
export class LockFile {
  public static serialize(meta: LockMetadata): Uint8Array {
    return new TextEncoder().encode(JSON.stringify(meta));
  }

  public static deserialize(bytes: Uint8Array): LockMetadata | null {
    try {
      const str = new TextDecoder("utf-8").decode(bytes);
      return JSON.parse(str) as LockMetadata;
    } catch {
      return null;
    }
  }
}
