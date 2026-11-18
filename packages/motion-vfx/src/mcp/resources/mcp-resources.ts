import { ViralCaptionPresetRegistry } from "../../captions/presets/ViralCaptionPresets.js";
import { AECapabilityAnalyzer } from "../../exporters/ae/AECapabilityMatrix.js";
import { EDLExporter } from "../../exporters/edl/EDLExporter.js";
import { FCPXMLExporter } from "../../exporters/fcpxml/FCPXMLExporter.js";
import { McpProjectNotFoundError } from "../errors/mcp-errors.js";
import { MCPProjectStore } from "../types.js";

export interface McpResourceDefinition {
  uri: string;
  name: string;
  mimeType: string;
  description: string;
  read: () => Promise<{ contents: Array<{ uri: string; mimeType: string; text: string }> }>;
}

/**
 * Recursos declarativos e inspección MCP (Fase 17).
 */
export class McpResources {
  public static getStaticResources(): McpResourceDefinition[] {
    return [
      {
        uri: "capabilities://after-effects",
        name: "After Effects Capabilities Report",
        mimeType: "application/json",
        description: "Reporte de compatibilidad, exactitud y fallbacks para Adobe After Effects JSX.",
        read: async () => ({
          contents: [
            {
              uri: "capabilities://after-effects",
              mimeType: "application/json",
              text: JSON.stringify(AECapabilityAnalyzer.getCapabilityReport(), null, 2),
            },
          ],
        }),
      },
      {
        uri: "capabilities://fcpxml",
        name: "FCPXML Capabilities Report",
        mimeType: "application/json",
        description: "Reporte de compatibilidad y soporte para Apple Final Cut Pro FCPXML.",
        read: async () => ({
          contents: [
            {
              uri: "capabilities://fcpxml",
              mimeType: "application/json",
              text: JSON.stringify(FCPXMLExporter.getCapabilityReport(), null, 2),
            },
          ],
        }),
      },
      {
        uri: "capabilities://edl",
        name: "CMX 3600 EDL Capabilities Report",
        mimeType: "application/json",
        description: "Reporte de compatibilidad y degradaciones para CMX 3600 EDL.",
        read: async () => ({
          contents: [
            {
              uri: "capabilities://edl",
              mimeType: "application/json",
              text: JSON.stringify(EDLExporter.getCapabilityReport(), null, 2),
            },
          ],
        }),
      },
      {
        uri: "presets://captions",
        name: "Viral Caption Presets Catalog",
        mimeType: "application/json",
        description: "Catálogo de presets tipográficos virales de Fase 16.",
        read: async () => ({
          contents: [
            {
              uri: "presets://captions",
              mimeType: "application/json",
              text: JSON.stringify(ViralCaptionPresetRegistry.listPresets(), null, 2),
            },
          ],
        }),
      },
    ];
  }

  public static async readProjectResource(
    projectId: string,
    revisionId?: string
  ): Promise<{ contents: Array<{ uri: string; mimeType: string; text: string }> }> {
    const snapshot = MCPProjectStore.getRevision(projectId, revisionId);
    if (!snapshot) {
      throw new McpProjectNotFoundError(projectId, revisionId);
    }

    const uri = `project://${projectId}/${snapshot.revisionId}`;
    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify(
            {
              projectId: snapshot.projectId,
              revisionId: snapshot.revisionId,
              parentRevisionId: snapshot.parentRevisionId,
              operation: snapshot.operation,
              createdAt: snapshot.createdAt,
              summary: snapshot.summary,
            },
            null,
            2
          ),
        },
      ],
    };
  }
}
