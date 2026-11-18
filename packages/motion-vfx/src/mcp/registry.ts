import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { ProjectRuntime } from "../runtime/ProjectRuntime.js";
import {
  CancelOperationInputSchema,
  CloseProjectInputSchema,
  CreateProjectInputSchema,
  DiffProjectRevisionsInputSchema,
  OpenProjectInputSchema,
  RestoreProjectRevisionInputSchema,
  SaveProjectInputSchema,
  ValidateProjectInputSchema,
} from "../schemas/runtime.schema.js";
import { registerLegacyAEBridge } from "./bridge/ae-bridge.js";
import { McpResources } from "./resources/mcp-resources.js";
import { RuntimeMCPResources } from "./resources/runtime-resources.js";
import {
  ApplyViralCaptionStyleSchema,
  CreateVideoFromScriptSchema,
  ExportAfterEffectsJSXSchema,
  GetTimelinePreviewFrameSchema,
} from "./schemas/mcp-tools.schema.js";
import { handleApplyViralCaptionStyle } from "./tools/apply-viral-caption-style.js";
import { handleCancelOperation } from "./tools/cancel-operation.js";
import { handleCloseProject } from "./tools/close-project.js";
import { handleCreateProject } from "./tools/create-project.js";
import { handleCreateVideoFromScript } from "./tools/create-video-from-script.js";
import { handleDiffProjectRevisions } from "./tools/diff-project-revisions.js";
import { handleExportAfterEffectsJSX } from "./tools/export-after-effects-jsx.js";
import { handleGetProjectStatus } from "./tools/get-project-status.js";
import { handleGetTimelinePreviewFrame } from "./tools/get-timeline-preview-frame.js";
import { handleListProjectRevisions } from "./tools/list-project-revisions.js";
import { handleOpenProject } from "./tools/open-project.js";
import { handleRestoreProjectRevision } from "./tools/restore-project-revision.js";
import { handleSaveProject } from "./tools/save-project.js";
import { handleValidateProject } from "./tools/validate-project.js";
import { handleTranscribeLocalAudio } from "./tools/transcribe-local-audio.js";
import { handleDetectViralClips } from "./tools/detect-viral-clips.js";
import { handlePackageSocialRelease } from "./tools/package-social-release.js";
import { handleAutoReframeVideo } from "./tools/auto-reframe-video.js";
import {
  handleVlogClassifyFootage,
  handleVlogGenerateJumpCutPlan,
  handleVlogGetStatus,
  handleVlogMatchBRoll,
  handleVlogProduce,
} from "./tools/vlog-tools.js";
import {
  editorial_compile_data_visualization,
  editorial_dataviz_to_jsx,
  editorial_parse_dataset,
} from "./tools/dataviz-tools.js";
import {
  editorial_run_qa,
  editorial_compare_revisions,
  editorial_get_review_queue,
} from "./tools/qa-tools.js";
import {
  editorial_generate_trim_plan,
  editorial_detect_redundancy,
  editorial_select_best_take,
} from "./tools/performance-tools.js";
import {
  compose_text_behind_subject,
  compose_multi_take_clones,
  detect_subjects_in_clip,
} from "./tools/compositing-tools.js";
import {
  apply_snap_zooms_to_timeline,
  apply_fisheye_optics,
  compile_dolly_zoom,
} from "./tools/optics-tools.js";
import {
  apply_posterize_time,
  compile_speed_ramp_to_beat,
  compile_temporal_orchestration,
} from "./tools/temporal-tools.js";
import {
  apply_film_grain_and_halation,
  apply_auteur_color_grading,
  compile_film_emulation_plan,
} from "./tools/film-tools.js";
import {
  apply_machine_gun_flash_cuts,
  apply_blackout_vacuum_drop,
  compile_syncopated_rhythm_cut,
} from "./tools/rhythm-tools.js";
import {
  apply_brutalist_kinetic_title,
  apply_liquid_chrome_text_effect,
  compile_perspective_anchored_typography,
} from "./tools/kinetic-typography-tools.js";
import {
  apply_snorricam_body_lock,
  apply_infinite_zoom_portal,
  compile_spatial_cinematography_plan,
} from "./tools/spatial-cinematography-tools.js";
import {
  apply_centrifugal_gyro_roll,
  apply_directional_whip_pan,
  compile_dynamic_mechanics_plan,
} from "./tools/dynamic-mechanics-tools.js";
import {
  apply_shutter_drag_echo,
  apply_anamorphic_streak_flare,
  apply_flir_thermal_vision,
  compile_photonics_plan,
} from "./tools/photonics-tools.js";
import {
  apply_manga_impact_frame,
  apply_procedural_speed_lines,
  apply_film_sprocket_holes,
  compile_mixed_media_plan,
} from "./tools/mixed-media-tools.js";
import {
  apply_audio_reactive_physics,
  apply_dynamic_aspect_ratio_breathing,
  apply_datamosh_pframe_glitch,
  compile_stem_kinetics_plan,
} from "./tools/stem-kinetics-tools.js";
import { z } from "zod";

