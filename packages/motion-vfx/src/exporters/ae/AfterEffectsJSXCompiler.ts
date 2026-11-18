import { Composition } from "../../core/composition.js";
import { Layer } from "../../core/layer.js";
import { BaseElement } from "../../elements/BaseElement.js";
import { MotionEngineError } from "../../errors/index.js";
import { ExportManifest, ExportManifestBuilder } from "../common/ExportManifest.js";
import { AECapabilityAnalyzer } from "./AECapabilityMatrix.js";
import {
  JSXASTBuilder,
  JSXScript,
  JSXStatement,
} from "./JSXAST.js";
import { JSXSerializer } from "./JSXSerializer.js";

export class ExportCapabilityError extends MotionEngineError {
  constructor(message: string, public readonly reportContext?: Record<string, any>) {
    super(`Export Capability Error: ${message}`);
  }
}

export interface JSXCompileOptions {
  strict?: boolean;
  dryRun?: boolean;
  projectId?: string;
  revisionId?: string;
  presetName?: string;
}

export interface JSXCompileResult {
  jsxContent: string;
  manifest: ExportManifest;
  plan: import("../common/CapabilityMatrix.js").ExportPlan;
  warnings: string[];
}

/**
 * Compilador determinista de IR Canónica a After Effects ExtendScript JSX (Fase 17).
 */
export class AfterEffectsJSXCompiler {
  public static readonly EXPORTER_VERSION = "1.7.0";

  /**
   * Compila una composición del core a un script ejecutable de ExtendScript JSX.
   */
  public static compile(comp: Composition, options: JSXCompileOptions = {}): JSXCompileResult {
    const strict = options.strict ?? false;
    const dryRun = options.dryRun ?? false;
    const projectId = options.projectId ?? `proj_${comp.id}`;
    const revisionId = options.revisionId ?? "rev_1";
    const warnings: string[] = [];

    // 1. Análisis de capacidades y plan de exportación (Gate B)
    const plan = AECapabilityAnalyzer.createExportPlan(comp, strict, dryRun);
    if (!plan.canProceed) {
      throw new ExportCapabilityError(
        `Cannot export composition '${comp.name}' in strict mode due to capability mismatches: ${plan.errors.join(", ")}`,
        { plan }
      );
    }

    if (dryRun) {
      const emptyManifest = ExportManifestBuilder.buildManifest({
        exporter: "AfterEffectsJSXCompiler",
        exporterVersion: this.EXPORTER_VERSION,
        sourceIRVersion: "1.7.0",
        projectId,
        revisionId,
        exportedContent: "// DRY RUN",
        primaryFileName: `${comp.name}.jsx`,
        capabilityReport: AECapabilityAnalyzer.getCapabilityReport(),
        warnings: plan.warnings,
      });

      return {
        jsxContent: "// DRY RUN: Export plan created successfully.",
        manifest: emptyManifest,
        plan,
        warnings: plan.warnings,
      };
    }

    // 2. Construir árbol AST tipado
    const statements: JSXStatement[] = [];

    // Comentario inicial del bloque
    statements.push(JSXASTBuilder.comment(`Composition: ${comp.name} (${comp.width}x${comp.height}, ${comp.fps} fps, ${comp.duration}s)`));

    // Variable de proyecto y composición
    statements.push(JSXASTBuilder.varDecl("project", JSXASTBuilder.id("app.project")));
    statements.push(
      JSXASTBuilder.varDecl(
        "comp",
        JSXASTBuilder.call("project.items", "addComp", [
          JSXASTBuilder.str(comp.name),
          JSXASTBuilder.num(comp.width),
          JSXASTBuilder.num(comp.height),
          JSXASTBuilder.num(1.0), // Pixel aspect ratio 1.0 (cuadrado)
          JSXASTBuilder.num(comp.duration),
          JSXASTBuilder.num(comp.fps),
        ])
      )
    );

    // Mapeo de IDs de capa a variables JSX
    const layerVarMap = new Map<string, string>();
    const elements = comp.getElements();
    const layers = comp.getLayers();
    const items = elements.length > 0 ? elements : layers;

    // 3. Compilar capas (respetando orden determinista de stacking)
    for (let lIdx = 0; lIdx < items.length; lIdx++) {
      const item = items[lIdx];
      const layerVar = `layer_${lIdx + 1}`;
      layerVarMap.set(item.id, layerVar);

      statements.push(this.compileItem(item, layerVar, comp));
    }

    // 4. Resolver enlaces de jerarquía (Parenting)
    for (let lIdx = 0; lIdx < items.length; lIdx++) {
      const item = items[lIdx] as any;
      if (item.parentId && layerVarMap.has(item.parentId)) {
        const childVar = layerVarMap.get(item.id)!;
        const parentVar = layerVarMap.get(item.parentId)!;
        statements.push(
          JSXASTBuilder.assign(`${childVar}.parent`, JSXASTBuilder.id(parentVar))
        );
      }
    }

    // 5. Ensamblar Script AST completo
    const script: JSXScript = {
      type: "Script",
      headerComment: `After Effects ExtendScript Export for Composition '${comp.name}'`,
      statements,
    };

    // 6. Serializar mediante JSXSerializer
    const jsxContent = JSXSerializer.serialize(script);

    // 7. Construir Manifiesto Determinista con Hash SHA-256
    const manifest = ExportManifestBuilder.buildManifest({
      exporter: "AfterEffectsJSXCompiler",
      exporterVersion: this.EXPORTER_VERSION,
      sourceIRVersion: "1.7.0",
      projectId,
      revisionId,
      exportedContent: jsxContent,
      primaryFileName: `${comp.name}.jsx`,
      capabilityReport: AECapabilityAnalyzer.getCapabilityReport(),
      warnings: plan.warnings,
    });

    return {
      jsxContent,
      manifest,
      plan,
      warnings: plan.warnings,
    };
  }

