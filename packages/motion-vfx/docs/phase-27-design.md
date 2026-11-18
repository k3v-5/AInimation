# Documento de Diseño Técnico: Fase 27 — Standalone CLI, Public TypeScript SDK & Gold Master Certification (v3.0.0)

## 1. Arquitectura del CLI y SDK

```
                       ┌─────────────────────────────────────────┐
                       │          Puntos de Entrada              │
                       ├────────────────────┬────────────────────┤
                       │  CLI Terminal      │  TypeScript SDK    │
                       │ (motion-engine)    │ (@motion-engine)   │
                       └─────────┬──────────┴─────────┬──────────┘
                                 │                    │
                                 ▼                    ▼
                       ┌─────────────────────────────────────────┐
                       │        MotionEngineSDK Facade           │
                       ├─────────────────────────────────────────┤
                       │ • createProject / loadProject           │
                       │ • render / exportAE / exportSocial      │
                       │ • runQA / optimizeVariants / validate   │
                       └──────────────────┬──────────────────────┘
                                          │
                   ┌──────────────────────┼──────────────────────┐
                   ▼                      ▼                      ▼
         ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
         │ RenderingPipeline │  │ AEBridgeManager   │  │SocialDeliveryPack │
         └───────────────────┘  └───────────────────┘  └───────────────────┘
```

---

## 2. Comandos CLI

- `motion-engine render <project.json> --output <out.mp4> [--fps 60] [--workers 4]`
- `motion-engine export-ae <project.json> --output <script.jsx> [--strict]`
- `motion-engine export-social <project.json> --outdir <dir> [--ratios 9:16,16:9,1:1]`
- `motion-engine qa <project.json> [--threshold 0.8]`
- `motion-engine validate <project.json>`
- `motion-engine version`

---

## 3. Contrato del SDK TypeScript (`MotionEngineSDK`)

```typescript
export class MotionEngine {
  public static createProject(options: ProjectOptions): Project;
  public static loadProject(jsonString: string): Project;
  public static render(comp: Composition, options?: RenderOptions): Promise<RenderResult>;
  public static exportAE(comp: Composition, options?: JSXCompileOptions): JSXCompileResult;
  public static deliverSocial(comp: Composition, options?: DeliveryConfig): PackageBuildResult;
  public static runQA(comp: Composition): QAReport;
  public static validate(projectData: unknown): ValidationResult;
}
```
