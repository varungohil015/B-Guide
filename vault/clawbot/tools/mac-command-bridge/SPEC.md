# SPEC

## Goal
Build a safe execution bridge so Alfred can request local actions on the user's Mac without requiring the user to manually paste commands every time.

## Recommended MVP approach
Use a watched command folder runner.

## Why this approach
- simpler than a full API service
- safer than unrestricted SSH shell access
- easy to audit
- works well with mounted/synced folders
- easy to extend later

## How it works
1. Alfred writes a command request file into a watched folder.
2. A small local runner on the Mac watches that folder.
3. The runner validates the request against an allowlist.
4. If valid, it executes the action.
5. It writes a result file back into a results folder.

## Initial command types
- `calendar.create_block`
- `calendar.today`
- `calendar.upcoming`
- `calendar.create_event`
- `tool.youtube_playlist_import`

## Request format
Simple JSON file.

Example:
```json
{
  "id": "cmd-001",
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

## Result format
```json
{
  "id": "cmd-001",
  "status": "ok",
  "result": {
    "event_id": "abc123"
  }
}
```

## Safety rules
- allowlist only
- no arbitrary shell execution
- scoped working directories only
- log every command
- optionally require approval for risky command classes later

## Phase 1
- watched folder runner
- calendar actions only
- result logging

## Phase 2
- transcript/tool execution
- better scheduling workflows
- retries/error handling

## Phase 3
- optional local API
- richer orchestration
