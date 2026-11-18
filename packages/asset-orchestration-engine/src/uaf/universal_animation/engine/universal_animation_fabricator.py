"""
Universal Animation Fabricator Engine.
Synthesizes Canonical Golden Animation Presets, procedural motion, retargeting, blend spaces, and runtime packaging.
UAF-81.55 Sections 3-132, 159, 160, 161, 162.
"""

from typing import Dict, Any, List, Optional, Tuple
import math

from ...core.hashing.canonical_hasher import CanonicalHasher
from ..models.definition import (
    AnimationType55,
    ChannelType55,
    CurveInterpolation55,
    MarkerType55,
    ResamplingMode55,
    BlendType55,
    LayerType55,
    LocomotionMode55,
    RootMotionMode55,
    CompressionMethod55,
    Keyframe55,
    AnimationTrack,
    AnimationCurve,
    AnimationMarker,
    AnimationEvent,
    AnimationClip,
    AnimationDefinition,
    RetargetProfile55,
    PoseLibrary55,
    BlendSpace55,
    MontageSection55,
    AnimationMontage55,
    StateTransition55,
    AnimationStateMachine55,
    MotionWarpingProfile55,
    FacialAnimationTrack55,
    AnimationCompressionProfile55,
    AnimationLODProfile55,
    RuntimeProfile55,
    AnimationDiff55,
)
from ..validation.universal_animation_validator import UniversalAnimationValidator, AnimationValidationReport
from ..package.universal_animation_package import ProductionReadyAnimatedCharacter
from ...universal_character.engine.universal_character_fabricator import UniversalCharacterFabricator
from ...universal_character.package.universal_character_package import ProductionReadyCharacter