/**
 * Registro centralizado de herramientas y recursos del Model Context Protocol (Fase 17 y 18).
 */
export class McpRegistry {
  private static defaultRuntime = new ProjectRuntime();

  public static registerAll(server: McpServer, runtime: ProjectRuntime = this.defaultRuntime): void {
    // --- HERRAMIENTAS DE FASE 17 ---
    server.tool(
      "create_video_from_script",
      "Orchestrates a complete multi-agent audiovisual project in canonical IR from a creative script or prompt.",
      CreateVideoFromScriptSchema.shape,
      async (args) => {
        try {
          const result = await handleCreateVideoFromScript(args);
          return {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          };
        } catch (error: any) {
          return {
            content: [{ type: "text", text: JSON.stringify({ error: error.message, details: error.details }, null, 2) }],
            isError: true,
          };
        }
      }
    );

    server.tool(
      "export_to_after_effects_jsx",
      "Compiles a canonical project or composition into an executable Adobe After Effects ExtendScript (.jsx) file.",
      ExportAfterEffectsJSXSchema.shape,
      async (args) => {
        try {
          const result = await handleExportAfterEffectsJSX(args);
          return {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          };
        } catch (error: any) {
          return {
            content: [{ type: "text", text: JSON.stringify({ error: error.message, details: error.details }, null, 2) }],
            isError: true,
          };
        }
      }
    );

    server.tool(
      "get_timeline_preview_frame",
      "Inspects the evaluated visual and temporal frame state at timestamp t using the existing canonical engine.",
      GetTimelinePreviewFrameSchema.shape,
      async (args) => {
        try {
          const result = await handleGetTimelinePreviewFrame(args);
          return {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          };
        } catch (error: any) {
          return {
            content: [{ type: "text", text: JSON.stringify({ error: error.message, details: error.details }, null, 2) }],
            isError: true,
          };
        }
      }
    );

    server.tool(
      "apply_viral_caption_style",
      "Applies kinetic typography and caption presets creating a new immutable revision.",
      ApplyViralCaptionStyleSchema.shape,
      async (args) => {
        try {
          const result = await handleApplyViralCaptionStyle(args);
          return {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          };
        } catch (error: any) {
          return {
            content: [{ type: "text", text: JSON.stringify({ error: error.message, details: error.details }, null, 2) }],
            isError: true,
          };
        }
      }
    );

    // --- HERRAMIENTAS DE FASE 18 (RUNTIME & PERSISTENCIA) ---
    server.tool(
      "create_project",
      "Creates a persistent versioned project envelope in the production runtime repository.",
      CreateProjectInputSchema.shape,
      async (args) => {
        try {
          const result = await handleCreateProject(runtime, args);
          return {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          };
        } catch (error: any) {
          return {
            content: [{ type: "text", text: JSON.stringify({ error: error.message, context: error.context }, null, 2) }],
            isError: true,
          };
        }
      }
    );

    server.tool(
      "open_project",
      "Opens an existing persistent project, running recovery if needed, and establishes an active editing session.",
      OpenProjectInputSchema.shape,
      async (args) => {
        try {
          const result = await handleOpenProject(runtime, args);
          return {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          };
        } catch (error: any) {
          return {
            content: [{ type: "text", text: JSON.stringify({ error: error.message, context: error.context }, null, 2) }],
            isError: true,
          };
        }
      }
    );

    server.tool(
      "save_project",
      "Saves a project envelope to persistent storage applying optimistic concurrency checks.",
      SaveProjectInputSchema.shape,
      async (args) => {
        try {
          const result = await handleSaveProject(runtime, args);
          return {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          };
        } catch (error: any) {
          return {
            content: [{ type: "text", text: JSON.stringify({ error: error.message, context: error.context }, null, 2) }],
            isError: true,
          };
        }
      }
    );

    server.tool(
      "close_project",
      "Closes an active project session, releasing concurrency locks safely.",
      CloseProjectInputSchema.shape,
      async (args) => {
        try {
          const result = await handleCloseProject(runtime, args);
          return {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          };
        } catch (error: any) {
          return {
            content: [{ type: "text", text: JSON.stringify({ error: error.message, context: error.context }, null, 2) }],
            isError: true,
          };
        }
      }
    );

    server.tool(
      "get_project_status",
      "Queries the current runtime status, revision HEAD, lock state, and health report of a project.",
      { projectId: CreateProjectInputSchema.shape.name },
      async (args) => {
        try {
          const result = await handleGetProjectStatus(runtime, args);
          return {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          };
        } catch (error: any) {
          return {
            content: [{ type: "text", text: JSON.stringify({ error: error.message, context: error.context }, null, 2) }],
            isError: true,
          };
        }
      }
    );

    server.tool(
      "list_project_revisions",
      "Lists the full immutable revision history for a persistent project.",
      { projectId: CreateProjectInputSchema.shape.name },
      async (args) => {
        try {
          const result = await handleListProjectRevisions(runtime, args);
          return {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          };
        } catch (error: any) {
          return {
            content: [{ type: "text", text: JSON.stringify({ error: error.message, context: error.context }, null, 2) }],
            isError: true,
          };
        }
      }
    );

    server.tool(
      "diff_project_revisions",
      "Calculates a structural and semantic diff between two revisions of a project.",
      DiffProjectRevisionsInputSchema.shape,
      async (args) => {
        try {
          const result = await handleDiffProjectRevisions(runtime, args);
          return {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          };
        } catch (error: any) {
          return {
            content: [{ type: "text", text: JSON.stringify({ error: error.message, context: error.context }, null, 2) }],
            isError: true,
          };
        }
      }
    );

    server.tool(
      "restore_project_revision",
      "Restores a historical revision by creating a new revision containing its content (non-destructive).",
      RestoreProjectRevisionInputSchema.shape,
      async (args) => {
        try {
          const result = await handleRestoreProjectRevision(runtime, args);
          return {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          };
        } catch (error: any) {
          return {
            content: [{ type: "text", text: JSON.stringify({ error: error.message, context: error.context }, null, 2) }],
            isError: true,
          };
        }
      }
    );

    server.tool(
      "validate_project",
      "Executes a comprehensive 6-layer validation on a project without mutating its state.",
      ValidateProjectInputSchema.shape,
      async (args) => {
        try {
          const result = await handleValidateProject(runtime, args);
          return {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          };
        } catch (error: any) {
          return {
            content: [{ type: "text", text: JSON.stringify({ error: error.message, context: error.context }, null, 2) }],
            isError: true,
          };
        }
      }
    );

    server.tool(
      "cancel_operation",
      "Cancels an active long-running runtime operation cooperatively.",
      CancelOperationInputSchema.shape,
      async (args) => {
        try {
          const result = await handleCancelOperation(runtime, args);
          return {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          };
        } catch (error: any) {
          return {
            content: [{ type: "text", text: JSON.stringify({ error: error.message, context: error.context }, null, 2) }],
            isError: true,
          };
        }
      }
    );

    // --- HERRAMIENTAS DE AUTOMATIZACIÓN (Autonomous Content Factory) ---
    server.tool(
      "transcribe_local_audio",
      "Transcribes local video/audio phonetically word-by-word with zero API cost using local Whisper or deterministic synthesis.",
      {
        audioPath: z.string().optional(),
        videoPath: z.string().optional(),
        textFallback: z.string().optional(),
        totalDurationSec: z.number().optional(),
      },
      async (args) => {
        try {
          const result = await handleTranscribeLocalAudio(args);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "detect_viral_clips",
      "Analyzes long-form transcripts and audio energy to extract top viral clips (30s-60s) with virality scoring (0-100).",
      {
        transcriptText: z.string().optional(),
        totalDurationSec: z.number().optional(),
        topK: z.number().optional(),
      },
      async (args) => {
        try {
          const result = await handleDetectViralClips(args);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "package_social_release",
      "Generates 3 A/B High-CTR YouTube titles, chapters description, and TikTok viral hashtags.",
      {
        projectName: z.string().optional(),
        topic: z.string(),
        keywords: z.array(z.string()).optional(),
        viralHookText: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await handlePackageSocialRelease(args);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "auto_reframe_video",
      "Calculates dynamic pan-and-scan or split-screen keyframes to convert 16:9 footage into 9:16 vertical video.",
      {
        mode: z.enum(["dynamic_pan_and_scan", "split_screen_stacked", "blur_background_boxed"]).optional(),
        sourceWidth: z.number().optional(),
        sourceHeight: z.number().optional(),
        targetWidth: z.number().optional(),
        targetHeight: z.number().optional(),
      },
      async (args) => {
        try {
          const result = await handleAutoReframeVideo(args);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    // --- HERRAMIENTAS DE VLOG INTELLIGENCE (Suite v3.5.0) ---
    server.tool(
      "vlog_generate_jump_cut_plan",
      "Calculates silence removal, phonetic word boundary protection, and punch-in keyframes for vlog editing.",
      {
        videoPath: z.string(),
        transcriptText: z.string().optional(),
        totalDurationSec: z.number().optional(),
        silenceThresholdSec: z.number().optional(),
        punchInScale: z.number().optional(),
      },
      async (args) => {
        try {
          const result = await handleVlogGenerateJumpCutPlan(args);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "vlog_classify_footage",
      "Probabilistically classifies raw footage into A-Roll, B-Roll, Timelapse, Action, Photo, or Screen.",
      {
        filePath: z.string(),
        durationSeconds: z.number(),
        hasSpeech: z.boolean().optional(),
        hasFace: z.boolean().optional(),
        hasCameraMotion: z.boolean().optional(),
      },
      async (args) => {
        try {
          const result = await handleVlogClassifyFootage(args);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "vlog_match_broll",
      "Matches and ranks candidate B-Roll footage against a narrative intent text using multicriteria scoring.",
      {
        intentText: z.string(),
        targetDurationSeconds: z.number().optional(),
        availableMedia: z.array(
          z.object({
            id: z.string().optional(),
            filePath: z.string(),
            durationSeconds: z.number(),
            hasAudio: z.boolean().optional(),
          })
        ).optional(),
      },
      async (args) => {
        try {
          const result = await handleVlogMatchBRoll(args);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "vlog_produce",
      "Orchestrates complete multi-lingual autonomous vlog production across 22 phases into After Effects JSX.",
      {
        projectId: z.string(),
        sourceLocale: z.enum(["es-MX", "es-ES", "en-US", "en-GB", "pt-BR", "fr-FR", "de-DE"]).optional(),
        targetLocales: z.array(z.enum(["es-MX", "es-ES", "en-US", "en-GB", "pt-BR", "fr-FR", "de-DE"])).optional(),
        scriptText: z.string(),
        assets: z.array(
          z.object({
            id: z.string(),
            name: z.string(),
            type: z.enum(["A_ROLL", "B_ROLL", "AUDIO_MUSIC", "AUDIO_SFX"]),
            durationSeconds: z.number(),
            filePath: z.string(),
          })
        ).optional(),
        aspectRatios: z.array(z.enum(["16:9", "9:16", "1:1", "4:5", "21:9"])).optional(),
        outputDirectory: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await handleVlogProduce(args);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "vlog_get_status",
      "Retrieves the runtime status, deliverable manifest, and artifacts of a vlog production run.",
      {
        runId: z.string().optional(),
        projectId: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await handleVlogGetStatus(args);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    // --- HERRAMIENTAS DE EDITORIAL INTEL & DATAVIZ (Suite v4.0.0) ---
    server.tool(
      "editorial_compile_data_visualization",
      "Compiles structured datasets into animated After Effects DataViz specifications (Bar charts, Big Stat, Timeline).",
      {
        dataset: z.any().optional(),
        spec: z.any(),
      },
      async (args) => {
        try {
          const result = await editorial_compile_data_visualization(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "editorial_dataviz_to_jsx",
      "Transpiles a DataViz IR AST into executable After Effects ExtendScript JSX.",
      {
        ir: z.any(),
      },
      async (args) => {
        try {
          const result = await editorial_dataviz_to_jsx(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "editorial_parse_dataset",
      "Parses raw CSV or JSON text into a normalized DataSet structure.",
      {
        format: z.enum(["CSV", "JSON"]),
        content: z.string(),
        title: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await editorial_parse_dataset(args);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "editorial_run_qa",
      "Audits an Editorial Document against the comprehensive v4 QA rules (structural, pacing, visual, audio).",
      {
        document: z.any(),
        options: z.any().optional(),
      },
      async (args) => {
        try {
          const result = await editorial_run_qa(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "editorial_compare_revisions",
      "Performs semantic differential analysis between two editorial revisions.",
      {
        before: z.any(),
        after: z.any(),
      },
      async (args) => {
        try {
          const result = await editorial_compare_revisions(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "editorial_generate_trim_plan",
      "Computes intelligent semantic trimming and best take selection across footage segments.",
      {
        segments: z.array(z.any()),
        sourceDurationSeconds: z.number().optional(),
        profile: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await editorial_generate_trim_plan(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "editorial_detect_redundancy",
      "Analyzes and flags semantically redundant arguments and repetitive dialogue.",
      {
        segments: z.array(z.any()),
      },
      async (args) => {
        try {
          const result = await editorial_detect_redundancy(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    // --- HERRAMIENTAS DE COMPOSICIÓN DE SUJETOS Y CLONES (Fase 19) ---
    server.tool(
      "compose_text_behind_subject",
      "Assembles a 3-layer depth sandwich compositing TIME Editorial text physically behind a detected foreground subject with edge feathering.",
      {
        id: z.string(),
        sourceAssetPath: z.string(),
        text: z.string(),
        typography: z
          .object({
            fontFamily: z.string().optional(),
            fontSize: z.number().optional(),
            colorHex: z.string().optional(),
            verticalStretchPercent: z.number().optional(),
            tracking: z.number().optional(),
          })
          .optional(),
        position: z.object({ x: z.number(), y: z.number() }),
        featherPx: z.number().optional(),
        backgroundBlurPx: z.number().optional(),
        inTimeSeconds: z.number().optional(),
        outTimeSeconds: z.number(),
      },
      async (args) => {
        try {
          const result = await compose_text_behind_subject(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "compose_multi_take_clones",
      "Weaves multiple takes of the same subject across different spatial screen zones into a seamless single-plate clone shot.",
      {
        id: z.string(),
        compWidth: z.number().optional(),
        compHeight: z.number().optional(),
        fps: z.number().optional(),
        takes: z.array(z.any()),
        edgeFeatherPx: z.number().optional(),
        totalDurationSeconds: z.number(),
        audioMode: z.enum(["ACTIVE_SPEAKER", "ALL_MIXED", "MASTER_ONLY"]).optional(),
      },
      async (args) => {
        try {
          const result = await compose_multi_take_clones(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "detect_subjects_in_clip",
      "Detects subject bounding boxes and silhouette contour points in a video frame for visual effects anchoring.",
      {
        frameIndex: z.number().optional(),
        timestampSeconds: z.number().optional(),
        compWidth: z.number().optional(),
        compHeight: z.number().optional(),
        zone: z.enum(["LEFT", "CENTER", "RIGHT"]).optional(),
      },
      async (args) => {
        try {
          const result = await detect_subjects_in_clip(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    // --- HERRAMIENTAS DE ÓPTICA Y CÁMARA (Fase 20) ---
    server.tool(
      "apply_snap_zooms_to_timeline",
      "Applies percussive snap/crash zooms with inertial harmonic bounce to beat accents and musical impacts.",
      {
        id: z.string(),
        targetCompWidth: z.number().optional(),
        targetCompHeight: z.number().optional(),
        fps: z.number().optional(),
        snapZooms: z.array(z.any()).optional(),
        fisheye: z.any().optional(),
        dollyZooms: z.array(z.any()).optional(),
        whipPans: z.array(z.any()).optional(),
      },
      async (args) => {
        try {
          const result = await apply_snap_zooms_to_timeline(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "apply_fisheye_optics",
      "Applies 90s-style vintage fisheye barrel distortion, peripheral chromatic aberration, and anamorphic vignette.",
      {
        id: z.string(),
        distortionFactor: z.number().optional(),
        chromaticAberrationPx: z.number().optional(),
        vignetteAmount: z.number().optional(),
      },
      async (args) => {
        try {
          const result = await apply_fisheye_optics(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "compile_dolly_zoom",
      "Computes exact scale compensation curves for a virtual Vertigo Dolly Zoom effect.",
      {
        id: z.string(),
        startTimeSeconds: z.number(),
        durationSeconds: z.number(),
        initialFovDegrees: z.number().optional(),
        finalFovDegrees: z.number().optional(),
        subjectScaleLock: z.boolean().optional(),
      },
      async (args) => {
        try {
          const result = await compile_dolly_zoom(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    // --- HERRAMIENTAS DE MODULACIÓN TEMPORAL (Fase 21) ---
    server.tool(
      "apply_posterize_time",
      "Applies stylized variable frame rates (12fps anime/16mm or 8fps stop-motion) to a target layer.",
      {
        id: z.string(),
        targetFps: z.number().optional(),
      },
      async (args) => {
        try {
          const result = await apply_posterize_time(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "compile_speed_ramp_to_beat",
      "Builds a smooth C^1 time remapping curve accelerating through tension and landing in slow motion on the beat drop.",
      {
        id: z.string(),
        sourceClipDurationSeconds: z.number(),
        targetBeatDropTimeSeconds: z.number(),
        fastMultiplier: z.number().optional(),
        slowMultiplier: z.number().optional(),
        transitionDurationSeconds: z.number().optional(),
        totalTimelineDurationSeconds: z.number(),
      },
      async (args) => {
        try {
          const result = await compile_speed_ramp_to_beat(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "compile_temporal_orchestration",
      "Orchestrates Posterize Time, Speed Ramps, and Stutter Freeze into a unified After Effects plan.",
      {
        id: z.string(),
        posterizeTime: z.any().optional(),
        speedRamps: z.array(z.any()).optional(),
        stutters: z.array(z.any()).optional(),
        fps: z.number().optional(),
      },
      async (args) => {
        try {
          const result = await compile_temporal_orchestration(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    // --- HERRAMIENTAS DE TEXTURA FÍLMICA Y COLOR DE AUTOR (Fase 22) ---
    server.tool(
      "apply_film_grain_and_halation",
      "Applies organic 16mm/35mm film grain and Kodak Vision3 red antihalation glow to high-contrast edges.",
      {
        grain: z.any().optional(),
        halation: z.any().optional(),
      },
      async (args) => {
        try {
          const result = await apply_film_grain_and_halation(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "apply_auteur_color_grading",
      "Applies auteur cinematographic color grading profiles (Tyler Pastel 70s, Kendrick Bleach Bypass BW, Ralphie MiniDV Acid).",
      {
        id: z.string(),
        profile: z.enum(["TYLER_PASTEL_70S", "KENDRICK_BLEACH_BYPASS_BW", "RALPHIE_MINIDV_ACID", "CUSTOM"]),
        saturation: z.number().optional(),
        contrast: z.number().optional(),
        liftPedestal: z.number().optional(),
      },
      async (args) => {
        try {
          const result = await apply_auteur_color_grading(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "compile_film_emulation_plan",
      "Consolidates organic grain, halation, shutter flicker, gate weave, and auteur color grading into an After Effects ExtendScript plan.",
      {
        id: z.string(),
        grain: z.any().optional(),
        halation: z.any().optional(),
        flicker: z.any().optional(),
        colorGrading: z.any().optional(),
      },
      async (args) => {
        try {
          const result = await compile_film_emulation_plan(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    // --- HERRAMIENTAS DE FASE 23: MONTAJE RÍTMICO, FLASH CUTS & BLACKOUT VACUUMS ---
    server.tool(
      "apply_machine_gun_flash_cuts",
      "Generates rapid stroboscopic flash cuts or media interleaving bursts quantized to video frames.",
      {
        burst: z.any(),
        fps: z.number().optional(),
      },
      async (args) => {
        try {
          const result = await apply_machine_gun_flash_cuts(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "apply_blackout_vacuum_drop",
      "Inserts an absolute blackout vacuum window before a musical beat drop with optional 1-frame impact flash.",
      {
        blackout: z.any(),
        fps: z.number().optional(),
      },
      async (args) => {
        try {
          const result = await apply_blackout_vacuum_drop(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "compile_syncopated_rhythm_cut",
      "Assembles a complete rhythm editing sequence with flash bursts and pre-drop blackouts in After Effects.",
      {
        id: z.string(),
        bpm: z.number(),
        fps: z.number().optional(),
        bursts: z.array(z.any()).optional(),
        blackouts: z.array(z.any()).optional(),
        syncopatedCuts: z.array(z.any()).optional(),
      },
      async (args) => {
        try {
          const result = await compile_syncopated_rhythm_cut(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    // --- HERRAMIENTAS DE FASE 24: TIPOGRAFÍA CINÉTICA BRUTALISTA, CROMO LÍQUIDO & PERSPECTIVA 3D ---
    server.tool(
      "apply_brutalist_kinetic_title",
      "Creates an ultra-bold brutalist editorial title with anamorphic vertical stretch, centered anchor point and negative tracking.",
      {
        brutalist: z.any(),
        compVarName: z.string().optional(),
        layerVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await apply_brutalist_kinetic_title(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "apply_liquid_chrome_text_effect",
      "Applies a reflective metallic liquid chrome shader with bevel, turbulent displacement, and specular reflection to text.",
      {
        chrome: z.any(),
        layerVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await apply_liquid_chrome_text_effect(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "compile_perspective_anchored_typography",
      "Consolidates brutalist typography, liquid chrome shader, 3D perspective orientation, and percussive word slam bounce.",
      {
        id: z.string(),
        fps: z.number().optional(),
        brutalist: z.any(),
        chrome: z.any().optional(),
        perspective: z.any().optional(),
        slam: z.any().optional(),
        compVarName: z.string().optional(),
        layerVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await compile_perspective_anchored_typography(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    // --- HERRAMIENTAS DE FASE 25: CINEMATOGRAFÍA ESPACIAL (SNORRICAM, PORTALES & OCCLUSION WIPES) ---
    server.tool(
      "apply_snorricam_body_lock",
      "Locks the subject rigidly to the center of the frame, transferring inertia to the background with motion tile mirror protection.",
      {
        snorricam: z.any(),
        compVarName: z.string().optional(),
        layerVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await apply_snorricam_body_lock(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "apply_infinite_zoom_portal",
      "Generates super-exponential crash zoom wormhole keyframes converging on a microscopic ROI and breaking into the next scene.",
      {
        portal: z.any(),
        fps: z.number().optional(),
        layerVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await apply_infinite_zoom_portal(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "compile_spatial_cinematography_plan",
      "Consolidates Snorricam body lock, infinite zoom portals, and parallax occlusion wipes into an ExtendScript execution plan.",
      {
        id: z.string(),
        fps: z.number().optional(),
        snorricam: z.any().optional(),
        portal: z.any().optional(),
        occlusionWipe: z.any().optional(),
        compVarName: z.string().optional(),
        sourceLayerVarName: z.string().optional(),
        destLayerVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await compile_spatial_cinematography_plan(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    // --- HERRAMIENTAS DE FASE 26: MECÁNICA DE CÁMARA & ÓPTICAS DINÁMICAS (GYRO, WHIP-PANS & BREATHING) ---
    server.tool(
      "apply_centrifugal_gyro_roll",
      "Executes continuous 360 degree centrifugal barrel rolls in Z-axis with circumscribed scaling and mirror edge protection.",
      {
        gyroRoll: z.any(),
        fps: z.number().optional(),
        layerVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await apply_centrifugal_gyro_roll(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "apply_directional_whip_pan",
      "Generates an invisible directional whip-pan match cut with symmetric directional blur and position offset.",
      {
        whipPan: z.any(),
        sourceLayerVarName: z.string().optional(),
        destLayerVarName: z.string().optional(),
        compVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await apply_directional_whip_pan(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "compile_dynamic_mechanics_plan",
      "Consolidates centrifugal gyro rolls, whip-pan match cuts, and procedural lens breathing into an ExtendScript execution plan.",
      {
        id: z.string(),
        fps: z.number().optional(),
        gyroRoll: z.any().optional(),
        whipPan: z.any().optional(),
        lensBreathing: z.any().optional(),
        compVarName: z.string().optional(),
        layerVarName: z.string().optional(),
        sourceLayerVarName: z.string().optional(),
        destLayerVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await compile_dynamic_mechanics_plan(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    // --- HERRAMIENTAS DE FASE 27: NOCTURNAL PHOTONICS & OPTICAL ARTEFACTS ---
    server.tool(
      "apply_shutter_drag_echo",
      "Emulates slow 360-degree shutter drag and kinetic ghosting echo trails via native ADBE Echo with exponential decay.",
      {
        shutterDrag: z.any(),
        layerVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await apply_shutter_drag_echo(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "apply_anamorphic_streak_flare",
      "Generates cylindrical anamorphic horizontal light streak flares with specular highlight isolation and chromatic tint.",
      {
        anamorphicStreak: z.any(),
        compVarName: z.string().optional(),
        layerVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await apply_anamorphic_streak_flare(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "apply_flir_thermal_vision",
      "Applies military FLIR infrared thermal false-color palette mapping with sensor noise and contour edge enhancement.",
      {
        flirThermal: z.any(),
        layerVarName: z.string().optional(),
        compVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await apply_flir_thermal_vision(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "compile_photonics_plan",
      "Consolidates shutter drag echo trails, anamorphic flares, prism star diffraction, and FLIR thermal shaders into an ExtendScript execution plan.",
      {
        id: z.string(),
        fps: z.number().optional(),
        compVarName: z.string().optional(),
        layerVarName: z.string().optional(),
        shutterLayerVarName: z.string().optional(),
        thermalLayerVarName: z.string().optional(),
        shutterDrag: z.any().optional(),
        anamorphicStreak: z.any().optional(),
        prismStar: z.any().optional(),
        flirThermal: z.any().optional(),
      },
      async (args) => {
        try {
          const result = await compile_photonics_plan(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    // --- HERRAMIENTAS DE FASE 28: MIXED-MEDIA & ANIME KINETICS ---
    server.tool(
      "apply_manga_impact_frame",
      "Inserts 1-2 frame stroboscopic manga impact cuts (difference inverted or stark threshold) quantized to exact frame grid.",
      {
        impactFrame: z.any(),
        fps: z.number().optional(),
        compVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await apply_manga_impact_frame(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "apply_procedural_speed_lines",
      "Generates convergent anime speed lines with central subject exclusion zone and 12fps posterized boil modulation.",
      {
        speedLines: z.any(),
        compVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await apply_procedural_speed_lines(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "apply_film_sprocket_holes",
      "Simulates 35mm/16mm celluloid film sprocket holes with marginal KeyKode lab text and organic gate weave jitter.",
      {
        sprocketHoles: z.any(),
        compVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await apply_film_sprocket_holes(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "compile_mixed_media_plan",
      "Consolidates manga impact frames, speed lines, 35mm sprocket holes, paper tear wipes, and doodle boil into an ExtendScript execution plan.",
      {
        id: z.string(),
        fps: z.number().optional(),
        compVarName: z.string().optional(),
        layerVarName: z.string().optional(),
        sourceLayerVarName: z.string().optional(),
        destLayerVarName: z.string().optional(),
        impactFrame: z.any().optional(),
        speedLines: z.any().optional(),
        sprocketHoles: z.any().optional(),
        paperTear: z.any().optional(),
        doodleBoil: z.any().optional(),
      },
      async (args) => {
        try {
          const result = await compile_mixed_media_plan(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    // --- HERRAMIENTAS DE FASE 29: AUDIO STEMS, ASPECT RATIO & DATAMOSH Y2K ---
    server.tool(
      "apply_audio_reactive_physics",
      "Calculates damped viscoelastic elastic bounce scale and chromatic shift reacting to 808 sub-bass hits.",
      {
        subBass: z.any(),
        fps: z.number().optional(),
        layerVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await apply_audio_reactive_physics(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "apply_dynamic_aspect_ratio_breathing",
      "Applies dynamic aspect ratio matte transitions between 9:16, 1:1, 4:3, 16:9, and 2.39:1 anamorphic scope.",
      {
        aspectRatioBreathing: z.any(),
        compVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await apply_dynamic_aspect_ratio_breathing(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "apply_datamosh_pframe_glitch",
      "Emulates Y2K MPEG I-frame loss and macroblock displacement glitch across transition cut points.",
      {
        datamosh: z.any(),
        compVarName: z.string().optional(),
        sourceLayerVarName: z.string().optional(),
        destLayerVarName: z.string().optional(),
      },
      async (args) => {
        try {
          const result = await apply_datamosh_pframe_glitch(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    server.tool(
      "compile_stem_kinetics_plan",
      "Consolidates 808 sub-bass bounce physics, aspect ratio breathing letterbox, and Y2K datamosh into an ExtendScript execution plan.",
      {
        id: z.string(),
        fps: z.number().optional(),
        compVarName: z.string().optional(),
        layerVarName: z.string().optional(),
        sourceLayerVarName: z.string().optional(),
        destLayerVarName: z.string().optional(),
        subBass: z.any().optional(),
        aspectRatioBreathing: z.any().optional(),
        datamosh: z.any().optional(),
      },
      async (args) => {
        try {
          const result = await compile_stem_kinetics_plan(args as any);
          return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
          return { content: [{ type: "text", text: JSON.stringify({ error: error.message }, null, 2) }], isError: true };
        }
      }
    );

    // --- RECURSOS DECLARATIVOS ---
    const resources = McpResources.getStaticResources();
    for (const res of resources) {
      server.resource(res.name, res.uri, async () => {
        return await res.read();
      });
    }

    server.resource("runtime-health", "runtime://health", async () => {
      const text = await RuntimeMCPResources.getResourceContent(runtime, "runtime://health");
      return { contents: [{ uri: "runtime://health", text }] };
    });

    server.resource("runtime-projects", "runtime://projects", async () => {
      const text = await RuntimeMCPResources.getResourceContent(runtime, "runtime://projects");
      return { contents: [{ uri: "runtime://projects", text }] };
    });

    server.resource("runtime-capabilities", "capabilities://runtime", async () => {
      const text = await RuntimeMCPResources.getResourceContent(runtime, "capabilities://runtime");
      return { contents: [{ uri: "capabilities://runtime", text }] };
    });

    // --- BRIDGE LEGADO ---
    registerLegacyAEBridge(server);
  }
}
