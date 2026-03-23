# YouTube Playlist to Obsidian Tool

This folder packages the current MVP idea and implementation for a free YouTube playlist transcript ingester that saves output into Obsidian.

## Purpose
Turn a YouTube playlist into:
- markdown transcript notes
- JSON transcript source files
- optional clean no-timestamp transcript notes
- an import index and summary

## Why it matters
This helps build a private business intelligence system from strong YouTube channels and playlists, so Alfred can use those transcripts later for better strategy, rules, and decision support.

## Current status
- MVP designed
- Python implementation drafted
- early Node prototype also exists
- not fully validated end-to-end in the OpenClaw Linux environment because package tooling was limited there
- should be straightforward for a friend/dev to complete from this handoff

## Folder contents
- `README.md` — overview
- `Product Spec.md` — what the tool should do
- `Build Notes.md` — implementation notes and decisions
- `Handoff for Developer.md` — what your friend should do next
- `Python MVP/` — current Python implementation files
- `Node Prototype/` — early Node attempt

## Recommended direction
Use the Python `yt-dlp` approach as the main path unless your friend has a strong reason to rewrite it.
It is the more practical MVP.
