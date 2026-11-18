import {
  BrutalistTypeSpecInput,
  LiquidChromeSpecInput,
  PerspectiveAnchorSpecInput,
  WordSlamSpecInput,
  BrutalistTypeEngine,
  LiquidChromeEngine,
  PerspectiveAnchorEngine,
  WordSlamEngine,
  KineticTypographyOrchestrator,
  CompileKineticTypographyOptions,
} from "../../kinetic-typography/index.js";

/**
 * REQ-F24: Herramientas MCP para tipografía cinética brutalista, cromo líquido y perspectiva 3D (Fase 24).
 */

export async function apply_brutalist_kinetic_title(params: {
  brutalist: BrutalistTypeSpecInput;
  compVarName?: string;
  layerVarName?: string;
}) {
  const extendScriptLines = BrutalistTypeEngine.exportToExtendScript(params.brutalist, {
    compVarName: params.compVarName,
    layerVarName: params.layerVarName,
  });
  return {
    success: true,
    extendScriptLines,
  };
}

export async function apply_liquid_chrome_text_effect(params: {
  chrome: LiquidChromeSpecInput;
  layerVarName?: string;
}) {
  const extendScriptLines = LiquidChromeEngine.exportToExtendScript(params.chrome, {
    layerVarName: params.layerVarName,
  });
  return {
    success: true,
    extendScriptLines,
  };
}

export async function compile_perspective_anchored_typography(
  params: CompileKineticTypographyOptions
) {
  const plan = KineticTypographyOrchestrator.compilePlan(params);
  return {
    success: true,
    plan,
  };
}
