# LAUNCH

## One-time setup
```bash
cd "/Users/ziscol/Obsidian/Private/clawbot/tools/google-calendar-connector"
chmod +x setup.sh run.sh
./setup.sh
```

## List calendars
```bash
./run.sh list-calendars
```

## Show today's events
```bash
./run.sh today
```

## Create a simple scheduled block
```bash
./run.sh create-block \
  --title "Founder Flow" \
  --day "2026-03-22" \
  --start-time "09:00" \
  --duration 240 \
  --description "Deep work block"
```

## Find events on a day by title match
```bash
./run.sh find-events --day "2026-03-22" --query "Founder Flow"
```

## Delete event by id
```bash
./run.sh delete-event --event-id "EVENT_ID"
```

## Upsert block (delete same-title block on that day, then recreate)
```bash
./run.sh upsert-block \
  --title "Founder Flow" \
  --day "2026-03-22" \
  --start-time "09:00" \
  --duration 240 \
  --description "Deep work block"
```
