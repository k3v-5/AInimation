/**
 * Catálogo de funciones puras de mutación sobre la IR canónica (Fase 18).
 */
export class ProjectMutation {
  public static addElement(project: any, element: any): any {
    const clone = JSON.parse(JSON.stringify(project));
    if (!clone.elements) {
      if (clone.composition && clone.composition.elements) {
        clone.composition.elements.push(element);
      } else {
        clone.elements = [element];
      }
    } else {
      clone.elements.push(element);
    }
    return clone;
  }

  public static removeElement(project: any, elementId: string): any {
    const clone = JSON.parse(JSON.stringify(project));
    if (Array.isArray(clone.elements)) {
      clone.elements = clone.elements.filter((e: any) => e.id !== elementId);
    }
    if (clone.composition && Array.isArray(clone.composition.elements)) {
      clone.composition.elements = clone.composition.elements.filter((e: any) => e.id !== elementId);
    }
    return clone;
  }

  public static updateElementProperty(project: any, elementId: string, propertyPath: string, value: any): any {
    const clone = JSON.parse(JSON.stringify(project));
    const elements = clone.elements ?? clone.composition?.elements ?? clone.composition?.layers ?? [];
    const elem = elements.find((e: any) => e.id === elementId);

    if (elem) {
      const parts = propertyPath.split(".");
      let curr = elem;
      for (let i = 0; i < parts.length - 1; i++) {
        if (!curr[parts[i]]) curr[parts[i]] = {};
        curr = curr[parts[i]];
      }
      curr[parts[parts.length - 1]] = value;
    }

    return clone;
  }
}
