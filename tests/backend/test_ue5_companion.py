"""
Unit and Integration Tests for UE5 Companion and Diagnostics.

Validates connectivity diagnostics, DefaultEngine.ini snippet generation,
scene bootstrapping across mock server and simulated in-engine Python environments.

100% Zero-Any compliant.
"""

from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock, patch

from backend.ue5.companion import (
    UE5BootstrapResult,
    UE5Companion,
    UE5DiagnosticReport,
    UE5PluginStatus,
    UE5SceneBootstrapConfig,
    generate_default_engine_ini_snippet,
)
from backend.ue5.mock_server import UE5MockServer


class TestUE5CompanionConfig(unittest.TestCase):
    """Test DefaultEngine.ini generation and model schemas."""

    def test_generate_default_engine_ini(self) -> None:
        ini = generate_default_engine_ini_snippet()
        self.assertIn("[/Script/RemoteControlWeb.RemoteControlWebSettings]", ini)
        self.assertIn("WebServerPort=30010", ini)
        self.assertIn("WebSocketServerPort=30020", ini)
        self.assertIn("[/Script/PixelStreaming.PixelStreamingSettings]", ini)
        self.assertIn('SignallingServerURL="ws://127.0.0.1:8888"', ini)
        self.assertIn("[/Script/Engine.RendererSettings]", ini)
        self.assertIn("r.DynamicGlobalIlluminationMethod=1", ini)
        self.assertIn("r.Nanite=1", ini)

    def test_diagnostic_report_model(self) -> None:
        plugin = UE5PluginStatus(
            name="RemoteControl",
            enabled=True,
            category="Messaging",
            version="5.4",
            description="Remote Control API",
        )
        report = UE5DiagnosticReport(
            host="127.0.0.1",
            http_port=30010,
            ws_port=30020,
            is_http_online=True,
            is_ws_online=True,
            response_time_ms=12.4,
            discovered_presets=["MyPreset"],
            active_plugins=[plugin],
            error_message=None,
            recommendations=["OK"],
        )
        self.assertTrue(report.is_http_online)
        self.assertEqual(len(report.discovered_presets), 1)
        self.assertEqual(report.discovered_presets[0], "MyPreset")


class TestUE5CompanionOffline(unittest.TestCase):
    """Test diagnostics and fallback behaviors when UE5 is offline."""

    def test_check_live_connection_offline(self) -> None:
        # Use an unused port unlikely to be open
        companion = UE5Companion(host="127.0.0.1", http_port=59998, ws_port=59999)
        report = companion.check_live_connection(timeout_seconds=0.2)
        self.assertFalse(report.is_http_online)
        self.assertFalse(report.is_ws_online)
        self.assertIsNotNone(report.error_message)
        self.assertTrue(len(report.recommendations) >= 1)
        self.assertIn("Unreal Engine no responde", report.recommendations[0])

    def test_bootstrap_scene_offline(self) -> None:
        companion = UE5Companion(host="127.0.0.1", http_port=59998, ws_port=59999)
        result = companion.bootstrap_scene()
        self.assertFalse(result.success)
        self.assertEqual(result.mode, "mock_fallback")
        self.assertIn("No se pudo conectar", result.message)


class TestUE5CompanionWithMockServer(unittest.TestCase):
    """Test diagnostics and bootstrap against an active UE5MockServer."""

    server: UE5MockServer

    @classmethod
    def setUpClass(cls) -> None:
        cls.server = UE5MockServer(port=30030, ws_port=30040)
        cls.server.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.stop()

    def test_check_live_connection_with_mock(self) -> None:
        companion = UE5Companion(host="127.0.0.1", http_port=30030, ws_port=30040)
        report = companion.check_live_connection(timeout_seconds=2.0)
        self.assertTrue(report.is_http_online)
        self.assertTrue(report.is_ws_online)
        self.assertGreater(report.response_time_ms, 0)
        self.assertIn("establecida y verificada", report.recommendations[0])

    def test_bootstrap_scene_with_mock(self) -> None:
        companion = UE5Companion(host="127.0.0.1", http_port=30030, ws_port=30040)
        config = UE5SceneBootstrapConfig(
            cine_camera_path="/Game/IANIMATION/CineCamera_Orchestrator",
            light_rig_preset="cyberpunk_neon",
        )
        result = companion.bootstrap_scene(config)
        self.assertTrue(result.success)
        self.assertEqual(result.mode, "remote_control_api")
        self.assertTrue(len(result.spawned_actors) >= 1)
        self.assertTrue(any("CineCamera_Orchestrator" in a for a in result.spawned_actors))


class TestUE5CompanionInEngine(unittest.TestCase):
    """Test simulated in-engine Python execution when sys.modules has unreal."""

    def test_bootstrap_scene_in_engine_python(self) -> None:
        mock_unreal = MagicMock()
        with patch.dict(sys.modules, {"unreal": mock_unreal}):
            companion = UE5Companion(host="127.0.0.1", http_port=30010, ws_port=30020)
            config = UE5SceneBootstrapConfig(light_rig_preset="studio_3point")
            result = companion.bootstrap_scene(config)
            self.assertTrue(result.success)
            self.assertEqual(result.mode, "in_engine_python")
            self.assertIn("PostProcessVolume_Lumen", result.spawned_actors)
            self.assertIn("LightRig_studio_3point_Directional", result.spawned_actors)


if __name__ == "__main__":
    unittest.main()
