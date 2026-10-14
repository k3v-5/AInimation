import React, { useState, useRef } from 'react';
import { Music, Image as ImageIcon, Video, X, UploadCloud } from 'lucide-react';
import { useUIStore } from '../../store';

export const MediaDropzone: React.FC = () => {
  const {
    audioPath,
    imagePath,
    videoPath,
    setAudioPath,
    setImagePath,
    setVideoPath,
  } = useUIStore();

  const [isDragging, setIsDragging] = useState(false);
  const audioInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    for (const file of files) {
      processFile(file.name);
    }
  };

  const processFile = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    if (ext === 'wav' || ext === 'mp3') {
      setAudioPath(fileName);
    } else if (['png', 'jpg', 'jpeg', 'webp'].includes(ext || '')) {
      setImagePath(fileName);
    } else if (['mp4', 'mov', 'webm'].includes(ext || '')) {
      setVideoPath(fileName);
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`border-2 border-dashed rounded-xl p-4 text-center transition-all select-none ${
        isDragging
          ? 'border-cyan-400 bg-cyan-950/30'
          : 'border-zinc-800 bg-zinc-900/60 hover:border-zinc-700'
      }`}
    >
      {/* Hidden File Inputs for Native Browsing */}
      <input
        ref={audioInputRef}
        type="file"
        accept=".wav,.mp3"
        className="hidden"
        onChange={(e) => {
          if (e.target.files?.[0]) processFile(e.target.files[0].name);
        }}
      />
      <input
        ref={imageInputRef}
        type="file"
        accept=".png,.jpg,.jpeg,.webp"
        className="hidden"
        onChange={(e) => {
          if (e.target.files?.[0]) processFile(e.target.files[0].name);
        }}
      />
      <input
        ref={videoInputRef}
        type="file"
        accept=".mp4,.mov,.webm"
        className="hidden"
        onChange={(e) => {
          if (e.target.files?.[0]) processFile(e.target.files[0].name);
        }}
      />

      {/* 3 Input Slot Cards */}
      <div className="grid grid-cols-3 gap-3 mb-3">
        {/* Audio Slot */}
        <div
          onClick={() => audioInputRef.current?.click()}
          className={`p-3 rounded-lg border flex flex-col items-center justify-center relative cursor-pointer transition ${
            audioPath
              ? 'border-cyan-500/40 bg-cyan-950/20 text-cyan-300'
              : 'border-zinc-800 bg-zinc-900/80 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200'
          }`}
        >
          {audioPath && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setAudioPath(null);
              }}
              title="Quitar audio"
              className="absolute top-1.5 right-1.5 p-0.5 hover:bg-zinc-800 text-zinc-400 hover:text-white rounded"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
          <Music className={`w-5 h-5 mb-1.5 ${audioPath ? 'text-cyan-400' : 'text-zinc-500'}`} />
          <span className="text-[11px] font-mono font-medium truncate max-w-full px-1">
            {audioPath || 'Subir Audio'}
          </span>
          <span className="text-[9px] text-zinc-500 font-mono mt-0.5">.WAV / .MP3</span>
        </div>

        {/* Character Image Slot */}
        <div
          onClick={() => imageInputRef.current?.click()}
          className={`p-3 rounded-lg border flex flex-col items-center justify-center relative cursor-pointer transition ${
            imagePath
              ? 'border-fuchsia-500/40 bg-fuchsia-950/20 text-fuchsia-300'
              : 'border-zinc-800 bg-zinc-900/80 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200'
          }`}
        >
          {imagePath && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setImagePath(null);
              }}
              title="Quitar imagen"
              className="absolute top-1.5 right-1.5 p-0.5 hover:bg-zinc-800 text-zinc-400 hover:text-white rounded"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
          <ImageIcon className={`w-5 h-5 mb-1.5 ${imagePath ? 'text-fuchsia-400' : 'text-zinc-500'}`} />
          <span className="text-[11px] font-mono font-medium truncate max-w-full px-1">
            {imagePath || 'Subir Personaje'}
          </span>
          <span className="text-[9px] text-zinc-500 font-mono mt-0.5">.PNG / .JPG</span>
        </div>

        {/* Video Mocap Slot */}
        <div
          onClick={() => videoInputRef.current?.click()}
          className={`p-3 rounded-lg border flex flex-col items-center justify-center relative cursor-pointer transition ${
            videoPath
              ? 'border-emerald-500/40 bg-emerald-950/20 text-emerald-300'
              : 'border-zinc-800 bg-zinc-900/80 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200'
          }`}
        >
          {videoPath && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setVideoPath(null);
              }}
              title="Quitar video"
              className="absolute top-1.5 right-1.5 p-0.5 hover:bg-zinc-800 text-zinc-400 hover:text-white rounded"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
          <Video className={`w-5 h-5 mb-1.5 ${videoPath ? 'text-emerald-400' : 'text-zinc-500'}`} />
          <span className="text-[11px] font-mono font-medium truncate max-w-full px-1">
            {videoPath || 'Subir Mocap'}
          </span>
          <span className="text-[9px] text-zinc-500 font-mono mt-0.5">.MP4 / .MOV</span>
        </div>
      </div>

      <div className="flex items-center justify-center gap-1.5 text-[11px] text-zinc-400">
        <UploadCloud className="w-3.5 h-3.5 text-zinc-500" />
        <span>Arrastra archivos o haz clic en cualquier recuadro para seleccionar</span>
      </div>
    </div>
  );
};

export default MediaDropzone;
