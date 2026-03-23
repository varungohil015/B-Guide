# FOLDER STRUCTURE

## Project root
```text
mac-command-bridge/
  README.md
  SPEC.md
  ARCHITECTURE.md
  NEXT STEPS.md
  FOLDER STRUCTURE.md
  REQUEST SCHEMA.md
  RUNNER DESIGN.md
  IMPLEMENTATION PLAN.md
  commands/
  results/
  logs/
```

## Runtime folders
### `commands/`
Incoming JSON request files written by Alfred.

### `results/`
JSON result files written by the local runner.

### `logs/`
Execution logs and error logs.

## Naming suggestion
Requests:
- `2026-03-21T20-55-00_cmd-001.json`

Results:
- `2026-03-21T20-55-03_cmd-001.result.json`

Logs:
- `runner.log`
