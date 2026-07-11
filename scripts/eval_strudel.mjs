#!/usr/bin/env node
/**
 * Headless Strudel pattern evaluator.
 *
 * Validates a .strudel file and dumps the scheduled events (haps) as JSON,
 * without a browser or audio. This is the fast feedback loop for AI-assisted
 * composing: syntax/eval errors come back with messages, and the event
 * timeline shows exactly which notes/samples play at which times.
 *
 * Usage:
 *   node scripts/eval_strudel.mjs <file.strudel> [--cycles N] [--json] [--quiet]
 *   node scripts/eval_strudel.mjs -e "s('bd hh sd hh')" [--cycles N] [--json]
 *
 *   --cycles N  query N cycles of the pattern (default 2)
 *   --json      full machine-readable output (all events)
 *   --quiet     validation only: print ok/error, no events
 *
 * Exit code 0 = pattern evaluated successfully, 1 = error.
 *
 * Playback-only functions (samples, setcpm, visuals, ...) are stubbed; any
 * name the evaluator had to stub is listed in the output as a warning so
 * silently-wrong output can't masquerade as success.
 */
import { readFileSync } from 'fs';
import { basename } from 'path';

// ---------- CLI args ----------
const args = process.argv.slice(2);
const opts = { cycles: 2, json: false, quiet: false, file: null, code: null };
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === '--cycles') opts.cycles = parseFloat(args[++i]);
  else if (a === '--json') opts.json = true;
  else if (a === '--quiet') opts.quiet = true;
  else if (a === '-e') opts.code = args[++i];
  else if (!a.startsWith('-')) opts.file = a;
}
if (!opts.file && opts.code == null) {
  console.error('Usage: node scripts/eval_strudel.mjs <file.strudel> [--cycles N] [--json] [--quiet]');
  process.exit(1);
}

let code = opts.code;
if (opts.file) {
  try {
    code = readFileSync(opts.file, 'utf8');
  } catch (e) {
    console.error(`Cannot read file: ${e.message}`);
    process.exit(1);
  }
}

// ---------- load strudel packages (silencing their load-time chatter) ----------
const realLog = console.log;
const realWarn = console.warn;
console.log = () => {};
console.warn = () => {};

const core = await import('@strudel/core');
const mini = await import('@strudel/mini');
const tonal = await import('@strudel/tonal');
const draw = await import('@strudel/draw'); // pianoroll/scope/etc. as no-op-safe methods
const { evaluate } = await import('@strudel/transpiler');

console.log = realLog;
console.warn = realWarn;

const { evalScope, silence, Pattern, pure, stack } = core;

// ---------- stubs for playback/browser-only functions ----------
const info = { tempo: null, sampleSources: [], stubbedGlobals: [], stubbedMethods: [] };

const stubs = {
  samples: async (...srcs) => { info.sampleSources.push(...srcs.map(String)); },
  setcpm: (v) => { info.tempo = { cpm: Number(v) }; },
  setcps: (v) => { info.tempo = { cps: Number(v) }; },
  setCpm: (v) => { info.tempo = { cpm: Number(v) }; },
  setCps: (v) => { info.tempo = { cps: Number(v) }; },
  hush: () => silence,
  all: (fn) => silence,
  loadOrc: async () => {},
  loadCsound: async () => {},
  loadSoundfont: async () => {},
  // repl widgets: resolve to their current value
  slider: (v) => pure(Number(v)),
  sliderWithID: (id, v) => pure(Number(v)),
};

await evalScope(core, mini, tonal, draw, stubs);

// visualization methods live in the browser repl; make them no-op passthroughs
for (const name of [
  'punchcard', '_punchcard', 'pianoroll', '_pianoroll', 'spectrum', '_spectrum',
  'scope', '_scope', 'markcss', 'spiral', '_spiral',
]) {
  if (!Pattern.prototype[name]) Pattern.prototype[name] = function () { return this; };
}

// `$: pattern` voice lines transpile to `.p(id)`, which registers the voice
// with the repl scheduler. Mimic that: collect voices, stack the unmuted ones.
// Anonymous `$:` lines all get id '$', so uniquify instead of clobbering.
const voices = new Map();
let voiceSeq = 0;
Pattern.prototype.p = function (id) {
  id = String(id);
  if (voices.has(id)) id = `${id}#${++voiceSeq}`;
  voices.set(id, this);
  return this;
};
Pattern.prototype.q = function () { return silence; };

