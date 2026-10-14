import React, { useRef, useEffect, useState, useCallback } from 'react';
import * as THREE from 'three';
import {
  Eye,
  MonitorPlay,
  Camera,
  Sun,
  Activity,
  Wifi,
  WifiOff,
  Play,
} from 'lucide-react';
import { useUIStore } from '../../store';
import type { CameraPreset, LightingPreset } from '../../types';

export const Viewport3D: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const {
    viewportMode,
    setViewportMode,
    lightingPreset,
    setLightingPreset,
    cameraPreset,
    setCameraPreset,
    currentTime,
    isPlaying,
    audioAnalysis,
    signalingUrl,
    setSignalingUrl,
    pixelStreamingStatus,
    setPixelStreamingStatus,
  } = useUIStore();

  const [fps, setFps] = useState<number>(60);
  const [cameraCoords, setCameraCoords] = useState<{ x: number; y: number; z: number }>({
    x: 0,
    y: 1.5,
    z: 4.5,
  });
  const [isSimulatedStreamActive, setIsSimulatedStreamActive] = useState(false);

  // ---------------------------------------------------------------------------
  // Three.js 3D Interactive Scene & Mannequin Lifecycle
  // ---------------------------------------------------------------------------
  useEffect(() => {
    if (viewportMode !== 'webgl' || !containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth || 800;
    const height = container.clientHeight || 450;

    // Scene & Camera
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x09090b);

    const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 100);
    camera.position.set(0, 1.6, 4.5);

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    container.replaceChildren(renderer.domElement);

    // Grid Floor
    const gridHelper = new THREE.GridHelper(16, 32, 0x06b6d4, 0x27272a);
    gridHelper.position.y = 0;
    scene.add(gridHelper);

    // Dynamic Lighting Rig
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 2.0);
    keyLight.position.set(3, 6, 4);
    keyLight.castShadow = true;
    scene.add(keyLight);

    const rimLight = new THREE.PointLight(0x06b6d4, 3.0, 10);
    rimLight.position.set(-3, 2, -3);
    scene.add(rimLight);

    // Apply Lighting Preset Palettes
    if (lightingPreset === 'cyberpunk_neon') {
      ambientLight.color.setHex(0x0a0f1d);
      ambientLight.intensity = 0.5;
      keyLight.color.setHex(0x06b6d4); // Cyan
      rimLight.color.setHex(0xd946ef); // Magenta
      rimLight.intensity = 4.0;
    } else if (lightingPreset === 'studio_3point') {
      ambientLight.color.setHex(0x27272a);
      ambientLight.intensity = 0.8;
      keyLight.color.setHex(0xfffbeb); // Warm
      rimLight.color.setHex(0xe0f2fe); // Cool fill
      rimLight.intensity = 2.0;
    } else if (lightingPreset === 'dramatic') {
      ambientLight.color.setHex(0x050505);
      ambientLight.intensity = 0.2;
      keyLight.color.setHex(0xffffff);
      keyLight.intensity = 4.0;
      rimLight.intensity = 1.0;
    } else if (lightingPreset === 'outdoor_sunlight') {
      ambientLight.color.setHex(0x38bdf8);
      ambientLight.intensity = 0.9;
      keyLight.color.setHex(0xfef08a);
      keyLight.intensity = 3.0;
    } else if (lightingPreset === 'night_moonlight') {
      ambientLight.color.setHex(0x030712);
      ambientLight.intensity = 0.3;
      keyLight.color.setHex(0x93c5fd);
      keyLight.intensity = 1.5;
    }

    // -------------------------------------------------------------------------
    // 3D Biped Mannequin Construction (Head, Torso, Limbs, Pedestal)
    // -------------------------------------------------------------------------
    const characterGroup = new THREE.Group();

    // Pedestal
    const pedestalGeo = new THREE.CylinderGeometry(1.2, 1.4, 0.15, 32);
    const pedestalMat = new THREE.MeshStandardMaterial({
      color: 0x18181b,
      roughness: 0.3,
      metalness: 0.8,
    });
    const pedestal = new THREE.Mesh(pedestalGeo, pedestalMat);
    pedestal.position.y = 0.075;
    pedestal.receiveShadow = true;
    characterGroup.add(pedestal);

    // PBR Mannequin Material
    const bodyMat = new THREE.MeshStandardMaterial({
      color: 0xd4d4d8,
      roughness: 0.2,
      metalness: 0.6,
    });
    const jointMat = new THREE.MeshStandardMaterial({
      color: 0x06b6d4,
      roughness: 0.1,
      metalness: 0.9,
      emissive: 0x06b6d4,
      emissiveIntensity: 0.2,
    });

    // Pelvis
    const pelvis = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.22, 0.25, 16), bodyMat);
    pelvis.position.y = 1.05;
    pelvis.castShadow = true;
    characterGroup.add(pelvis);

    // Torso / Chest
    const torso = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.22, 0.5, 16), bodyMat);
    torso.position.y = 1.45;
    torso.castShadow = true;
    characterGroup.add(torso);

    // Head
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.18, 24, 24), bodyMat);
    head.position.y = 1.95;
    head.castShadow = true;
    characterGroup.add(head);

    // Visor Accent
    const visor = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.08, 0.15), jointMat);
    visor.position.set(0, 1.96, 0.12);
    characterGroup.add(visor);

    // Left Arm Hierarchy
    const leftArm = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.07, 0.45, 12), bodyMat);
    leftArm.position.set(0.42, 1.4, 0);
    characterGroup.add(leftArm);

    // Right Arm Hierarchy
    const rightArm = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.07, 0.45, 12), bodyMat);
    rightArm.position.set(-0.42, 1.4, 0);
    characterGroup.add(rightArm);

    // Legs
    const leftLeg = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.08, 0.75, 12), bodyMat);
    leftLeg.position.set(0.2, 0.55, 0);
    characterGroup.add(leftLeg);

    const rightLeg = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.08, 0.75, 12), bodyMat);
    rightLeg.position.set(-0.2, 0.55, 0);
    characterGroup.add(rightLeg);

    scene.add(characterGroup);

    // -------------------------------------------------------------------------
    // CineCamera Frustum Marker Visualization
    // -------------------------------------------------------------------------
    const cameraHelperGeo = new THREE.ConeGeometry(0.2, 0.5, 4);
    const cameraHelperMat = new THREE.MeshBasicMaterial({
      color: 0xf59e0b,
      wireframe: true,
    });
    const cameraFrustumMesh = new THREE.Mesh(cameraHelperGeo, cameraHelperMat);
    cameraFrustumMesh.position.set(0, 2.5, 3.2);
    cameraFrustumMesh.rotation.x = Math.PI / 2;
    scene.add(cameraFrustumMesh);

    // -------------------------------------------------------------------------
    // Smooth Orbit & Mouse Drag Interaction
    // -------------------------------------------------------------------------
    let isDragging = false;
    let prevMouseX = 0;
    let prevMouseY = 0;
    let orbitTheta = 0;
    let orbitPhi = Math.PI / 4;
    let orbitRadius = 4.5;

    const handleMouseDown = (e: MouseEvent) => {
      isDragging = true;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const deltaX = e.clientX - prevMouseX;
      const deltaY = e.clientY - prevMouseY;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;

      orbitTheta -= deltaX * 0.008;
      orbitPhi = Math.max(0.1, Math.min(Math.PI / 2 - 0.05, orbitPhi + deltaY * 0.008));
    };

    const handleMouseUp = () => {
      isDragging = false;
    };

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      orbitRadius = Math.max(1.8, Math.min(12.0, orbitRadius + e.deltaY * 0.005));
    };

    container.addEventListener('mousedown', handleMouseDown);
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    container.addEventListener('wheel', handleWheel, { passive: false });

    // Handle Window Resize
    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    // -------------------------------------------------------------------------
    // Animation Render Loop
    // -------------------------------------------------------------------------
    let frameId: number;
    let lastTime = performance.now();
    let frameCount = 0;

    const renderLoop = (timeNow: number) => {
      frameId = requestAnimationFrame(renderLoop);

      // FPS Calculation
      frameCount++;
      if (timeNow - lastTime >= 1000) {
        setFps(frameCount);
        frameCount = 0;
        lastTime = timeNow;
      }

      // Procedural Camera Presets Animation when not manually dragging
      if (!isDragging) {
        if (cameraPreset === 'smooth_orbit') {
          orbitTheta += 0.005;
        } else if (cameraPreset === 'dramatic_orbit') {
          orbitTheta += 0.012;
        } else if (cameraPreset === 'spiral_ascent') {
          orbitTheta += 0.008;
          orbitPhi = 0.3 + 0.3 * Math.sin(timeNow * 0.001);
        }
      }

      // Update Camera Position via Spherical Coordinates
      const cx = orbitRadius * Math.sin(orbitPhi) * Math.sin(orbitTheta);
      const cy = orbitRadius * Math.cos(orbitPhi) + 0.5;
      const cz = orbitRadius * Math.sin(orbitPhi) * Math.cos(orbitTheta);
      camera.position.set(cx, cy, cz);
      camera.lookAt(0, 1.2, 0);

      setCameraCoords({
        x: Number(cx.toFixed(2)),
        y: Number(cy.toFixed(2)),
        z: Number(cz.toFixed(2)),
      });

      // Synchronized Mannequin Motion (Audio Reactivity & Playback)
      const bpm = audioAnalysis?.bpm || 128.0;
      const beatFreq = (bpm / 60.0) * Math.PI * 2;
      const timeSec = isPlaying ? currentTime : timeNow * 0.001;

      // Vertical bounce on the beat
      const bounce = Math.abs(Math.sin(timeSec * (beatFreq / 2))) * 0.08;
      torso.position.y = 1.45 + bounce;
      head.position.y = 1.95 + bounce;
      visor.position.y = 1.96 + bounce;

      // Arm swing
      const armSwing = Math.sin(timeSec * beatFreq) * 0.3;
      leftArm.rotation.x = armSwing;
      rightArm.rotation.x = -armSwing;

      // Pulse neon rim light on the downbeat
      const beatPulse = 1.0 + Math.max(0, Math.sin(timeSec * beatFreq)) * 1.5;
      rimLight.intensity = (lightingPreset === 'cyberpunk_neon' ? 3.0 : 2.0) * beatPulse;

      renderer.render(scene, camera);
    };

    renderLoop(performance.now());

    return () => {
      cancelAnimationFrame(frameId);
      container.removeEventListener('mousedown', handleMouseDown);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      container.removeEventListener('wheel', handleWheel);
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
    };
  }, [viewportMode, lightingPreset, cameraPreset, isPlaying, currentTime, audioAnalysis]);

  // ---------------------------------------------------------------------------
  // Simulated WebRTC Stream Video Loop
  // ---------------------------------------------------------------------------
  const startSimulatedStream = useCallback(() => {
    setIsSimulatedStreamActive(true);
    setPixelStreamingStatus('connected');

    const offscreenCanvas = document.createElement('canvas');
    offscreenCanvas.width = 1280;
    offscreenCanvas.height = 720;
    const ctx = offscreenCanvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let t = 0;

    const drawFrame = () => {
      t += 0.03;
      ctx.fillStyle = '#09090b';
      ctx.fillRect(0, 0, 1280, 720);

      // Cyan-to-magenta grid
      ctx.strokeStyle = '#06b6d433';
      ctx.lineWidth = 1.5;
      for (let x = 0; x < 1280; x += 60) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, 720);
        ctx.stroke();
      }
      for (let y = 0; y < 720; y += 60) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(1280, y);
        ctx.stroke();
      }

      // Live animated badge
      ctx.fillStyle = '#10b981';
      ctx.beginPath();
      ctx.arc(60, 50, 8, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#f4f4f5';
      ctx.font = 'bold 20px monospace';
      ctx.fillText('UNREAL ENGINE 5.4 - PIXEL STREAMING (WEBRTC)', 80, 56);

      ctx.fillStyle = '#a1a1aa';
      ctx.font = '16px monospace';
      ctx.fillText(`LUMEN GI | NANITE ENABLED | 60.0 FPS | RENDER QUEUE IDLE`, 80, 86);

      // Rotating 3D wireframe box
      ctx.save();
      ctx.translate(640, 380);
      ctx.rotate(t);
      ctx.strokeStyle = '#06b6d4';
      ctx.lineWidth = 3;
      ctx.strokeRect(-120, -120, 240, 240);
      ctx.fillStyle = '#06b6d41a';
      ctx.fillRect(-120, -120, 240, 240);
      ctx.restore();

      animId = requestAnimationFrame(drawFrame);
    };

    drawFrame();

    const stream = offscreenCanvas.captureStream(60);
    if (videoRef.current) {
      videoRef.current.srcObject = stream;
      videoRef.current.play().catch(() => {});
    }

    return () => {
      cancelAnimationFrame(animId);
    };
  }, [setPixelStreamingStatus]);

  const togglePixelStreamingConnect = () => {
    if (pixelStreamingStatus === 'connected' || isSimulatedStreamActive) {
      setPixelStreamingStatus('disconnected');
      setIsSimulatedStreamActive(false);
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    } else {
      setPixelStreamingStatus('connecting');
      setTimeout(() => {
        startSimulatedStream();
      }, 600);
    }
  };

  return (
    <div className="relative bg-zinc-950 border border-zinc-800 rounded-xl overflow-hidden flex flex-col h-full shadow-2xl">
      {/* Viewport Top Header Toolbar */}
      <div className="absolute top-3 left-3 right-3 flex items-center justify-between z-20 pointer-events-none">
        <div className="flex items-center gap-2 pointer-events-auto bg-zinc-900/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-zinc-700/60 text-xs font-mono text-zinc-200 shadow-lg">
          <Eye className="w-4 h-4 text-cyan-400" />
          <span className="font-semibold tracking-wider">VIEWPORT 3D</span>
          <span className="text-zinc-600">|</span>
          <span className="text-[11px] text-zinc-400">
            {viewportMode === 'webgl' ? 'Three.js PBR Engine' : 'WebRTC Stream'}
          </span>
        </div>

        {/* Mode Selector & Preset Dropdowns */}
        <div className="flex items-center gap-2 pointer-events-auto">
          {viewportMode === 'webgl' && (
            <div className="flex items-center gap-1.5 bg-zinc-900/90 backdrop-blur-md px-2 py-1 rounded-lg border border-zinc-700/60 text-xs">
              <Sun className="w-3.5 h-3.5 text-amber-400" />
              <select
                value={lightingPreset}
                onChange={(e) => setLightingPreset(e.target.value as LightingPreset)}
                className="bg-transparent text-zinc-200 text-xs font-mono outline-none cursor-pointer"
              >
                <option value="cyberpunk_neon" className="bg-zinc-900">
                  Lumen: Cyberpunk Neon
                </option>
                <option value="studio_3point" className="bg-zinc-900">
                  Lumen: Studio 3-Point
                </option>
                <option value="dramatic" className="bg-zinc-900">
                  Lumen: Dramatic
                </option>
                <option value="outdoor_sunlight" className="bg-zinc-900">
                  Lumen: Sol Exterior
                </option>
                <option value="night_moonlight" className="bg-zinc-900">
                  Lumen: Luz de Luna
                </option>
              </select>
            </div>
          )}

          {viewportMode === 'webgl' && (
            <div className="flex items-center gap-1.5 bg-zinc-900/90 backdrop-blur-md px-2 py-1 rounded-lg border border-zinc-700/60 text-xs">
              <Camera className="w-3.5 h-3.5 text-cyan-400" />
              <select
                value={cameraPreset}
                onChange={(e) => setCameraPreset(e.target.value as CameraPreset)}
                className="bg-transparent text-zinc-200 text-xs font-mono outline-none cursor-pointer"
              >
                <option value="dramatic_orbit" className="bg-zinc-900">
                  Cámara: Dramatic Orbit
                </option>
                <option value="smooth_orbit" className="bg-zinc-900">
                  Cámara: Smooth Orbit
                </option>
                <option value="aerial_pan" className="bg-zinc-900">
                  Cámara: Aerial Pan
                </option>
                <option value="front_close" className="bg-zinc-900">
                  Cámara: Front Close-Up
                </option>
                <option value="spiral_ascent" className="bg-zinc-900">
                  Cámara: Spiral Ascent
                </option>
              </select>
            </div>
          )}

          {/* Engine / Viewport Mode Switcher */}
          <div className="flex items-center gap-1 bg-zinc-900/90 backdrop-blur-md p-1 rounded-lg border border-zinc-700/60 text-xs">
            <button
              onClick={() => setViewportMode('webgl')}
              className={`px-2.5 py-1 rounded font-mono transition ${
                viewportMode === 'webgl'
                  ? 'bg-cyan-500 text-black font-semibold shadow'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              WebGL 3D
            </button>
            <button
              onClick={() => setViewportMode('pixel_streaming')}
              className={`px-2.5 py-1 rounded font-mono transition ${
                viewportMode === 'pixel_streaming'
                  ? 'bg-cyan-500 text-black font-semibold shadow'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              UE5 Pixel Streaming
            </button>
          </div>
        </div>
      </div>

      {/* Main Viewport Content Canvas */}
      {viewportMode === 'webgl' ? (
        <div ref={containerRef} className="w-full h-full relative cursor-grab active:cursor-grabbing" />
      ) : (
        <div className="w-full h-full relative flex flex-col items-center justify-center bg-zinc-950 p-6">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className={`w-full h-full object-contain ${
              pixelStreamingStatus === 'connected' ? 'block' : 'hidden'
            }`}
          />

          {pixelStreamingStatus !== 'connected' && (
            <div className="flex flex-col items-center text-center max-w-md">
              <MonitorPlay className="w-14 h-14 text-cyan-400 mb-3 animate-pulse" />
              <h3 className="text-base font-semibold text-zinc-100 mb-1">
                Pixel Streaming WebRTC para Unreal Engine 5
              </h3>
              <p className="text-xs text-zinc-400 mb-4 leading-relaxed">
                Transmisión remota interactiva de 60 FPS con control de cámara e iluminación en tiempo
                real desde el orquestador.
              </p>

              {/* Signaling URL configuration */}
              <div className="w-full flex items-center gap-2 bg-zinc-900 border border-zinc-700 rounded-lg p-1.5 mb-4">
                <input
                  type="text"
                  value={signalingUrl}
                  onChange={(e) => setSignalingUrl(e.target.value)}
                  placeholder="ws://127.0.0.1:8888"
                  className="flex-1 bg-transparent px-2 text-xs font-mono text-zinc-200 outline-none"
                />
                <button
                  onClick={togglePixelStreamingConnect}
                  disabled={pixelStreamingStatus === 'connecting'}
                  className="px-3 py-1.5 bg-cyan-500 hover:bg-cyan-400 text-black text-xs font-bold rounded transition font-mono"
                >
                  {pixelStreamingStatus === 'connecting' ? 'Conectando...' : 'Conectar'}
                </button>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={startSimulatedStream}
                  className="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-cyan-300 border border-cyan-500/30 text-xs rounded transition font-mono flex items-center gap-1.5"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>Simular Transmisión UE5</span>
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Viewport Bottom Overlay Info Bar */}
      <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between z-20 pointer-events-none">
        <div className="flex items-center gap-3 pointer-events-auto bg-zinc-900/85 backdrop-blur-md px-3 py-1 rounded-lg border border-zinc-800 text-[11px] font-mono text-zinc-400 shadow">
          <div className="flex items-center gap-1.5 text-zinc-300">
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span>{fps} FPS</span>
          </div>
          <span className="text-zinc-700">|</span>
          <span>
            Pos: [{cameraCoords.x}, {cameraCoords.y}, {cameraCoords.z}]
          </span>
          <span className="text-zinc-700">|</span>
          <span className="text-cyan-400 font-semibold">{lightingPreset}</span>
        </div>

        {viewportMode === 'pixel_streaming' && (
          <div className="flex items-center gap-2 pointer-events-auto">
            <button
              onClick={togglePixelStreamingConnect}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-mono border backdrop-blur-md transition ${
                pixelStreamingStatus === 'connected'
                  ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-400'
                  : 'bg-zinc-900/90 border-zinc-700 text-zinc-400 hover:text-white'
              }`}
            >
              {pixelStreamingStatus === 'connected' ? (
                <>
                  <Wifi className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
                  <span>En Vivo (WebRTC)</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-3.5 h-3.5 text-zinc-500" />
                  <span>Desconectado</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Viewport3D;
