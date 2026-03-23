# RUNNER DESIGN

## Goal
A local runner process on the Mac watches `commands/` and executes only approved actions.

## Core behavior
1. Watch `commands/` for new `.json` files.
2. Parse request.
3. Validate schema.
4. Validate action against allowlist.
5. Dispatch to a local wrapper.
6. Write result JSON to `results/`.
7. Log success/failure to `logs/runner.log`.
8. Move processed requests to an archive folder later if needed.

## Allowlist (phase 1)
- `calendar.list_calendars`
- `calendar.today`
- `calendar.upcoming`
- `calendar.create_event`
- `calendar.create_block`

## Dispatch design
The runner should not execute arbitrary shell.
It should map each action to a known Python function or safe command wrapper.

Example mapping:
- `calendar.create_block` -> call Google calendar connector locally
- `calendar.today` -> call connector and return event list

## Safety rules
- reject unknown actions
- reject malformed JSON
- log all requests
- do not allow arbitrary path arguments outside approved scope
- do not allow raw shell strings in requests

## MVP implementation idea
Python runner with polling loop every few seconds is enough.
No need for a fancy daemon first.