  private static compileItem(item: BaseElement | Layer, layerVar: string, comp: Composition): JSXStatement {
    const stmts: JSXStatement[] = [];
    const isElement = item instanceof BaseElement || "transform" in item;
    const duration = isElement
      ? (item as BaseElement).duration
      : ((item as Layer).endTime === Infinity ? comp.duration : (item as Layer).endTime - (item as Layer).startTime);

    // Crear capa sólida por defecto o capa base
    stmts.push(JSXASTBuilder.comment(`Layer [${item.id}] '${item.name}'`));
    stmts.push(
      JSXASTBuilder.varDecl(
        layerVar,
        JSXASTBuilder.call("comp.layers", "addSolid", [
          JSXASTBuilder.arr([
            JSXASTBuilder.num(1.0),
            JSXASTBuilder.num(1.0),
            JSXASTBuilder.num(1.0),
          ]), // Color blanco base
          JSXASTBuilder.str(item.name),
          JSXASTBuilder.num(comp.width),
          JSXASTBuilder.num(comp.height),
          JSXASTBuilder.num(1.0),
          JSXASTBuilder.num(duration > 0 ? duration : comp.duration),
        ])
      )
    );

    // InPoint y OutPoint
    if (item.startTime !== undefined && item.startTime > 0) {
      stmts.push(JSXASTBuilder.assign(`${layerVar}.startTime`, JSXASTBuilder.num(item.startTime)));
    }

    // Compilar Transformaciones (Anchor Point, Position, Scale, Rotation, Opacity)
    if (isElement && (item as BaseElement).transform) {
      const transform = (item as BaseElement).transform;

      // Anchor Point: Convertir de normalizado [0, 1] a coordenadas en píxeles de AE
      const anchorVal = transform.anchorPoint.getValue();
      const anchorPxX = anchorVal.x * comp.width;
      const anchorPxY = anchorVal.y * comp.height;
      stmts.push(
        JSXASTBuilder.call(`${layerVar}.transform.anchorPoint`, "setValue", [
          JSXASTBuilder.arr([JSXASTBuilder.num(anchorPxX), JSXASTBuilder.num(anchorPxY)]),
        ])
      );

      // Position
      const posKeyframes = transform.position.getKeyframes();
      if (posKeyframes.length > 0) {
        for (const kf of posKeyframes) {
          stmts.push(
            JSXASTBuilder.call(`${layerVar}.transform.position`, "setValueAtTime", [
              JSXASTBuilder.num(kf.time),
              JSXASTBuilder.arr([JSXASTBuilder.num(kf.value.x), JSXASTBuilder.num(kf.value.y)]),
            ])
          );
        }
      } else {
        const pos = transform.position.getValue();
        stmts.push(
          JSXASTBuilder.call(`${layerVar}.transform.position`, "setValue", [
            JSXASTBuilder.arr([JSXASTBuilder.num(pos.x), JSXASTBuilder.num(pos.y)]),
          ])
        );
      }

      // Scale
      const scaleKeyframes = transform.scale.getKeyframes();
      if (scaleKeyframes.length > 0) {
        for (const kf of scaleKeyframes) {
          stmts.push(
            JSXASTBuilder.call(`${layerVar}.transform.scale`, "setValueAtTime", [
              JSXASTBuilder.num(kf.time),
              JSXASTBuilder.arr([
                JSXASTBuilder.num(kf.value.x * 100),
                JSXASTBuilder.num(kf.value.y * 100),
              ]),
            ])
          );
        }
      } else {
        const scl = transform.scale.getValue();
        stmts.push(
          JSXASTBuilder.call(`${layerVar}.transform.scale`, "setValue", [
            JSXASTBuilder.arr([JSXASTBuilder.num(scl.x * 100), JSXASTBuilder.num(scl.y * 100)]),
          ])
        );
      }

      // Rotation
      const rotKeyframes = transform.rotation.getKeyframes();
      if (rotKeyframes.length > 0) {
        for (const kf of rotKeyframes) {
          stmts.push(
            JSXASTBuilder.call(`${layerVar}.transform.rotation`, "setValueAtTime", [
              JSXASTBuilder.num(kf.time),
              JSXASTBuilder.num(kf.value),
            ])
          );
        }
      } else {
        const rot = transform.rotation.getValue();
        if (rot !== 0) {
          stmts.push(
            JSXASTBuilder.call(`${layerVar}.transform.rotation`, "setValue", [JSXASTBuilder.num(rot)])
          );
        }
      }

      // Opacity
      const opcKeyframes = transform.opacity.getKeyframes();
      if (opcKeyframes.length > 0) {
        for (const kf of opcKeyframes) {
          stmts.push(
            JSXASTBuilder.call(`${layerVar}.transform.opacity`, "setValueAtTime", [
              JSXASTBuilder.num(kf.time),
              JSXASTBuilder.num(kf.value * 100),
            ])
          );
        }
      } else {
        const opc = transform.opacity.getValue();
        if (opc !== 1.0) {
          stmts.push(
            JSXASTBuilder.call(`${layerVar}.transform.opacity`, "setValue", [
              JSXASTBuilder.num(opc * 100),
            ])
          );
        }
      }
    } else if (!isElement) {
      const layer = item as Layer;
      const posProp = layer.property<any>("position");
      if (posProp) {
        const keyframes = posProp.getKeyframes();
        if (keyframes.length > 0) {
          for (const kf of keyframes) {
            stmts.push(
              JSXASTBuilder.call(`${layerVar}.transform.position`, "setValueAtTime", [
                JSXASTBuilder.num(kf.time),
                JSXASTBuilder.arr([JSXASTBuilder.num(kf.value.x), JSXASTBuilder.num(kf.value.y)]),
              ])
            );
          }
        } else {
          const pos = posProp.getValue();
          if (pos) {
            stmts.push(
              JSXASTBuilder.call(`${layerVar}.transform.position`, "setValue", [
                JSXASTBuilder.arr([JSXASTBuilder.num(pos.x), JSXASTBuilder.num(pos.y)]),
              ])
            );
          }
        }
      }
    }

    return JSXASTBuilder.block(`Setup ${item.name}`, stmts);
  }
}
