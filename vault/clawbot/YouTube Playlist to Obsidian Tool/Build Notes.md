# Build Notes

## Main implementation decision
The Python version using `yt-dlp` is the recommended MVP.

Reason:
- more practical for real-world YouTube metadata/caption handling
- easier to export playlist entries reliably
- better fit for a quick internal CLI tool

## Current Python MVP capabilities
- accepts playlist URL
- accepts output folder
- fetches playlist entries
- fetches video-level subtitle/caption metadata
- prefers normal subtitles, then automatic captions
- supports `json3` and `vtt` parsing
- writes markdown transcript note
- writes JSON source file
- can also write clean no-timestamp markdown version
- can generate `index.md`
- always writes `import-summary.json`
- skips missing transcript videos gracefully

## Current Python dependency
- `yt-dlp>=2025.3.0`

## Current environment issue encountered
The OpenClaw Linux environment had Python but lacked a complete `pip` / `ensurepip` setup for creating and validating a local venv there.
This is an environment issue, not a product design issue.

## Node prototype status
There is an early Node prototype using `youtubei.js` and a caption approach.
It is not the recommended main path right now.
Keep only as reference or backup.

## Developer recommendation
Take the Python version, run it on a normal machine with Python + pip working, test it on a real playlist, then improve from there.
