import { ProjectSnapshot } from "./ProjectSnapshot.js";

/**
 * Utilidad de consulta pura sobre el estado de la IR de un snapshot (Fase 18).
 */
export class ProjectQuery {
  public static getElements(snapshot: ProjectSnapshot): any[] {
    const raw = snapshot.getRawData<any>();
    return raw.elements ?? raw.composition?.elements ?? raw.composition?.layers ?? [];
  }

  public static getElementById(snapshot: ProjectSnapshot, elementId: string): any | undefined {
    const elements = this.getElements(snapshot);
    return elements.find((e: any) => e.id === elementId);
  }

  public static getAssets(snapshot: ProjectSnapshot): any[] {
    const raw = snapshot.getRawData<any>();
    return raw.assets ?? [];
  }

  public static getDuration(snapshot: ProjectSnapshot): number {
    const raw = snapshot.getRawData<any>();
    return raw.composition?.duration ?? raw.duration ?? 0;
  }
}
