import { AudioBus, AudioBusType } from "./audio-ir.types.js";

/**
 * REQ-019: Jerarquía Canónica de 8 Buses de Audio con Validación de DAG y Ganancia
 */
export class HierarchicalMixer {
  public static readonly CANONICAL_BUS_IDS: AudioBusType[] = [
    "MASTER",
    "VOICE",
    "DIALOGUE",
    "MUSIC",
    "AMBIENCE",
    "ROOM_TONE",
    "SFX",
    "CRITICAL_SFX",
    "ARCHIVE_AUDIO",
  ];

  private readonly buses: Map<AudioBusType, AudioBus> = new Map();

  constructor(customBuses?: AudioBus[]) {
    if (customBuses && customBuses.length > 0) {
      for (const bus of customBuses) {
        this.addBus(bus);
      }
      this.validateHierarchy();
    } else {
      this.initializeDefaultHierarchy();
    }
  }

  private initializeDefaultHierarchy(): void {
    const master: AudioBus = {
      id: "MASTER",
      name: "Master Output",
      gainDb: 0.0,
      pan: 0.0,
      mute: false,
      solo: false,
      effects: [],
      automations: [],
    };
    this.buses.set("MASTER", master);

    const childBuses: Array<{ id: AudioBusType; name: string; defaultGain: number }> = [
      { id: "VOICE", name: "Voice Track", defaultGain: 0.0 },
      { id: "DIALOGUE", name: "Dialogue Track", defaultGain: 0.0 },
      { id: "MUSIC", name: "Music Bed", defaultGain: -6.0 },
      { id: "AMBIENCE", name: "Atmospheric Ambience", defaultGain: -12.0 },
      { id: "ROOM_TONE", name: "Room Tone Floor", defaultGain: -18.0 },
      { id: "SFX", name: "Sound Effects", defaultGain: -3.0 },
      { id: "CRITICAL_SFX", name: "Critical Narrative SFX", defaultGain: 0.0 },
      { id: "ARCHIVE_AUDIO", name: "Historical Archive", defaultGain: -2.0 },
    ];

    for (const item of childBuses) {
      this.buses.set(item.id, {
        id: item.id,
        name: item.name,
        parentBusId: "MASTER",
        gainDb: item.defaultGain,
        pan: 0.0,
        mute: false,
        solo: false,
        effects: [],
        automations: [],
      });
    }
  }

  public addBus(bus: AudioBus): void {
    if (this.buses.has(bus.id)) {
      throw new Error(`[AUDIO_MIXER_ERROR] Bus duplicado detectado: '${bus.id}'`);
    }
    // Clamping de ganancia segura [-60 dB, +12 dB]
    const clampedGain = Math.max(-60, Math.min(12, bus.gainDb));
    this.buses.set(bus.id, {
      ...bus,
      gainDb: clampedGain,
      pan: Math.max(-1.0, Math.min(1.0, bus.pan)),
    });
  }

  public getBus(id: AudioBusType): AudioBus {
    const bus = this.buses.get(id);
    if (!bus) {
      throw new Error(`[AUDIO_MIXER_ERROR] Bus no encontrado: '${id}'`);
    }
    return bus;
  }

  public getAllBuses(): AudioBus[] {
    return Array.from(this.buses.values());
  }

  /**
   * REQ-019: Validación de ciclos en el ruteo de buses (Detección de bucles de retroalimentación)
   */
  public validateHierarchy(): void {
    for (const [id, bus] of this.buses) {
      const visited = new Set<AudioBusType>([id]);
      let currentParent = bus.parentBusId;

      while (currentParent) {
        if (visited.has(currentParent)) {
          throw new Error(`[AUDIO_BUS_CYCLE_ERROR] Ciclo detectado en ruteo de bus: '${id}' -> '${currentParent}'`);
        }
        visited.add(currentParent);
        const parentBus = this.buses.get(currentParent);
        if (!parentBus) {
          throw new Error(`[AUDIO_ROUTING_ERROR] El bus '${id}' referencia a un padre inexistente: '${currentParent}'`);
        }
        currentParent = parentBus.parentBusId;
      }
    }
  }

  /**
   * Calcula la ganancia efectiva acumulada desde un bus hasta el MASTER
   */
  public getEffectiveGainDb(busId: AudioBusType): number {
    const bus = this.getBus(busId);
    let totalGain = bus.gainDb;
    let currentParent = bus.parentBusId;

    while (currentParent) {
      const parent = this.getBus(currentParent);
      totalGain += parent.gainDb;
      currentParent = parent.parentBusId;
    }

    return totalGain;
  }

  /**
   * Determina si un bus está efectivamente silenciado considerando mutes y solos de la jerarquía
   */
  public isBusAudible(busId: AudioBusType): boolean {
    const anySoloActive = Array.from(this.buses.values()).some((b) => b.solo);

    const bus = this.getBus(busId);
    if (bus.mute) return false;

    // Si algún bus tiene SOLO activado, este bus solo suena si él o algún ancestro/descendiente tiene SOLO
    if (anySoloActive && !bus.solo) {
      return false;
    }

    // Verificar si algún padre tiene MUTE
    let currentParent = bus.parentBusId;
    while (currentParent) {
      const parent = this.getBus(currentParent);
      if (parent.mute) return false;
      currentParent = parent.parentBusId;
    }

    return true;
  }
}
