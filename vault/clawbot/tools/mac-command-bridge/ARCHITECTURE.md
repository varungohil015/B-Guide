# ARCHITECTURE

## Recommended MVP
Watched command folder runner.

## Folders
- `commands/` — incoming command JSON files
- `results/` — result JSON files
- `logs/` — execution logs

## Local components on Mac
- runner script/process
- allowlist of actions
- wrappers around real tools (calendar connector, transcript importer, etc.)

## Why this beats current setup
Current setup requires manual terminal paste every time.
This bridge turns Alfred into an operator instead of just a planner.

## Core design rule
Alfred should request actions, not raw shell.
The Mac runner decides whether the request is allowed and how to execute it.