class UniversalAnimationFabricator:
    """
    Core fabrication engine for Universal Animation, Motion, Retargeting, and Runtime System.
    """

    @classmethod
    def build_track(
        cls,
        bone_name: str,
        channel: ChannelType55,
        duration: float,
        sample_rate: int = 30,
        base_value: Tuple[float, ...] = (0.0, 0.0, 0.0),
        amplitude: float = 0.0,
        frequency: float = 1.0,
    ) -> AnimationTrack:
        """
        Builds an AnimationTrack with deterministic harmonic motion.
        """
        frame_count = max(2, int(duration * sample_rate) + 1)
        dt = duration / (frame_count - 1)
        keyframes = []

        for i in range(frame_count):
            t = i * dt
            # Harmonic displacement
            osc = amplitude * math.sin(2.0 * math.pi * frequency * t)
            if len(base_value) == 3:
                val = (base_value[0], base_value[1] + osc, base_value[2])
            elif len(base_value) == 4:
                # Quat identity with slight pitch/yaw
                val = (osc * 0.1, 0.0, 0.0, 1.0)
            else:
                val = (base_value[0] + osc,)
            keyframes.append(Keyframe55(time_sec=round(t, 4), value=val))

        return AnimationTrack(
            bone_name=bone_name,
            channel=channel,
            keyframes=keyframes,
            interpolation=CurveInterpolation55.LINEAR,
        )

    @classmethod
    def build_standard_tracks(
        cls,
        skeleton_bones: List[str],
        duration: float = 1.0,
        sample_rate: int = 30,
        amplitude: float = 1.0,
        frequency: float = 1.0,
    ) -> List[AnimationTrack]:
        """
        Builds basic tracks for pelvis, spine, and limbs.
        """
        tracks = []
        for b in skeleton_bones[:8]:  # Cover root, pelvis, spine, head, limbs
            tracks.append(cls.build_track(b, ChannelType55.ROTATION, duration, sample_rate, base_value=(0.0, 0.0, 0.0, 1.0), amplitude=amplitude * 0.2, frequency=frequency))
        # Pelvis translation bounce
        if "PELVIS" in skeleton_bones:
            tracks.append(cls.build_track("PELVIS", ChannelType55.TRANSLATION, duration, sample_rate, base_value=(0.0, 0.0, 95.0), amplitude=amplitude * 1.5, frequency=frequency * 2.0))
        return tracks

    # --- PROCEDURAL GENERATORS (Sections 45-58) ---

    @classmethod
    def generate_procedural_walk(cls, skeleton_bones: List[str], duration: float = 1.0, sample_rate: int = 30) -> AnimationDefinition:
        tracks = cls.build_standard_tracks(skeleton_bones, duration, sample_rate, amplitude=2.0, frequency=1.0)
        markers = [
            AnimationMarker("Footstep_L", MarkerType55.FOOTSTEP, time_sec=0.25),
            AnimationMarker("Footstep_R", MarkerType55.FOOTSTEP, time_sec=0.75),
        ]
        events = [
            AnimationEvent("PlayFootstepSound", time_sec=0.25, payload={"foot": "LEFT"}),
            AnimationEvent("PlayFootstepSound", time_sec=0.75, payload={"foot": "RIGHT"}),
        ]
        return AnimationDefinition(
            animation_id="Anim_Procedural_Walk",
            name="Procedural Walk Cycle",
            anim_type=AnimationType55.WALK,
            duration=duration,
            sample_rate=sample_rate,
            tracks=tracks,
            markers=markers,
            events=events,
        )

    @classmethod
    def generate_procedural_run(cls, skeleton_bones: List[str], duration: float = 0.8, sample_rate: int = 30) -> AnimationDefinition:
        tracks = cls.build_standard_tracks(skeleton_bones, duration, sample_rate, amplitude=3.5, frequency=1.25)
        markers = [
            AnimationMarker("Footstep_L", MarkerType55.FOOTSTEP, time_sec=0.2),
            AnimationMarker("Footstep_R", MarkerType55.FOOTSTEP, time_sec=0.6),
        ]
        return AnimationDefinition(
            animation_id="Anim_Procedural_Run",
            name="Procedural Run Cycle",
            anim_type=AnimationType55.RUN,
            duration=duration,
            sample_rate=sample_rate,
            tracks=tracks,
            markers=markers,
        )

    @classmethod
    def generate_breathing(cls, duration: float = 2.0, sample_rate: int = 30) -> AnimationDefinition:
        tracks = [
            cls.build_track("SPINE_02", ChannelType55.ROTATION, duration, sample_rate, base_value=(0.0, 0.0, 0.0, 1.0), amplitude=0.05, frequency=0.5),
            cls.build_track("PELVIS", ChannelType55.TRANSLATION, duration, sample_rate, base_value=(0.0, 0.0, 95.0), amplitude=0.3, frequency=0.5),
        ]
        return AnimationDefinition(
            animation_id="Anim_Breathing_Idle",
            name="Breathing Idle Loop",
            anim_type=AnimationType55.IDLE,
            duration=duration,
            sample_rate=sample_rate,
            tracks=tracks,
        )

    @classmethod
    def generate_look_at(cls, target_pos: Tuple[float, float, float] = (0.0, 100.0, 160.0)) -> AnimationDefinition:
        tracks = [
            cls.build_track("HEAD", ChannelType55.ROTATION, duration=1.0, sample_rate=30, base_value=(0.1, 0.0, 0.0, 1.0)),
            cls.build_track("NECK", ChannelType55.ROTATION, duration=1.0, sample_rate=30, base_value=(0.05, 0.0, 0.0, 1.0)),
        ]
        return AnimationDefinition(
            animation_id="Anim_LookAt",
            name="Look-At Aim Track",
            anim_type=AnimationType55.AIM,
            duration=1.0,
            sample_rate=30,
            tracks=tracks,
        )

    @classmethod
    def generate_foot_placement(cls, floor_height: float = 0.0) -> Dict[str, Any]:
        return {
            "floor_height": floor_height,
            "foot_l_offset_z": max(0.0, floor_height),
            "foot_r_offset_z": max(0.0, floor_height),
            "ik_foot_aligned": True,
        }

    # --- RESAMPLING & NORMALIZATION (Sections 19-24) ---

    @classmethod
    def resample_animation(
        cls,
        anim: AnimationDefinition,
        target_sample_rate: int = 60,
        mode: ResamplingMode55 = ResamplingMode55.LINEAR,
    ) -> AnimationDefinition:
        new_tracks = []
        for t in anim.tracks:
            new_track = cls.build_track(
                t.bone_name,
                t.channel,
                anim.duration,
                sample_rate=target_sample_rate,
                base_value=t.keyframes[0].value if t.keyframes else (0.0, 0.0, 0.0),
            )
            new_tracks.append(new_track)

        return AnimationDefinition(
            animation_id=f"{anim.animation_id}_resampled_{target_sample_rate}",
            name=f"{anim.name} ({target_sample_rate}Hz)",
            anim_type=anim.anim_type,
            duration=anim.duration,
            sample_rate=target_sample_rate,
            skeleton_reference=anim.skeleton_reference,
            tracks=new_tracks,
            curves=anim.curves,
            markers=anim.markers,
            events=anim.events,
        )

    # --- STATE MACHINE, MONTAGES, BLEND SPACES (Sections 64, 71, 74) ---

    @classmethod
    def build_locomotion_state_machine(cls) -> AnimationStateMachine55:
        states = ["IDLE", "WALK", "RUN", "JUMP_START", "JUMP_FALL", "JUMP_LAND"]
        transitions = [
            StateTransition55(from_state="IDLE", to_state="WALK", condition="Speed > 10.0"),
            StateTransition55(from_state="WALK", to_state="RUN", condition="Speed > 250.0"),
            StateTransition55(from_state="RUN", to_state="WALK", condition="Speed <= 250.0"),
            StateTransition55(from_state="WALK", to_state="IDLE", condition="Speed <= 10.0"),
            StateTransition55(from_state="IDLE", to_state="JUMP_START", condition="IsFalling == True"),
            StateTransition55(from_state="JUMP_START", to_state="JUMP_FALL", condition="TimeRemaining < 0.1"),
            StateTransition55(from_state="JUMP_FALL", to_state="JUMP_LAND", condition="IsGrounded == True"),
            StateTransition55(from_state="JUMP_LAND", to_state="IDLE", condition="TimeRemaining < 0.1"),
        ]
        return AnimationStateMachine55(
            machine_id="SM_Locomotion",
            states=states,
            transitions=transitions,
            default_state="IDLE",
        )

    @classmethod
    def build_blend_space_1d(cls, blend_id: str = "BS_Locomotion") -> BlendSpace55:
        samples = [
            (0.0, "Anim_Idle"),
            (150.0, "Anim_Walk"),
            (350.0, "Anim_Run"),
            (550.0, "Anim_Sprint"),
        ]
        return BlendSpace55(
            blend_id=blend_id,
            dimensions=1,
            param_x_name="Speed",
            param_x_range=(0.0, 600.0),
            samples=samples,
            blend_type=BlendType55.LINEAR,
        )

    @classmethod
    def build_montage(
        cls,
        animation_id: str,
        montage_id: str = "MONT_Attack",
        duration: float = 1.2,
    ) -> AnimationMontage55:
        sections = [
            MontageSection55("Windup", start_time=0.0, length=0.3, next_section="Swing"),
            MontageSection55("Swing", start_time=0.3, length=0.4, next_section="Recovery"),
            MontageSection55("Recovery", start_time=0.7, length=0.5, next_section=None),
        ]
        notifies = [
            AnimationMarker("HitWindow_Start", MarkerType55.HIT, time_sec=0.35),
            AnimationMarker("HitWindow_End", MarkerType55.HIT, time_sec=0.55),
        ]
        return AnimationMontage55(
            montage_id=montage_id,
            animation_id=animation_id,
            sections=sections,
            notifies=notifies,
            blend_in_sec=0.2,
            blend_out_sec=0.2,
        )

    # --- THE 15 GOLDEN ANIMATIONS (Section 160) ---

    @classmethod
    def build_golden_idle(cls, character: Optional[ProductionReadyCharacter] = None) -> ProductionReadyAnimatedCharacter:
        char = character or UniversalCharacterFabricator.build_golden_human_male()
        anim = cls.generate_breathing(duration=2.0, sample_rate=30)
        anim.animation_id = "GOLDEN_IDLE"
        anim.name = "Golden Idle"
        return cls.fabricate(char, anim, export_path="/Game/Animations/Anim_Golden_Idle.uasset")

    @classmethod
    def build_golden_walk(cls, character: Optional[ProductionReadyCharacter] = None) -> ProductionReadyAnimatedCharacter:
        char = character or UniversalCharacterFabricator.build_golden_human_male()
        anim = cls.generate_procedural_walk(char.skeleton.bone_names, duration=1.0, sample_rate=30)
        anim.animation_id = "GOLDEN_WALK"
        anim.name = "Golden Walk"
        return cls.fabricate(char, anim, export_path="/Game/Animations/Anim_Golden_Walk.uasset")

    @classmethod
    def build_golden_run(cls, character: Optional[ProductionReadyCharacter] = None) -> ProductionReadyAnimatedCharacter:
        char = character or UniversalCharacterFabricator.build_golden_human_male()
        anim = cls.generate_procedural_run(char.skeleton.bone_names, duration=0.8, sample_rate=30)
        anim.animation_id = "GOLDEN_RUN"
        anim.name = "Golden Run"
        return cls.fabricate(char, anim, export_path="/Game/Animations/Anim_Golden_Run.uasset")

    @classmethod
    def build_golden_sprint(cls, character: Optional[ProductionReadyCharacter] = None) -> ProductionReadyAnimatedCharacter:
        char = character or UniversalCharacterFabricator.build_golden_human_male()
        tracks = cls.build_standard_tracks(char.skeleton.bone_names, duration=0.6, sample_rate=60, amplitude=4.5, frequency=1.66)
        anim = AnimationDefinition(
            animation_id="GOLDEN_SPRINT",
            name="Golden Sprint",
            anim_type=AnimationType55.SPRINT,
            duration=0.6,
            sample_rate=60,
            tracks=tracks,
        )
        return cls.fabricate(char, anim, export_path="/Game/Animations/Anim_Golden_Sprint.uasset")

    @classmethod
    def build_golden_jump(cls, character: Optional[ProductionReadyCharacter] = None) -> ProductionReadyAnimatedCharacter:
        char = character or UniversalCharacterFabricator.build_golden_human_male()
        tracks = cls.build_standard_tracks(char.skeleton.bone_names, duration=1.2, sample_rate=30, amplitude=2.0)
        anim = AnimationDefinition(
            animation_id="GOLDEN_JUMP",
            name="Golden Jump",
            anim_type=AnimationType55.JUMP,
            duration=1.2,
            sample_rate=30,
            tracks=tracks,
            markers=[AnimationMarker("JumpApex", MarkerType55.SYNC, time_sec=0.5)],
        )
        return cls.fabricate(char, anim, export_path="/Game/Animations/Anim_Golden_Jump.uasset")

    @classmethod
    def build_golden_fall(cls, character: Optional[ProductionReadyCharacter] = None) -> ProductionReadyAnimatedCharacter:
        char = character or UniversalCharacterFabricator.build_golden_human_male()
        tracks = cls.build_standard_tracks(char.skeleton.bone_names, duration=0.5, sample_rate=30, amplitude=1.0)
        anim = AnimationDefinition(
            animation_id="GOLDEN_FALL",
            name="Golden Fall",
            anim_type=AnimationType55.FALL,
            duration=0.5,
            sample_rate=30,
            tracks=tracks,
        )
        return cls.fabricate(char, anim, export_path="/Game/Animations/Anim_Golden_Fall.uasset")

    @classmethod
    def build_golden_land(cls, character: Optional[ProductionReadyCharacter] = None) -> ProductionReadyAnimatedCharacter:
        char = character or UniversalCharacterFabricator.build_golden_human_male()
        tracks = cls.build_standard_tracks(char.skeleton.bone_names, duration=0.6, sample_rate=30, amplitude=1.5)
        anim = AnimationDefinition(
            animation_id="GOLDEN_LAND",
            name="Golden Land",
            anim_type=AnimationType55.LAND,
            duration=0.6,
            sample_rate=30,
            tracks=tracks,
            events=[AnimationEvent("OnLandingImpact", time_sec=0.1, payload={"impact_intensity": 1.0})],
        )
        return cls.fabricate(char, anim, export_path="/Game/Animations/Anim_Golden_Land.uasset")

    @classmethod
    def build_golden_turn(cls, character: Optional[ProductionReadyCharacter] = None) -> ProductionReadyAnimatedCharacter:
        char = character or UniversalCharacterFabricator.build_golden_human_male()
        tracks = cls.build_standard_tracks(char.skeleton.bone_names, duration=0.8, sample_rate=30, amplitude=1.2)
        anim = AnimationDefinition(
            animation_id="GOLDEN_TURN",
            name="Golden Turn",
            anim_type=AnimationType55.TURN,
            duration=0.8,
            sample_rate=30,
            tracks=tracks,
        )
        return cls.fabricate(char, anim, export_path="/Game/Animations/Anim_Golden_Turn.uasset")

    @classmethod
    def build_golden_strafe(cls, character: Optional[ProductionReadyCharacter] = None) -> ProductionReadyAnimatedCharacter:
        char = character or UniversalCharacterFabricator.build_golden_human_male()
        tracks = cls.build_standard_tracks(char.skeleton.bone_names, duration=1.0, sample_rate=30, amplitude=1.8)
        anim = AnimationDefinition(
            animation_id="GOLDEN_STRAFE",
            name="Golden Strafe",
            anim_type=AnimationType55.STRAFE,
            duration=1.0,
            sample_rate=30,
            tracks=tracks,
        )
        return cls.fabricate(char, anim, export_path="/Game/Animations/Anim_Golden_Strafe.uasset")

    @classmethod
    def build_golden_attack(cls, character: Optional[ProductionReadyCharacter] = None) -> ProductionReadyAnimatedCharacter:
        char = character or UniversalCharacterFabricator.build_golden_human_male()
        tracks = cls.build_standard_tracks(char.skeleton.bone_names, duration=1.2, sample_rate=30, amplitude=3.0)
        anim = AnimationDefinition(
            animation_id="GOLDEN_ATTACK",
            name="Golden Attack",
            anim_type=AnimationType55.ATTACK,
            duration=1.2,
            sample_rate=30,
            tracks=tracks,
            markers=[AnimationMarker("Hit_Strike", MarkerType55.HIT, time_sec=0.45)],
            events=[AnimationEvent("TriggerWeaponHitbox", time_sec=0.45)],
        )
        montage = cls.build_montage(anim.animation_id, "MONT_Golden_Attack", duration=1.2)
        return cls.fabricate(char, anim, montages=[montage], export_path="/Game/Animations/Anim_Golden_Attack.uasset")

    @classmethod
    def build_golden_aim(cls, character: Optional[ProductionReadyCharacter] = None) -> ProductionReadyAnimatedCharacter:
        char = character or UniversalCharacterFabricator.build_golden_human_male()
        anim = cls.generate_look_at()
        anim.animation_id = "GOLDEN_AIM"
        anim.name = "Golden Aim"
        return cls.fabricate(char, anim, export_path="/Game/Animations/Anim_Golden_Aim.uasset")

    @classmethod
    def build_golden_crouch(cls, character: Optional[ProductionReadyCharacter] = None) -> ProductionReadyAnimatedCharacter:
        char = character or UniversalCharacterFabricator.build_golden_human_male()
        tracks = [
            cls.build_track("PELVIS", ChannelType55.TRANSLATION, duration=1.5, sample_rate=30, base_value=(0.0, 0.0, 50.0), amplitude=0.2),
            cls.build_track("SPINE_01", ChannelType55.ROTATION, duration=1.5, sample_rate=30, base_value=(0.2, 0.0, 0.0, 1.0)),
        ]
        anim = AnimationDefinition(
            animation_id="GOLDEN_CROUCH",
            name="Golden Crouch",
            anim_type=AnimationType55.CROUCH,
            duration=1.5,
            sample_rate=30,
            tracks=tracks,
        )
        return cls.fabricate(char, anim, export_path="/Game/Animations/Anim_Golden_Crouch.uasset")

    @classmethod
    def build_golden_facial(cls, character: Optional[ProductionReadyCharacter] = None) -> ProductionReadyAnimatedCharacter:
        char = character or UniversalCharacterFabricator.build_golden_facial_character()
        tracks = cls.build_standard_tracks(char.skeleton.bone_names, duration=2.0, sample_rate=30)
        facial_tracks = [
            FacialAnimationTrack55("Morph_Face_Smile", [(0.0, 0.0), (1.0, 0.8), (2.0, 0.0)]),
            FacialAnimationTrack55("Morph_Eye_Blink_L", [(0.0, 0.0), (0.5, 1.0), (0.6, 0.0)]),
            FacialAnimationTrack55("Morph_Eye_Blink_R", [(0.0, 0.0), (0.5, 1.0), (0.6, 0.0)]),
        ]
        anim = AnimationDefinition(
            animation_id="GOLDEN_FACIAL",
            name="Golden Facial",
            anim_type=AnimationType55.CUSTOM,
            duration=2.0,
            sample_rate=30,
            tracks=tracks,
        )
        return cls.fabricate(char, anim, facial_tracks=facial_tracks, export_path="/Game/Animations/Anim_Golden_Facial.uasset")

    @classmethod
    def build_golden_root_motion(cls, character: Optional[ProductionReadyCharacter] = None) -> ProductionReadyAnimatedCharacter:
        char = character or UniversalCharacterFabricator.build_golden_human_male()
        tracks = cls.build_standard_tracks(char.skeleton.bone_names, duration=1.5, sample_rate=30, amplitude=2.5)
        # Add root bone forward motion
        root_track = cls.build_track("ROOT", ChannelType55.TRANSLATION, duration=1.5, sample_rate=30, base_value=(0.0, 100.0, 0.0), amplitude=50.0)
        tracks.append(root_track)
        anim = AnimationDefinition(
            animation_id="GOLDEN_ROOT_MOTION",
            name="Golden Root Motion",
            anim_type=AnimationType55.CUSTOM,
            duration=1.5,
            sample_rate=30,
            tracks=tracks,
            root_motion_enabled=True,
        )
        warping = MotionWarpingProfile55("Warp_Forward_Dash", warp_target_bone="ROOT", max_translation_warp_cm=100.0)
        return cls.fabricate(char, anim, warping=warping, export_path="/Game/Animations/Anim_Golden_Root_Motion.uasset")

    @classmethod
    def build_golden_retarget(cls, character: Optional[ProductionReadyCharacter] = None) -> ProductionReadyAnimatedCharacter:
        char = character or UniversalCharacterFabricator.build_golden_human_male()
        anim = cls.generate_procedural_walk(char.skeleton.bone_names, duration=1.0, sample_rate=30)
        anim.animation_id = "GOLDEN_RETARGET"
        anim.name = "Golden Retargeted Walk"
        retarget = RetargetProfile55(
            profile_id="RP_UE5_Manny",
            source_skeleton=char.skeleton.skeleton_id,
            target_skeleton="SKEL_UE5_Manny",
            bone_mapping={b: b for b in char.skeleton.bone_names},
            ik_goals=["IK_Foot_L", "IK_Foot_R", "IK_Hand_L", "IK_Hand_R"],
        )
        return cls.fabricate(char, anim, retarget=retarget, export_path="/Game/Animations/Anim_Golden_Retarget.uasset")

    # --- FABRICATE ---

    @classmethod
    def fabricate(
        cls,
        character: ProductionReadyCharacter,
        animation: AnimationDefinition,
        clips: Optional[List[AnimationClip]] = None,
        retarget: Optional[RetargetProfile55] = None,
        blend_space: Optional[BlendSpace55] = None,
        montages: Optional[List[AnimationMontage55]] = None,
        state_machine: Optional[AnimationStateMachine55] = None,
        warping: Optional[MotionWarpingProfile55] = None,
        facial_tracks: Optional[List[FacialAnimationTrack55]] = None,
        compression: Optional[AnimationCompressionProfile55] = None,
        lod_profile: Optional[AnimationLODProfile55] = None,
        runtime_profile: Optional[RuntimeProfile55] = None,
        export_path: Optional[str] = None,
    ) -> ProductionReadyAnimatedCharacter:
        """
        Synthesizes and validates ProductionReadyAnimatedCharacter.
        """
        out_path = export_path or f"/Game/Animations/Anim_{animation.animation_id}.uasset"
        comp = compression or AnimationCompressionProfile55()
        lods = lod_profile or AnimationLODProfile55()
        rt = runtime_profile or RuntimeProfile55(f"RT_{animation.animation_id}")
        clips_list = clips or [AnimationClip(f"Clip_{animation.animation_id}", 0.0, animation.duration)]
        montages_list = montages or []
        facial_list = facial_tracks or []

        report = UniversalAnimationValidator.validate_animation(
            animation=animation,
            retarget=retarget,
            state_machine=state_machine,
            compression=comp,
            runtime_profile=rt,
            export_path=out_path,
        )

        return ProductionReadyAnimatedCharacter(
            character=character,
            animation=animation,
            clips=clips_list,
            retarget=retarget,
            blend_space=blend_space,
            montages=montages_list,
            state_machine=state_machine,
            warping=warping,
            facial_tracks=facial_list,
            compression=comp,
            lod_profile=lods,
            runtime_profile=rt,
            validation_report=report,
            export_path=out_path,
        )

    # --- CACHE & DIFF (Sections 124-129) ---

    @classmethod
    def generate_cache_key(cls, animated_char: ProductionReadyAnimatedCharacter) -> str:
        payload = {
            "char_hash": animated_char.character.canonical_hash,
            "anim_id": animated_char.animation.animation_id,
            "duration": animated_char.animation.duration,
            "sample_rate": animated_char.animation.sample_rate,
            "track_count": len(animated_char.animation.tracks),
        }
        return CanonicalHasher.compute_hash(payload)

    @classmethod
    def diff_animations(cls, anim_a: AnimationDefinition, anim_b: AnimationDefinition, diff_id: str = "DIFF_ANIM_01") -> AnimationDiff55:
        return AnimationDiff55(
            diff_id=diff_id,
            duration_changed=anim_a.duration != anim_b.duration,
            tracks_changed=len(anim_a.tracks) != len(anim_b.tracks),
            events_changed=len(anim_a.events) != len(anim_b.events),
        )
