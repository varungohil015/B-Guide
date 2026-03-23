# Handoff for Developer

## What this project is
A free-first internal CLI tool for turning a YouTube playlist into Obsidian transcript notes using YouTube's own transcript/caption tracks.

## Recommended path
Use the Python MVP as the base implementation.

## Immediate tasks
1. Set up the Python environment locally
2. Install dependencies from `requirements.txt`
3. Run the tool against a real playlist
4. Fix any edge cases discovered during live testing
5. Improve setup and UX as needed

## Things to verify in testing
- playlist extraction works correctly
- creator-uploaded subtitles are preferred when available
- auto captions are used as fallback
- `json3` parsing works
- `vtt` parsing works
- markdown files are readable in Obsidian
- clean transcript output is useful
- skipped videos are reported cleanly
- `index.md` and `import-summary.json` are accurate

## Suggested nice-to-have improvements
- better filename handling for weird titles
- support custom vault folder presets
- add a dry-run mode
- add better logging
- maybe package as a simple installable CLI

## Suggested test command
```bash
python main.py \
  --playlist "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID" \
  --output "$HOME/obsidian-transcripts" \
  --clean \
  --index \
  --limit 5
```

## Core requirement
Do not overbuild it.
Get playlist in -> transcripts out -> Obsidian-ready files saved.
That is the real MVP.
