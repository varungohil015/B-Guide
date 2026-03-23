# IMPLEMENTATION PLAN

## Phase 1 — calendar bridge only
### Goal
Remove manual copy-paste for calendar actions.

### Tasks
1. Create runtime folders:
   - `commands/`
   - `results/`
   - `logs/`
2. Build runner script.
3. Add request validation.
4. Add allowlisted calendar action handlers.
5. Write result and error JSON files.
6. Test end-to-end with one create block request.

## Phase 2 — cleaner orchestration
1. Add archive for processed commands.
2. Add duplicate request handling.
3. Add command status tracking.
4. Add better logging.

## Phase 3 — expand actions
1. transcript import commands
2. note creation/update commands
3. future tool runners

## Success condition for MVP
Alfred can create a request file for `calendar.create_block`, the Mac runner processes it automatically, and a result file confirms the event was created.
