// @kabelsalat/web (a dependency of @strudel/core) has no "exports" field, so
// Node resolves its "main" (an IIFE browser build) instead of the ESM build
// and the SalatRepl import in @strudel/core fails. Point Node at the .mjs.
// Runs automatically via the "postinstall" hook in package.json.
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const pkgPath = join(
  dirname(fileURLToPath(import.meta.url)),
  '..', 'node_modules', '@kabelsalat', 'web', 'package.json'
);

let pkg;
try {
  pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
} catch {
  console.log('patch_kabelsalat: @kabelsalat/web not installed, nothing to patch');
  process.exit(0);
}

if (pkg.exports?.['.']?.import === './dist/index.mjs') {
  console.log('patch_kabelsalat: already patched');
  process.exit(0);
}

pkg.exports = {
  '.': {
    import: './dist/index.mjs',
    default: './dist/index.js',
  },
};
writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + '\n');
console.log('patch_kabelsalat: patched @kabelsalat/web exports to use ESM build');
