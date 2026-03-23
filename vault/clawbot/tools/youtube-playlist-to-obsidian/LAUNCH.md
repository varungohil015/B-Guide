# LAUNCH

## On your Mac
Open Terminal and go to the project folder inside your synced Obsidian vault.

Example shape:
```bash
cd "/Users/ziscol/Obsidian/Private/clawbot/tools/youtube-playlist-to-obsidian"
```

If your synced vault lives somewhere else, use that path instead.

## First run
```bash
chmod +x run.sh
./run.sh \
  --playlist "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID" \
  --output "/Users/ziscol/Obsidian/Private/YouTube Playlist Transcripts" \
  --clean \
  --index \
  --limit 5
```

## What it does
- creates `.venv` if needed
- installs/upgrades Python dependencies
- runs `main.py` with your arguments

## Full run after test
Remove `--limit 5` when the small test works.

## If it breaks
Send the terminal output back to Alfred for debugging.
