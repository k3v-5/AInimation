"""
Main entry point for IANIMATION Orchestrator Backend & FastMCP Server.

Allows running the FastMCP server in stdio mode (for Claude Desktop / Antigravity / Cursor)
or as an HTTP / SSE server for the Tauri frontend, as well as running pipeline simulations.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path
import sys
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.core.config import get_settings
from backend.core.telemetry import get_telemetry_bus
from backend.mcp.server import mcp_server
from backend.mcp.plan_engine import PlanEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ianimation.main")


async def run_stdio_mcp() -> None:
    """
    Run the FastMCP server over standard input/output (stdio) conforming
    to Model Context Protocol specification for LLM tool use.
    """
    logger.info("Starting IANIMATION FastMCP Server in stdio mode...")
    logger.info("Registered tools: %s", ", ".join(mcp_server.list_tools()))
    
    # Simple JSON-RPC / MCP loop over stdio
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    sys.stdout.write(json.dumps({
        "status": "ready",
        "server": mcp_server.server_name,
        "tools": mcp_server.list_tools(),
    }) + "\n")
    sys.stdout.flush()

    while True:
        line = await reader.readline()
        if not line:
            break
        try:
            payload = json.loads(line.decode("utf-8").strip())
            tool_name = payload.get("tool")
            args = payload.get("arguments", {})
            call_id = payload.get("id", "call_0")

            if tool_name in mcp_server.tools:
                result = mcp_server.call_tool(tool_name, **args)
                response = {
                    "id": call_id,
                    "status": "success",
                    "result": result.model_dump() if hasattr(result, "model_dump") else result,
                }
            else:
                response = {
                    "id": call_id,
                    "status": "error",
                    "error": f"Tool '{tool_name}' not found. Available: {mcp_server.list_tools()}",
                }
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except Exception as exc:
            logger.error("Error processing stdio payload: %s", exc)
            sys.stdout.write(json.dumps({"status": "error", "message": str(exc)}) + "\n")
            sys.stdout.flush()


def run_pipeline_verification() -> int:
    """
    Execute the automated end-to-end verification pipeline.
    """
    logger.info("Executing End-to-End Orchestrator Pipeline Verification...")
    from scripts.verify_pipeline import main as run_verify_main
    return run_verify_main()


def main() -> int:
    """
    CLI entry point parsing modes: stdio, verify, or status.
    """
    parser = argparse.ArgumentParser(description="IANIMATION 3D AI Orchestrator Backend")
    parser.add_argument(
        "--mode",
        choices=["stdio", "verify", "list-tools"],
        default="stdio",
        help="Execution mode (stdio for MCP, verify for full E2E test, list-tools for catalog)",
    )
    args = parser.parse_args()

    if args.mode == "list-tools":
        print(json.dumps({
            "server": mcp_server.server_name,
            "tools": mcp_server.list_tools(),
        }, indent=2))
        return 0
    elif args.mode == "verify":
        return run_pipeline_verification()
    elif args.mode == "stdio":
        try:
            asyncio.run(run_stdio_mcp())
            return 0
        except KeyboardInterrupt:
            logger.info("FastMCP Server terminated by user.")
            return 0


if __name__ == "__main__":
    sys.exit(main())
