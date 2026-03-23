# LAUNCH

## Start the runner on your Mac
```bash
cd "/Users/ziscol/Obsidian/Private/clawbot/tools/mac-command-bridge"
chmod +x run_runner.sh
./run_runner.sh
```

The runner will:
- watch `commands/`
- write results to `results/`
- log activity to `logs/runner.log`
- move processed requests into `processed/`

## First test command
Create a JSON file in `commands/` like this:

```json
{
  "id": "cmd-001",
  "created_at": "2026-03-21T20:55:00Z",
  "action": "calendar.create_block",
  "args": {
    "title": "Founder Flow",
    "day": "2026-03-22",
    "start_time": "09:00",
    "duration": 240,
    "description": "Deep work block"
  }
}
```

Then wait a few seconds and inspect:
- `results/`
- `logs/runner.log`
- `processed/`
