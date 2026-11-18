/**
 * The single seam between this server and the vendored StykAnimate core.
 *
 * Everything the tools need from the editor — the document model, the rig
 * evaluator and the native container codec — is re-exported here so the
 * vendored tree can move without touching the tool layer.
 */
export { Editor } from '../vendor/stykanimate/src/editor.mjs';
export {
  buildContainerV2,
  decodeDocument,
  normalizeDecodedDocument,
} from '../vendor/stykanimate/src/native-container.mjs';
export { nativeFigureDocument } from '../vendor/stykanimate/src/native-figure.mjs';
export { createStartupDocument } from '../vendor/stykanimate/src/startup-document.mjs';
