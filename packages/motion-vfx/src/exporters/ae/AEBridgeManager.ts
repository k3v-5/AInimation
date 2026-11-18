import { Composition } from "../../core/composition.js";
import { AfterEffectsJSXCompiler, JSXCompileOptions, JSXCompileResult } from "./AfterEffectsJSXCompiler.js";
import { AEExpressionBuilder } from "./expressions/AEExpressionBuilder.js";
import { AEExpressionValidator } from "./expressions/AEExpressionValidator.js";
import { AEShapeCompiler, AEShapeDefinition } from "./shapes/AEShapeCompiler.js";
import { AETemplateImporter, ImportedTemplateResult } from "./importer/AETemplateImporter.js";
import { AEJSXParser, ParsedJSXComposition } from "./importer/AEJSXParser.js";

export class AEBridgeManager {
  /**
   * Compila una composición a script JSX estándar.
   */
  public static compileProject(comp: Composition, options: JSXCompileOptions = {}): JSXCompileResult {
    return AfterEffectsJSXCompiler.compile(comp, options);
  }

  /**
   * Importa un template JSX a una Composition canónica del motor.
   */
  public static importTemplate(jsxContent: string, compIdOverride?: string): ImportedTemplateResult {
    return AETemplateImporter.importTemplate(jsxContent, compIdOverride);
  }

  /**
   * Parsea un script JSX sin instanciar la composición.
   */
  public static parseJSX(jsxContent: string): ParsedJSXComposition {
    return AEJSXParser.parse(jsxContent);
  }

  /**
   * Compila un conjunto de Shape Layers vectoriales a líneas ExtendScript.
   */
  public static compileShapeLayers(compVar: string, layerName: string, shapes: AEShapeDefinition[]): string[] {
    return AEShapeCompiler.compileShapeLayer(compVar, layerName, shapes);
  }

  /**
   * Acceso al generador de expresiones de After Effects.
   */
  public static get expressions() {
    return AEExpressionBuilder;
  }

  /**
   * Acceso al validador de expresiones de After Effects.
   */
  public static validateExpression(expr: string) {
    return AEExpressionValidator.validate(expr);
  }
}
