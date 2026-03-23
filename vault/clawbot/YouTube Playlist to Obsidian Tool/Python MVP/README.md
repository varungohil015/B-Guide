# Python MVP

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

## Usage
```bash
python main.py \
  --playlist "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID" \
  --output "$HOME/obsidian-transcripts" \
  --clean \
  --index \
  --limit 5
```

## Notes
- preferred MVP path
- free-first using YouTube captions/transcripts
- skips videos without accessible transcripts
