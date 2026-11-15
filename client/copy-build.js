import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Resolve paths from this script's folder, so the copy works from any working directory.
const clientDir = path.dirname(fileURLToPath(import.meta.url));
const srcDir = path.join(clientDir, 'dist');
const destDir = path.join(clientDir, '..', 'backend', 'src', 'static');

if (!fs.existsSync(srcDir)) {
    console.error(`Build output directory not found: ${srcDir}`);
    process.exit(1);
}

// Remove the previous copy first. Vite file names contain content hashes, so
// files from earlier builds would otherwise pile up in static/.
fs.rmSync(destDir, { recursive: true, force: true });
fs.cpSync(srcDir, destDir, { recursive: true });
console.log(`Copied build files from ${srcDir} to ${destDir}`);
