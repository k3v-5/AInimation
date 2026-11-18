# StykAnimate MCP server

<p align="center">
  <img src="assets/python-vs-java.gif" alt="A stick figure animation built entirely through the StykAnimate MCP server" width="620">
</p>

<p align="center"><sub>
  Every frame above came from tool calls against this server — the figures, the poses, the
  timing and the layers. The project it came from is
  <a href="assets/python-vs-java.styk">assets/python-vs-java.styk</a>.
</sub></p>

An [MCP](https://modelcontextprotocol.io) server for [StykAnimate](https://stykanimate.com), the
open-source stick figure animation app. It lets an AI assistant open a StykAnimate or Pivot
project, read its rig and timeline, and change the animation — without a screen, a GPU or a
browser.

The server reuses the app's own document model, rig evaluator and file codec, so a project it
opens is the same project the desktop app opens, and a project it writes is the same project the
app writes.

## What it can do

**Read a project.** Open a `.styk`, `.stkz`, `.stykmov`, `.piv` or `.stk` file and report its
canvas, frame rate, keyframes, layers, figure definitions and instances.

**Read the rig.** Evaluate the animation at any tick and get back where every joint sits in
canvas pixels, where each segment starts and ends, and what the inverse kinematics controllers
are doing. This is the part that makes the server useful: a model can answer "where is the
character's left hand at frame 30?" and act on the answer.

**Change the animation.** Move, rotate, scale, flip, align and re-order figures. Set a joint's
angle, length or world position. Move an inverse kinematics target. Add, delete, duplicate and
retime keyframes. Recolour figures, parts, layers and the scene. Every change is one undoable
step, and `history_undo` / `history_redo` walk back through them.

**Write a project.** Save as a StykAnimate project, a portable figure or a movieclip, or export
to a Pivot `.piv` or `.stk` file.

## The example at the top

The animation in the picture was built by asking this server to draw it, one tool call at a
time. Nothing was drawn by hand and nothing was scripted against the file format.

| Step | Tool |
| --- | --- |
| Put the two characters, the ball and the code lines on the stage | `figure_add` |
| Pose them, with the arm and leg angles solved against the rig | `pose_set` |
| Build the timeline — fast beats at 4 ticks, slow beats at 12 to 24 | `keyframe_edit`, `keyframe_timing` |
| Name the layers `STAGE`, `PYTHON`, `JAVA`, `BOILERPLATE`, `TASK` | `layer_edit` |
| Write the file and check it | `project_save`, `project_validate` |

The result is [assets/python-vs-java.styk](assets/python-vs-java.styk): 14 keyframes, 129 ticks,
24 fps, six figure definitions. It opens in the StykAnimate app like any other project.

## Install

From GitHub, which needs no account and no registry:

```sh
npx -y github:ghassenTn/stykanimate-mcp
```

Pin a release:

```sh
npx -y github:ghassenTn/stykanimate-mcp#v0.1.0
```

Or install the tarball attached to a release:

```sh
npx -y https://github.com/ghassenTn/stykanimate-mcp/releases/download/v0.1.0/stykanimate-mcp-0.1.0.tgz
```

Or install the MCP bundle, which a client that supports one-click installs can
open directly:

```sh
npx -y https://github.com/ghassenTn/stykanimate-mcp/releases/download/v0.1.0/stykanimate-mcp-0.1.0.mcpb
```

Or clone and run it:

```sh
git clone https://github.com/ghassenTn/stykanimate-mcp.git
cd stykanimate-mcp
npm ci
node src/index.js
```

The package is also prepared for the npm registry as `stykanimate-mcp`; see
[Publishing](#publishing) once npm access is available.

### Connect a client

Claude Code:

```sh
claude mcp add stykanimate -- npx -y github:ghassenTn/stykanimate-mcp
```

Claude Desktop, Cursor, or any client that reads `mcpServers`:

```json
{
  "mcpServers": {
    "stykanimate": {
      "command": "npx",
      "args": ["-y", "github:ghassenTn/stykanimate-mcp"]
    }
  }
}
```

VS Code (`.vscode/mcp.json`):

```json
{
  "servers": {
    "stykanimate": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "github:ghassenTn/stykanimate-mcp"]
    }
  }
}
```

### Run it as a service

```sh
stykanimate-mcp --transport http --port 7331
```

The HTTP transport speaks Streamable HTTP. It only accepts requests from `localhost`, `127.0.0.1`
and `[::1]`, and it rejects a request that carries a foreign `Origin` header, so a page in a
browser cannot drive a server that reads files from the machine. Put your own authentication in
front of it before exposing it beyond the machine.

## Requirements

- Node.js 20 or newer.
- Python 3.10 or newer, **only** to read and write Pivot `.piv` and `.stk` files. The server
  starts the bundled codec on demand and stops it again when it has been idle, so a session that
  only touches StykAnimate files never starts a Python process. Set `STYK_PYTHON` to choose a
  specific interpreter.

## The tools

| Tool | What it does |
| --- | --- |
| `capabilities` | What this server supports, and which projects are open. |
| `project_open` | Open a project file. |
| `project_close` | Close a project. |
| `project_describe` | The structure of the open project. |
| `project_validate` | Run the editor's own document validation. |
| `project_save` | Write the project to a file. |
| `project_timeline` | The keyframes and the playback timeline. |
| `project_seek` | Move the playhead. |
| `figure_list` | The figure instances in the project. |
| `figure_describe` | One figure's definition, rig and instance. |
| `figure_add` | Add a figure instance. |
| `figure_duplicate` | Copy a figure, with its pose. |
| `figure_delete` | Remove a figure from keyframes. |
| `figure_transform` | Move, rotate, scale, flip, align, centre or re-order figures. |
| `pose_evaluate` | The solved rig at a tick. |
| `pose_set` | Set a figure's root, scale and joint angles, lengths and positions. |
| `pose_ik_set` | Move an inverse kinematics target. |
| `pose_set_ik` | Turn a joint's inverse kinematics controller on or off, or change it. |
| `pose_reset` | Return a figure to its rest pose. |
| `keyframe_edit` | Add, delete, duplicate or move keyframes. |
| `keyframe_timing` | Change a keyframe's length, the frame rate or the canvas size. |
| `layer_list` | The layers of the project. |
| `layer_edit` | Create, rename, delete, reorder, fill, show, hide, lock and unlock layers. |
| `style_set` | Recolour a figure, a part, a layer or the scene. |
| `history_undo` | Undo the last change. |
| `history_redo` | Redo the last undone change. |

### How a model should use it

A typical conversation goes: `capabilities` → `project_open` → `project_describe` →
`figure_describe` → `pose_evaluate` → a change → `pose_evaluate` again to check the result.

Two conventions matter:

- **A frame number is a place on the timeline** — one of the positions the playhead moves through.
  The pose and figure tools use it, because they act on what the animation shows. The "playback"
  section of `project_timeline` lists those places, and their number is the frame number.
- **A keyframe number in `keyframe_edit` and `keyframe_timing` is a stored pose**, one entry in
  the project's pose list, because those tools add, remove and retime poses. The "keyframes"
  section of `project_timeline` lists those, and says where each one is shown.

On a project with one keyframe per moment the two are the same number, which is the case for
every project imported from Pivot. A project with an advanced timeline can hold more poses than
it shows, and there the two differ: a pose the playback does not reach has no place, and only
the keyframe tools can name it.

A **figure** is named by its instance id, and a **joint** by its handle id. Both come from
`figure_list` and `figure_describe`.

### Projects with an advanced timeline

StykAnimate has two timelines. The simple one is a list of keyframes, each holding the pose of
every figure, and it is what a project imported from Pivot uses. The advanced one is a sheet of
cells that sample stored poses over spans, and it is what the app's own new projects use.

The server works on the stored poses the playback reaches. The sheet's own cells are not exposed,
so a few results differ from the app:

- `figure_list` reports the figures the sheet shows at the playhead, and lists the stored poses
  that hold each of them. A figure the sheet added appears in the first list and in none of the
  second.
- The pose and figure tools act on the place they are given, so they change what the sheet
  shows.
- `style_set` on a figure names the ticks the playback reaches, because that is what a sheet
  holds.
- A keyframe the playback does not reach can still be added, retimed and removed through the
  keyframe tools, but nothing shows it.
- `project_describe` reports `advancedTimeline: true` when a project uses one.

Everything else — opening, describing, transforming, recolouring, saving — behaves the same in
both.


## Resources

| Resource | What it holds |
| --- | --- |
| `stykanimate://projects` | A summary of every open project. |
| `stykanimate://projects/{project}/document` | The whole editable document. |
| `stykanimate://projects/{project}/pose` | The solved rig at a tick. |

## How it is built

```
src/            The server: tools, session, file I/O and the codec client
src/tools/      One module per group of tools
vendor/         The StykAnimate editor core, vendored from the app
py/             The Python codec, vendored from the app
scripts/        The vendor sync and the package checks
test/           The tests
```

`vendor/stykanimate` holds the transitive import closure of the app's `editor.mjs`,
`native-container.mjs` and friends: about 300 modules with no third-party runtime dependencies.
`scripts/vendor-sync.mjs` refreshes it from a checkout of the app and records what it copied in
`vendor/stykanimate/PROVENANCE.json`. `npm run vendor:check` fails when the vendored copy has
drifted from its source.

The sync looks for the app in a sibling `StykAnimate-App` directory by default. Point it
elsewhere with `--source <path>` or the `STYKANIMATE_SOURCE` environment variable:

```sh
npm run vendor -- --source ../StykAnimate-App
```

## Development

```sh
npm ci
npm run check     # syntax, tool registration, vendored-core freshness, registry manifest
npm test          # the test suite
```

`node scripts/demo-session.mjs` drives the server over stdio the way a client does and prints
every answer, which is the quickest way to see the whole flow: open, describe, pose, time,
recolour, undo, save and reopen.

The tests need a Python interpreter for the codec test; that one test skips itself when there is
none.

## Publishing

The package is prepared for the npm registry as `stykanimate-mcp`.

```sh
npm ci
npm run check && npm test
npm run publish:package
```

`prepublishOnly` runs the checks and the tests, so a publish cannot ship a broken package. The
version in `package.json` and the one in `server.json` have to move together, because the
registry manifest names the exact package version.

A tagged release publishes the package again with provenance:

```sh
git tag v0.1.0 && git push origin v0.1.0
```

The workflow needs an `NPM_TOKEN` secret in the repository settings.

### The MCP bundle

`npm run bundle` builds `build/stykanimate-mcp-<version>.mcpb`: a zip archive with the server,
its runtime dependencies, the vendored editor core, the Python codec and a manifest that tells a
client how to run it. It is the package type the official MCP registry accepts without a package
registry, and clients that support one-click installs can open it directly.

The bundle's hash goes in `server.json` under `packages[0].file_sha256`, so the registry and a
client can both check the file they download. The build writes the hash next to the bundle:

```sh
npm run bundle
cat build/stykanimate-mcp-0.1.0.mcpb.sha256
```

Until npm is available, the release tarball and the bundle are the installable artifacts: they
are the same package the registry would serve, and they are attached to every release.

## Licence

GPL-3.0-or-later, the same licence as the StykAnimate app this server is built from. See
[LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).
