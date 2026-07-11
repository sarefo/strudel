---
name: strudel
description: Compose, edit, or debug a Strudel pattern file end-to-end - write the code, validate it headlessly, regenerate metadata, and hand it over for listening. Use when the user asks for new music, changes to a track, or why a .strudel file is broken.
---

# Strudel compose-and-test loop

Argument: a description of the music to write/change, or a path to a
`.strudel` file to fix. Follow the "AI Composing Workflow" in CLAUDE.md:

1. If unsure about any Strudel function or mini-notation, consult Context7
   (`/tidalcycles/strudel`) before writing code.
2. Write or edit the file in `files/`, keeping the metadata header
   (`@title`, `@by`, `@version`, `@license`, `@url`, `@stage`).
   Prefer `$:` voice lines (with `_$:` for muted scratch voices) and the
   idioms already used by existing files in `files/`.
3. Validate: `node scripts/eval_strudel.mjs files/<file>.strudel`
   - On error: fix and re-run until clean.
   - On success: inspect the summary/event dump. Check notes, rhythm, tempo,
     and per-voice counts against the request. Use `--json --cycles N` to see
     the full timeline when detail matters.
4. Regenerate metadata: `py scripts/update_data.py`
5. Let the user listen — pick one:
   - Claude-in-Chrome: navigate a tab to https://strudel.cc, then
     `strudelMirror.setCode(<code>); await strudelMirror.evaluate();`
     check `strudelMirror.repl.state.evalError`, let it play, and ask the
     user for verdict. Call `strudelMirror.stop()` before making changes.
   - Or print the strudel.cc link: `https://strudel.cc/#` + URL-encoded
     base64 of the file content.

Do not declare a piece finished on validation alone — the user's ears are
the final test.
