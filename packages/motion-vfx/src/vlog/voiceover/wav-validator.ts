import { InvalidWavError } from "../contracts/errors.js";
import { AUDIO_SPECS } from "../contracts/vlog.constants.js";

/** Metadatos decodificados de un encabezado WAV */
export interface ValidatedWavMetadata {
  sampleRate: number;
  channels: number;
  bitDepth: number;
  dataSizeBytes: number;
  durationSeconds: number;
  isCanonical: boolean;
}

/**
 * Validador e inspector binario estricto de archivos y buffers WAV (PCM 16-bit 44.1kHz Mono).
 * Verifica la firma RIFF/WAVE, integridad de subchunks y ausencia de corrupción.
 */
export class WavValidator {
  /**
   * Valida un buffer de audio WAV asegurando cumplimiento del formato canónico de voiceover.
   */
  public static validateBuffer(buffer: Buffer | Uint8Array, enforceCanonical = true): ValidatedWavMetadata {
    if (!buffer || buffer.length < 44) {
      throw new InvalidWavError(`WAV buffer is truncated or smaller than minimum header size (got ${buffer?.length ?? 0} bytes, expected >= 44)`);
    }

    const buf = Buffer.isBuffer(buffer) ? buffer : Buffer.from(buffer);

    // 1. Chunk ID: "RIFF"
    const riffHeader = buf.toString("ascii", 0, 4);
    if (riffHeader !== "RIFF") {
      throw new InvalidWavError(`Invalid RIFF header: expected 'RIFF', got '${riffHeader}'`);
    }

    // 2. Format: "WAVE"
    const waveFormat = buf.toString("ascii", 8, 12);
    if (waveFormat !== "WAVE") {
      throw new InvalidWavError(`Invalid WAVE container: expected 'WAVE', got '${waveFormat}'`);
    }

    // 3. Buscar subchunk "fmt "
    let offset = 12;
    let foundFmt = false;
    let audioFormat = 0;
    let channels = 0;
    let sampleRate = 0;
    let bitDepth = 0;

    let foundData = false;
    let dataSizeBytes = 0;
    let dataOffset = 0;

    while (offset < buf.length - 8) {
      const chunkId = buf.toString("ascii", offset, offset + 4);
      const chunkSize = buf.readUInt32LE(offset + 4);

      if (chunkId === "fmt ") {
        foundFmt = true;
        audioFormat = buf.readUInt16LE(offset + 8);
        channels = buf.readUInt16LE(offset + 10);
        sampleRate = buf.readUInt32LE(offset + 12);
        bitDepth = buf.readUInt16LE(offset + 22);
      } else if (chunkId === "data") {
        foundData = true;
        dataSizeBytes = chunkSize;
        dataOffset = offset + 8;
        break; // el data chunk contiene las muestras PCM
      }

      offset += 8 + chunkSize;
    }

    if (!foundFmt) {
      throw new InvalidWavError("Missing 'fmt ' chunk in WAV header");
    }

    if (!foundData) {
      throw new InvalidWavError("Missing 'data' chunk in WAV header");
    }

    // Verificar formato PCM (1)
    if (audioFormat !== 1) {
      throw new InvalidWavError(`Unsupported audio format: expected PCM (1), got format code ${audioFormat}`);
    }

    // Verificar que los bytes declarados de audio existen realmente en el buffer
    const availableDataBytes = buf.length - dataOffset;
    if (availableDataBytes < dataSizeBytes) {
      throw new InvalidWavError(`WAV buffer is truncated: declared ${dataSizeBytes} data bytes, but only ${availableDataBytes} available`);
    }

    const bytesPerSample = (bitDepth / 8) * channels;
    if (bytesPerSample <= 0) {
      throw new InvalidWavError(`Invalid sample frame size (bitDepth: ${bitDepth}, channels: ${channels})`);
    }

    const durationSeconds = dataSizeBytes / (sampleRate * bytesPerSample);

    const isCanonical =
      sampleRate === AUDIO_SPECS.VOICEOVER.sampleRate &&
      channels === AUDIO_SPECS.VOICEOVER.channels &&
      bitDepth === AUDIO_SPECS.VOICEOVER.bitDepth;

    if (enforceCanonical && !isCanonical) {
      throw new InvalidWavError(
        `WAV does not meet canonical voiceover specs (${AUDIO_SPECS.VOICEOVER.sampleRate}Hz, ${AUDIO_SPECS.VOICEOVER.channels}ch, ${AUDIO_SPECS.VOICEOVER.bitDepth}bit). Got: ${sampleRate}Hz, ${channels}ch, ${bitDepth}bit`
      );
    }

    return {
      sampleRate,
      channels,
      bitDepth,
      dataSizeBytes,
      durationSeconds: Number(durationSeconds.toFixed(4)),
      isCanonical,
    };
  }

  /**
   * Crea un buffer WAV canónico (PCM 16-bit 44.1kHz Mono) a partir de muestras Int16Array.
   */
  public static createCanonicalWav(pcmSamples: Int16Array): Buffer {
    const sampleRate = AUDIO_SPECS.VOICEOVER.sampleRate; // 44100
    const channels = AUDIO_SPECS.VOICEOVER.channels; // 1
    const bitDepth = AUDIO_SPECS.VOICEOVER.bitDepth; // 16
    const bytesPerSample = (bitDepth / 8) * channels; // 2
    const dataSize = pcmSamples.length * 2;
    const totalFileSize = 44 + dataSize;

    const buffer = Buffer.alloc(totalFileSize);

    // RIFF chunk descriptor
    buffer.write("RIFF", 0, "ascii");
    buffer.writeUInt32LE(totalFileSize - 8, 4);
    buffer.write("WAVE", 8, "ascii");

    // "fmt " sub-chunk
    buffer.write("fmt ", 12, "ascii");
    buffer.writeUInt32LE(16, 16); // tamaño subchunk fmt (16 para PCM)
    buffer.writeUInt16LE(1, 20); // formato de audio 1 = PCM
    buffer.writeUInt16LE(channels, 22); // 1 canal (mono)
    buffer.writeUInt32LE(sampleRate, 24); // 44100
    buffer.writeUInt32LE(sampleRate * bytesPerSample, 28); // ByteRate = 88200
    buffer.writeUInt16LE(bytesPerSample, 32); // BlockAlign = 2
    buffer.writeUInt16LE(bitDepth, 34); // 16 bits por muestra

    // "data" sub-chunk
    buffer.write("data", 36, "ascii");
    buffer.writeUInt32LE(dataSize, 40);

    // Copiar muestras PCM
    for (let i = 0; i < pcmSamples.length; i++) {
      buffer.writeInt16LE(pcmSamples[i], 44 + i * 2);
    }

    return buffer;
  }
}
