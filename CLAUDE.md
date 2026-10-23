# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Strudel files repository that provides a web interface for managing and accessing Strudel music pattern files. Strudel is a live coding language for music patterns, and this repository serves as a collection/library of `.strudel` files that can be opened directly in strudel.cc.

## Architecture

The repository has a simple static site architecture:

- `index.html` - Main web interface that displays a sortable table of all Strudel files
- `data/` - Contains generated JSON metadata about files and docs
  - `files.json` - Metadata for all .strudel files (title, author, modified date, path)
  - `docs.json` - Metadata for documentation files
- `files/` - Contains the actual .strudel pattern files
- `samples/` - Audio sample files organized by category, referenced by strudel.json
- `strudel.json` - Configuration mapping sample categories to their file lists
- `scripts/` - Python utilities for data generation and local development
- `docs/` - Documentation files (markdown)

### Key Components

**Web Interface (index.html)**:
- Fetches file metadata from `data/files.json`
- For each file, loads the content and base64-encodes it
- Creates direct links to strudel.cc with encoded content as URL fragment
- Provides sortable table interface

**Data Generation (scripts/update_data.py)**:
- Scans `files/` directory for .strudel files
- Extracts metadata from file comments (@title, @by tags)
- Generates `data/files.json` with file listings
- Also handles documentation files in `docs/` directory

## Common Development Commands

### Local Development Server
```bash
# Check if server is already running
curl -s http://localhost:8001 > /dev/null && echo "Server already running" || echo "Server not running"

# Only if not already running (py launcher, from repo root):
py -m http.server 8001
```
The site will be available at http://localhost:8001 (main interface at http://localhost:8001/index.html)

**Note**: Generally, the local server will already be running at port 8001. Always check if it's running before attempting to start it.

### Update File Metadata
```bash
# From repo root (py launcher, per machine-wide Python rules)
py scripts/update_data.py
```
This regenerates `data/files.json` and `data/docs.json` based on current files.
Run it after adding, renaming, or re-staging any `.strudel` file.

### Validate Strudel Files (headless, no browser)
```bash
node scripts/eval_strudel.mjs files/your_file.strudel              # summary
node scripts/eval_strudel.mjs files/your_file.strudel --json       # full event dump
node scripts/eval_strudel.mjs files/your_file.strudel --quiet      # validation only
node scripts/eval_strudel.mjs -e 's("bd hh sd hh")' --cycles 4     # inline code
```
This runs the actual Strudel engine (`@strudel/core` + transpiler) in Node:
- Reports syntax/eval errors with line and column — in about a second
- Dumps the scheduled events (begin/end time, note, sound, gain, ...) so the
  musical structure can be verified without listening
- Reports tempo, sample sources, and per-voice event counts for `$:` voices
  (muted `_$:` voices are listed but excluded from the event dump)
- Stubs playback-only functions (`samples`, `setcpm`, visuals); anything it
  had to stub beyond the known list appears as a warning
- Exit code 0 = valid, 1 = error (machine-checkable)

Requires `npm install` once (the `postinstall` hook patches a broken
`@kabelsalat/web` package entry — see `scripts/patch_kabelsalat.mjs`).

### Test Playback in the Browser
Preferred: use the Claude-in-Chrome tools against the user's real browser.
strudel.cc exposes its REPL as `window.strudelMirror`, so after navigating
to https://strudel.cc (or opening a `#<base64>` link):
```js
strudelMirror.setCode(codeString);   // inject the pattern
await strudelMirror.evaluate();      // compile + start playback
strudelMirror.repl.scheduler.started // true if playing
strudelMirror.repl.state.evalError   // eval error, if any
strudelMirror.stop();                // stop playback
```
The user hears the result live — always stop playback when done testing.

Fallback (puppeteer, headless):
```bash
node scripts/test_strudel_browser.mjs files/your_file.strudel [--headed] [--json]
```
**Known limitation on this machine**: strudel.cc's JS modules stall forever in
every puppeteer-launched Chrome (bundled or system, headless or headed), so
this script currently only works elsewhere. Use the Claude-in-Chrome route here.

### File Organization

**Strudel Files**: Place new .strudel files in the `files/` directory. Include metadata in comments:
```
// @title Your Song Title
// @by Your Name
```

**Audio Samples**: Place samples in `samples/category_name/` and update `strudel.json` to reference them.

## Development Notes

- No build process required - this is a static site
- The main interface dynamically loads and encodes .strudel files for strudel.cc integration
- File metadata is cached in JSON files and should be regenerated when files change
- The repository uses GitHub Pages for hosting at the main branch

## Strudel Code Logic

When working with Strudel code logic, patterns, or syntax, use the Context7 MCP server to access up-to-date Strudel documentation. Use the following approach:

1. First resolve the library ID: Context7 `resolve-library-id` with `libraryName: "strudel"`
2. Then query the docs: Context7 `query-docs` with library ID `"/tidalcycles/strudel"`

This ensures accurate understanding of:
- Pattern syntax and functions (e.g., `note()`, `s()`, `cat()`, `seq()`)
- Mini-notation syntax (e.g., `"c3 [e3 g3]*2"`)
- Audio sample handling and sound selection
- Timing and sequencing functions (e.g., `slow()`, `fast()`, `rev()`)
- Effects and transformations (e.g., `add()`, `jux()`, `off()`)
- Method chaining patterns (e.g., `.note().s("piano").room(0.5)`)
- Proper Strudel coding conventions and best practices

## AI Composing Workflow

When asked to write or modify Strudel music, follow this loop:

1. **Consult docs** via Context7 for any function you're not certain about.
2. **Write/edit** the `.strudel` file in `files/`, with the standard metadata
   header (`@title`, `@by`, `@version`, `@stage`).
3. **Validate headlessly**: `node scripts/eval_strudel.mjs files/<file>.strudel`
   — fix any errors; check the event dump matches the musical intent
   (right notes, right rhythm, no silent voices, correct voice counts).
4. **Regenerate metadata**: `py scripts/update_data.py`.
5. **Hand over for listening**: either open the file in the user's browser via
   Claude-in-Chrome (`strudelMirror.setCode(...)` + `evaluate()`), or give the
   user the strudel.cc link. Only the user can judge how it sounds — always
   end an iteration by letting them listen.

To build a strudel.cc link from a file:
`https://strudel.cc/#` + URL-encoded base64 of the UTF-8 file content
(same encoding as `js/script.js` uses).