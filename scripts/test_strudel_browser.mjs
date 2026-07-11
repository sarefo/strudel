#!/usr/bin/env node
/**
 * Browser smoke test: load a .strudel file in strudel.cc, start playback,
 * and report whether audio actually runs — plus any console/page errors.
 *
 * For correctness checks (syntax, event timeline) use eval_strudel.mjs first;
 * this script only answers "does it make sound in the real player".
 *
 * Usage:
 *   node scripts/test_strudel_browser.mjs <file.strudel> [--headed] [--seconds N] [--screenshot] [--json]
 *
 *   --headed      show the browser window (default: headless)
 *   --seconds N   how long to let it play (default 4)
 *   --screenshot  save temp/screenshots/<name>.png
 *   --json        machine-readable output
 *
 * Exit code 0 = played with a running audio context and no errors, 1 otherwise.
 */
import { readFileSync, mkdirSync } from 'fs';
import { basename } from 'path';
import puppeteer from 'puppeteer';

const args = process.argv.slice(2);
const opts = { headed: false, seconds: 4, screenshot: false, json: false, file: null };
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === '--headed') opts.headed = true;
  else if (a === '--seconds') opts.seconds = parseFloat(args[++i]);
  else if (a === '--screenshot') opts.screenshot = true;
  else if (a === '--json') opts.json = true;
  else if (!a.startsWith('-')) opts.file = a;
}
if (!opts.file) {
  console.error('Usage: node scripts/test_strudel_browser.mjs <file.strudel> [--headed] [--seconds N] [--screenshot] [--json]');
  process.exit(1);
}

const content = readFileSync(opts.file, 'utf8');
const encoded = Buffer.from(content, 'utf8').toString('base64');
const url = `https://strudel.cc/#${encodeURIComponent(encoded)}`;
const name = basename(opts.file, '.strudel');

const result = {
  ok: false,
  file: basename(opts.file),
  consoleErrors: [],
  pageErrors: [],
  audio: { contexts: 0, running: 0, timeAdvanced: false },
};

const browser = await puppeteer.launch({
  headless: !opts.headed,
  args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required'],
});

try {
  const page = await browser.newPage();

  // listeners must be attached BEFORE navigation to catch load-time errors
  page.on('pageerror', (err) => result.pageErrors.push(String(err.message || err)));
  page.on('console', (msg) => {
    if (msg.type() === 'error') result.consoleErrors.push(msg.text());
  });

  // strudel.cc doesn't expose its AudioContext; wrap the constructor before
  // any page script runs so we can inspect the instances later
  await page.evaluateOnNewDocument(() => {
    window.__audioContexts = [];
    const Orig = window.AudioContext;
    window.AudioContext = class extends Orig {
      constructor(...a) {
        super(...a);
        window.__audioContexts.push(this);
      }
    };
  });

  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForSelector('.cm-content', { timeout: 30000 }); // editor ready
  await new Promise((r) => setTimeout(r, 3000)); // sample/module loading

  // ctrl+enter = evaluate & play (more reliable than hunting for the button)
  await page.keyboard.down('Control');
  await page.keyboard.press('Enter');
  await page.keyboard.up('Control');

  await new Promise((r) => setTimeout(r, 1500));
  const t0 = await page.evaluate(() =>
    (window.__audioContexts || []).map((c) => ({ state: c.state, time: c.currentTime }))
  );

  await new Promise((r) => setTimeout(r, opts.seconds * 1000));
  const t1 = await page.evaluate(() =>
    (window.__audioContexts || []).map((c) => ({ state: c.state, time: c.currentTime }))
  );

  result.audio.contexts = t1.length;
  result.audio.running = t1.filter((c) => c.state === 'running').length;
  result.audio.timeAdvanced = t1.some((c, i) => t0[i] && c.time > t0[i].time);

  if (opts.screenshot) {
    mkdirSync('temp/screenshots', { recursive: true });
    await page.screenshot({ path: `temp/screenshots/${name}.png`, fullPage: true });
    result.screenshot = `temp/screenshots/${name}.png`;
  }

  result.ok =
    result.audio.running > 0 &&
    result.audio.timeAdvanced &&
    result.pageErrors.length === 0 &&
    result.consoleErrors.length === 0;
} catch (err) {
  result.pageErrors.push(`test harness: ${String(err.message || err)}`);
} finally {
  await browser.close();
}

if (opts.json) {
  console.log(JSON.stringify(result, null, 2));
} else {
  console.log(`${result.ok ? '✅' : '❌'} ${result.file}`);
  console.log(`   audio contexts: ${result.audio.contexts} (${result.audio.running} running, time advanced: ${result.audio.timeAdvanced})`);
  for (const e of result.consoleErrors) console.log(`   console error: ${e}`);
  for (const e of result.pageErrors) console.log(`   page error: ${e}`);
  if (result.screenshot) console.log(`   screenshot: ${result.screenshot}`);
}
process.exit(result.ok ? 0 : 1);
