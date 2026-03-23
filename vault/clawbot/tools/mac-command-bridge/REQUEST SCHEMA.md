# REQUEST SCHEMA

## Request JSON
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

## Result JSON
```json
{
  "id": "cmd-001",
  "completed_at": "2026-03-21T20:55:03Z",
  "status": "ok",
  "action": "calendar.create_block",
  "result": {
    "event_id": "abc123",
    "html_link": "https://calendar.google.com/..."
  }
}
```

## Error result
```json
{
  "id": "cmd-001",
  "completed_at": "2026-03-21T20:55:03Z",
  "status": "error",
  "action": "calendar.create_block",
  "error": "Missing required field: start_time"
}
```

## Required request fields
- `id`
- `created_at`
- `action`
- `args`
