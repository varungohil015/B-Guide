# Product Spec

## Goal
Build a free-first internal tool that accepts a YouTube playlist URL and creates Obsidian-friendly transcript notes using YouTube's built-in captions/transcripts whenever available.

## Input
- YouTube playlist URL
- output folder path
- optional language code
- optional clean transcript generation
- optional index generation
- optional video limit

## Core output
For each successful video:
- one markdown note with timestamps
- one JSON transcript source file
- one clean markdown note without timestamps (optional)

For each run:
- `index.md` (optional)
- `import-summary.json`

## Desired folder structure
```text
Target Folder/
  index.md
  import-summary.json
  video-title-VIDEOID.md
  video-title-VIDEOID.json
  _clean/
    video-title-VIDEOID.md
```

## Logic
1. Read playlist URL
2. Fetch video list from playlist
3. For each video:
   - fetch metadata
   - try normal subtitles first
   - if not available, try automatic captions
   - if transcript exists, parse and save it
   - if transcript does not exist, skip gracefully
4. Generate summary and optional index

## Constraints
- free-first
- use YouTube-provided transcript/captions when possible
- do not require paid APIs for MVP
- output should fit naturally into Obsidian
- failures on one video should not kill the whole run

## Future additions
- summarize transcripts
- extract principles
- extract action items
- tag by topic or creator
- batch multiple playlists
- build channel-level playbooks from imported transcripts
