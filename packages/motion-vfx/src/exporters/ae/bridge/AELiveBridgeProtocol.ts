export interface JSONRPCRequest<T = Record<string, unknown>> {
  jsonrpc: "2.0";
  id: string | number;
  method: "query_comp" | "patch_property" | "get_render_status" | "exec_extendscript";
  params?: T;
}

export interface JSONRPCResponse<T = unknown> {
  jsonrpc: "2.0";
  id: string | number;
  result?: T;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
}

export interface CompositionState {
  name: string;
  width: number;
  height: number;
  duration: number;
  fps: number;
  layersCount: number;
  layers: Array<{
    index: number;
    name: string;
    enabled: boolean;
    inPoint: number;
    outPoint: number;
    locked: boolean;
  }>;
}

export interface RenderQueueStatus {
  numItems: number;
  isRendering: boolean;
  items: Array<{
    index: number;
    compName: string;
    status: "queued" | "rendering" | "done" | "paused" | "error";
    outputFilePath?: string;
  }>;
}

/**
 * Protocolo de comunicación IPC bidireccional y cliente en tiempo real para Adobe After Effects (Fase 9 / Mejoras).
 * Permite consultar el estado de composiciones activas, parchar propiedades en vivo y monitorear la cola de procesamiento.
 */
export class AELiveBridgeProtocol {
  /**
   * Crea una solicitud formateada en JSON-RPC 2.0.
   */
  public static createRequest<T = Record<string, unknown>>(
    method: JSONRPCRequest["method"],
    params?: T,
    id: string | number = Date.now()
  ): JSONRPCRequest<T> {
    return {
      jsonrpc: "2.0",
      id,
      method,
      params,
    };
  }

  /**
   * Parsea y valida una respuesta JSON-RPC recibida de After Effects.
   */
  public static parseResponse<T = unknown>(jsonStr: string): JSONRPCResponse<T> {
    try {
      const parsed = JSON.parse(jsonStr) as JSONRPCResponse<T>;
      if (parsed.jsonrpc !== "2.0" || parsed.id === undefined) {
        throw new Error("Invalid JSON-RPC 2.0 response format");
      }
      return parsed;
    } catch (err) {
      return {
        jsonrpc: "2.0",
        id: "err",
        error: {
          code: -32700,
          message: `Parse Error: ${err instanceof Error ? err.message : String(err)}`,
        },
      };
    }
  }

  /**
   * Genera el payload de ExtendScript para consultar el estado completo de una composición activa.
   */
  public static buildQueryCompPayload(compNameOrId?: string): string {
    return [
      `(function() {`,
      `  try {`,
      `    var p = app.project;`,
      `    if (!p) return JSON.stringify({ error: "No active project" });`,
      `    var comp = null;`,
      compNameOrId
        ? `    for (var i = 1; i <= p.items.length; i++) { if (p.items[i] instanceof CompItem && (p.items[i].name === "${compNameOrId}" || p.items[i].id == "${compNameOrId}")) { comp = p.items[i]; break; } }`
        : `    comp = p.activeItem instanceof CompItem ? p.activeItem : (p.items.length > 0 && p.items[1] instanceof CompItem ? p.items[1] : null);`,
      `    if (!comp) return JSON.stringify({ error: "No composition found" });`,
      `    var layers = [];`,
      `    for (var j = 1; j <= comp.layers.length; j++) {`,
      `      var l = comp.layers[j];`,
      `      layers.push({ index: l.index, name: l.name, enabled: l.enabled, inPoint: l.inPoint, outPoint: l.outPoint, locked: l.locked });`,
      `    }`,
      `    return JSON.stringify({ name: comp.name, width: comp.width, height: comp.height, duration: comp.duration, fps: comp.frameRate, layersCount: comp.layers.length, layers: layers });`,
      `  } catch(e) { return JSON.stringify({ error: e.toString() }); }`,
      `})();`,
    ].join("\n");
  }

  /**
   * Genera el payload de ExtendScript para actualizar una propiedad en vivo en After Effects sin recargar.
   */
  public static buildPatchPropertyPayload(
    compName: string,
    layerNameOrIndex: string | number,
    propertyPath: string,
    valueLiteral: string
  ): string {
    return [
      `(function() {`,
      `  try {`,
      `    var p = app.project;`,
      `    if (!p) return JSON.stringify({ error: "No active project" });`,
      `    var comp = null;`,
      `    for (var i = 1; i <= p.items.length; i++) { if (p.items[i] instanceof CompItem && p.items[i].name === "${compName}") { comp = p.items[i]; break; } }`,
      `    if (!comp) return JSON.stringify({ error: "Composition not found" });`,
      typeof layerNameOrIndex === "number"
        ? `    var layer = comp.layers[${layerNameOrIndex}];`
        : `    var layer = comp.layers.byName("${layerNameOrIndex}");`,
      `    if (!layer) return JSON.stringify({ error: "Layer not found" });`,
      `    layer.${propertyPath}.setValue(${valueLiteral});`,
      `    return JSON.stringify({ success: true });`,
      `  } catch(e) { return JSON.stringify({ error: e.toString() }); }`,
      `})();`,
    ].join("\n");
  }

  /**
   * Genera el payload de ExtendScript para consultar el estado de la cola de procesamiento (Render Queue).
   */
  public static buildRenderStatusPayload(): string {
    return [
      `(function() {`,
      `  try {`,
      `    var p = app.project;`,
      `    if (!p) return JSON.stringify({ error: "No active project" });`,
      `    var rq = p.renderQueue;`,
      `    var items = [];`,
      `    for (var i = 1; i <= rq.items.length; i++) {`,
      `      var it = rq.items[i];`,
      `      var outPath = "";`,
      `      try { outPath = it.outputModule(1).file ? it.outputModule(1).file.fsName : ""; } catch(oe) {}`,
      `      var st = "queued";`,
      `      if (it.status === RQItemStatus.RENDERING) st = "rendering";`,
      `      else if (it.status === RQItemStatus.DONE) st = "done";`,
      `      else if (it.status === RQItemStatus.ERR_STOPPED) st = "error";`,
      `      items.push({ index: i, compName: it.comp ? it.comp.name : "Unknown", status: st, outputFilePath: outPath });`,
      `    }`,
      `    return JSON.stringify({ numItems: rq.items.length, isRendering: rq.rendering, items: items });`,
      `  } catch(e) { return JSON.stringify({ error: e.toString() }); }`,
      `})();`,
    ].join("\n");
  }
}
