// Core & Evaluators
export * from "./core/CaptionEvaluator.js";
export * from "./core/CaptionTrack.js";

// Layout & Safe Zones
export * from "./layout/CaptionLayoutEngine.js";
export * from "./layout/CaptionPositionResolver.js";
export * from "./layout/DynamicCaptionLayoutEngine.js";
export * from "./safezones/SafeZoneResolver.js";

// Backgrounds & Animations
export * from "./backgrounds/AdaptiveBackgroundEngine.js";
export * from "./animations/WordAnimationEngine.js";
export * from "./animations/WordKaraokeSyncEngine.js";

// Intelligence & Prosody
export * from "./intelligence/EmphasisScorer.js";
export * from "./intelligence/CaptionIntelligenceEngine.js";
export * from "./intelligence/SpeechRecognitionEngine.js";

// Emojis & Icons
export * from "./icons/EmojiPlacementEngine.js";

// Parsers & Normalizers
export * from "./transcript/TranscriptParser.js";
export * from "./transcript/SRTParser.js";
export * from "./transcript/WhisperJSONParser.js";
export * from "./normalizer/CaptionNormalizer.js";

// Presets & Segmentation
export * from "./presets/CaptionPresetRegistry.js";
export * from "./presets/ViralCaptionPresets.js";
export * from "./segmentation/CaptionSegmenter.js";

// Schemas & Serialization
export * from "./schemas/caption.schema.js";
export * from "./serialization/CaptionSerializer.js";

// Types
export * from "./types/index.js";
