#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import { Innertube } from 'youtubei.js';

function printHelp() {
  console.log(`yt-playlist-obsidian

Export YouTube playlist transcripts into Obsidian-friendly markdown files.

Usage:
  yt-playlist-obsidian --playlist <url> --output <folder> [options]
  node src/cli.js --playlist <url> --output <folder> [options]
`);
}

// Prototype only. Full implementation was not completed here.
printHelp();