// ---------- evaluate, auto-stubbing unknown names (with warnings) ----------
async function tryEvaluate(code) {
  for (let attempt = 0; attempt < 20; attempt++) {
    try {
      return await evaluate(code);
    } catch (err) {
      const msg = String(err?.message || err);
      let m;
      if ((m = msg.match(/^(\w[\w$]*) is not defined$/))) {
        // unknown global -> stub as identity-ish pattern factory
        globalThis[m[1]] = (...a) => silence;
        info.stubbedGlobals.push(m[1]);
        continue;
      }
      if ((m = msg.match(/\.(\w[\w$]*) is not a function/))) {
        // unknown pattern method -> no-op passthrough
        Pattern.prototype[m[1]] = function () { return this; };
        info.stubbedMethods.push(m[1]);
        continue;
      }
      throw err;
    }
  }
  throw new Error('Too many unknown names; giving up auto-stubbing.');
}

let pattern;
try {
  ({ pattern } = await tryEvaluate(code));
  // when `$:` voices are registered, the repl plays those (not the return
  // value of the last statement); ids starting with '_' are muted
  if (voices.size > 0) {
    const active = [...voices.entries()].filter(([id]) => !id.startsWith('_'));
    pattern = active.length ? stack(...active.map(([, p]) => p)) : silence;
  }
} catch (err) {
  const out = {
    ok: false,
    file: opts.file ? basename(opts.file) : '(inline)',
    error: String(err?.message || err),
  };
  if (err?.loc) out.location = err.loc; // acorn syntax errors carry line/column
  if (opts.json) console.log(JSON.stringify(out, null, 2));
  else {
    console.log(`❌ ${out.file}: ${out.error}`);
    if (out.location) console.log(`   at line ${out.location.line}, column ${out.location.column}`);
  }
  process.exit(1);
}

// ---------- query events ----------
let haps = [];
let queryError = null;
try {
  haps = pattern.queryArc(0, opts.cycles);
} catch (err) {
  queryError = String(err?.message || err);
}

const frac = (f) => (typeof f?.valueOf === 'function' ? Number(f.valueOf()) : Number(f));
const events = haps
  .filter((h) => h.whole) // discrete events only (skip continuous signals)
  .map((h) => ({
    begin: frac(h.whole.begin),
    end: frac(h.whole.end),
    dur: frac(h.whole.end) - frac(h.whole.begin),
    value: h.value,
  }))
  .sort((a, b) => a.begin - b.begin);

// per-voice grouping: transpiler turns `$: pat` into .p('$'); values don't
// carry the label, so summarize by sound/note instead
const soundCounts = {};
for (const e of events) {
  const key = e.value?.s ?? e.value?.sound ?? (e.value?.note != null ? `note:${typeof e.value.note}` : typeof e.value);
  soundCounts[key] = (soundCounts[key] || 0) + 1;
}

// per-voice event counts (for `$:` / `name:` multi-voice files)
const voiceCounts = {};
for (const [id, p] of voices) {
  try {
    const n = p.queryArc(0, opts.cycles).filter((h) => h.whole).length;
    voiceCounts[id] = id.startsWith('_') ? `${n} (muted)` : n;
  } catch {
    voiceCounts[id] = 'query error';
  }
}

const result = {
  ok: true,
  file: opts.file ? basename(opts.file) : '(inline)',
  cycles: opts.cycles,
  eventCount: events.length,
  tempo: info.tempo,
  sampleSources: info.sampleSources,
  voices: voiceCounts,
  warnings: [
    ...info.stubbedGlobals.map((n) => `stubbed unknown global: ${n}`),
    ...info.stubbedMethods.map((n) => `stubbed unknown method: .${n}()`),
    ...(queryError ? [`query error: ${queryError}`] : []),
    ...(events.length === 0 ? ['pattern produced no discrete events — is everything muted or silent?'] : []),
  ],
  sounds: soundCounts,
};

if (opts.json) {
  result.events = events;
  console.log(JSON.stringify(result, null, 2));
} else {
  console.log(`✅ ${result.file}: evaluated OK — ${result.eventCount} events over ${opts.cycles} cycle(s)`);
  if (info.tempo) console.log(`   tempo: ${JSON.stringify(info.tempo)}`);
  if (info.sampleSources.length) console.log(`   sample sources: ${[...new Set(info.sampleSources)].join(', ')}`);
  if (Object.keys(voiceCounts).length) {
    console.log(`   voices: ${Object.entries(voiceCounts).map(([k, v]) => `${k}=${v}`).join(', ')}`);
  }
  for (const w of result.warnings) console.log(`   ⚠️  ${w}`);
  if (!opts.quiet && events.length) {
    console.log(`   sounds: ${Object.entries(soundCounts).map(([k, v]) => `${k}×${v}`).join(', ')}`);
    const shown = events.slice(0, 20);
    for (const e of shown) {
      const v = Object.entries(e.value)
        .filter(([k]) => typeof e.value[k] !== 'object')
        .map(([k, val]) => `${k}=${val}`)
        .join(' ');
      console.log(`   ${e.begin.toFixed(3)}–${e.end.toFixed(3)}  ${v}`);
    }
    if (events.length > shown.length) console.log(`   ... ${events.length - shown.length} more (use --json for all)`);
  }
}
process.exit(queryError ? 1 : 0);
