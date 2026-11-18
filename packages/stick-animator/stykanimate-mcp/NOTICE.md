# Notices

This package is a derivative work of [StykAnimate](https://stykanimate.com), the open-source
stick figure animation app, and is distributed under the same terms.

## The vendored application core

`vendor/stykanimate/` holds the transitive import closure of the StykAnimate editor core:

- `src/editor.mjs` and its command mixins — the document model, the command history and the
  validation rules.
- `src/pivot/` — the rig evaluator, the geometry builder and the scene validator.
- `src/native-container.mjs` — the reader and writer for the StykAnimate native file formats.
- `src/editor-load.mjs`, `src/demo.mjs`, `src/startup-document.mjs` and the modules they need.

`vendor/stykanimate/vendor/` holds the third-party helpers the app's own tree references:
`earcut.mjs` (ISC, see `earcut.LICENSE`) and the zstd WebAssembly build (MIT, see
`zstd/LICENSE`).

`vendor/stykanimate/PROVENANCE.json` records the upstream repository, the exact commit, the file
list and a digest of everything that was copied. `scripts/vendor-sync.mjs` refreshes the copy
from a checkout of the app.

## The vendored Python codec

`py/backend/` and `py/codecs/` hold the Python codec service that reads and writes Pivot `.piv`
and `.stk` files. It is the same code the desktop app runs, copied with its `backend/` and
`codecs/` layout intact so its own relative lookups keep working.

## Trademarks

The StykAnimate name and logo identify the official project. This package is not affiliated with
or endorsed by Pivot Animator or Stick Nodes; those names appear only to describe file
compatibility.
