import { SocialLaunchPackager, YouTubeChapter } from "../../automation/packaging/SocialLaunchPackager.js";
import { McpValidationError } from "../errors/mcp-errors.js";

export interface PackageSocialReleaseArgs {
  projectName: string;
  topic: string;
  chapters?: YouTubeChapter[];
  keywords?: string[];
  viralHookText?: string;
}

/**
 * Handler de la herramienta MCP `package_social_release`.
 * Genera el paquete completo de publicación (Títulos A/B High-CTR, descripción con capítulos y hashtags).
 */
export async function handlePackageSocialRelease(rawArgs: unknown) {
  const args = rawArgs as PackageSocialReleaseArgs;
  if (!args || typeof args !== "object" || !args.topic) {
    throw new McpValidationError("A valid 'topic' string is required.");
  }

  const projName = args.projectName ?? "Social_Video_Production";
  const chapters = args.chapters ?? [{ title: "Introducción", startTimeSec: 0 }];
  const hook = args.viralHookText ?? `Descubre la verdad sobre ${args.topic}`;

  const ytPackage = SocialLaunchPackager.generateYouTubePackage(
    projName,
    args.topic,
    chapters,
    args.keywords ?? []
  );

  const ttPackage = SocialLaunchPackager.generateTikTokPackage(
    args.topic,
    hook,
    args.keywords ?? []
  );

  return {
    status: "success",
    youtube: ytPackage,
    tiktok_reels: ttPackage,
  };
}
