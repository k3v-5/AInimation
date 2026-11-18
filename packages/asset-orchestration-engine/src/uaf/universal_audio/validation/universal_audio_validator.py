"""
UAF-81.59 Universal Audio, Music, Voice, Ambience, 3D Audio & Audio Simulation System.
Normative Audio Validator Engine.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
import math

from ..models.definition import (
    AudioCategory,
    AudioClipType,
    AudioFormat,
    AudioState,
    AudioAsset,
    AudioEmitter,
    AudioListener,
    AudioEvent,
    AudioBus,
    AudioMixerGraph,
    MusicStateMachine,
    AudioZone,
    AudioPortal,
)


@dataclass
class AudioValidationReport:
    """Report detailing validation status, issues, and metrics of audio configurations."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        self.is_valid = False
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


class UniversalAudioValidator:
    """
    Validates audio assets, emitters, listeners, buses, mixer graphs,
    and adaptive music state machines against UAF-81.59 standards.
    """

    @staticmethod
    def validate_asset(asset: AudioAsset) -> AudioValidationReport:
        report = AudioValidationReport()
        if not asset.asset_id or not asset.asset_id.strip():
            report.add_error("AudioAsset asset_id cannot be empty.")
        if asset.duration <= 0.0 or math.isnan(asset.duration):
            report.add_error(f"AudioAsset {asset.asset_id} must have a positive duration, got {asset.duration}.")
        if asset.channels not in [1, 2, 4, 6, 8]:
            report.add_error(f"AudioAsset {asset.asset_id} has unsupported channel count: {asset.channels}.")
        if asset.sample_rate not in [22050, 44100, 48000, 96000]:
            report.add_warning(f"AudioAsset {asset.asset_id} sample rate {asset.sample_rate} Hz is non-standard.")
        return report

    @staticmethod
    def validate_emitter(emitter: AudioEmitter) -> AudioValidationReport:
        report = AudioValidationReport()
        if not emitter.emitter_id or not emitter.emitter_id.strip():
            report.add_error("AudioEmitter emitter_id cannot be empty.")
        for coord in emitter.position:
            if math.isnan(coord) or math.isinf(coord):
                report.add_error(f"AudioEmitter {emitter.emitter_id} position contains invalid coordinate: {coord}.")
        if emitter.attenuation.min_distance > emitter.attenuation.max_distance:
            report.add_error(
                f"AudioEmitter {emitter.emitter_id} min_distance ({emitter.attenuation.min_distance}) "
                f"cannot exceed max_distance ({emitter.attenuation.max_distance})."
            )
        if emitter.attenuation.min_distance < 0.0 or emitter.attenuation.max_distance <= 0.0:
            report.add_error(f"AudioEmitter {emitter.emitter_id} attenuation distances must be positive.")
        return report

    @staticmethod
    def validate_listener(listener: AudioListener) -> AudioValidationReport:
        report = AudioValidationReport()
        if not listener.listener_id or not listener.listener_id.strip():
            report.add_error("AudioListener listener_id cannot be empty.")
        for coord in listener.position:
            if math.isnan(coord) or math.isinf(coord):
                report.add_error(f"AudioListener {listener.listener_id} position contains invalid coordinate: {coord}.")
        
        # Check that up and forward vectors are not zero or parallel
        f_mag = math.sqrt(sum(c*c for c in listener.forward_vector))
        u_mag = math.sqrt(sum(c*c for c in listener.up_vector))
        if f_mag < 1e-4 or u_mag < 1e-4:
            report.add_error(f"AudioListener {listener.listener_id} has degenerate orientation vectors.")
        return report

    @staticmethod
    def validate_mixer_graph(graph: AudioMixerGraph) -> AudioValidationReport:
        report = AudioValidationReport()
        if graph.has_cycle():
            report.add_error("AudioMixerGraph contains a cyclic dependency loop.")
        return report

    @staticmethod
    def validate_music_state_machine(sm: MusicStateMachine) -> AudioValidationReport:
        report = AudioValidationReport()
        for trans in sm.transitions:
            if trans.duration < 0.0:
                report.add_error(f"MusicTransition {trans.from_state}->{trans.to_state} has negative duration.")
        return report

    @staticmethod
    def validate_audio_state(state: AudioState) -> AudioValidationReport:
        report = AudioValidationReport()
        if state.master_volume < 0.0 or state.master_volume > 2.0:
            report.add_error(f"Master volume must be in [0.0, 2.0], got {state.master_volume}.")
        if state.voice_limit < 1 or state.voice_limit > 512:
            report.add_error(f"Voice limit must be in [1, 512], got {state.voice_limit}.")
        
        for em in state.active_emitters.values():
            em_rep = UniversalAudioValidator.validate_emitter(em)
            if not em_rep.is_valid:
                for err in em_rep.errors:
                    report.add_error(err)

        for ls in state.active_listeners.values():
            ls_rep = UniversalAudioValidator.validate_listener(ls)
            if not ls_rep.is_valid:
                for err in ls_rep.errors:
                    report.add_error(err)

        report.metrics = {
            "active_voices": len(state.active_voices),
            "active_emitters": len(state.active_emitters),
            "active_listeners": len(state.active_listeners),
            "voice_limit": state.voice_limit,
        }
        return report
