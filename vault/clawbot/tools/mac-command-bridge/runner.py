#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
COMMANDS_DIR = BASE_DIR / 'commands'
RESULTS_DIR = BASE_DIR / 'results'
LOGS_DIR = BASE_DIR / 'logs'
PROCESSED_DIR = BASE_DIR / 'processed'
LOG_FILE = LOGS_DIR / 'runner.log'
CALENDAR_DIR = Path('/Users/ziscol/Obsidian/Private/clawbot/tools/google-calendar-connector')
CALENDAR_RUNNER = CALENDAR_DIR / 'run.sh'
POLL_SECONDS = 3

ALLOWED_ACTIONS = {
    'calendar.list_calendars',
    'calendar.today',
    'calendar.upcoming',
    'calendar.create_event',
    'calendar.create_block',
    'calendar.delete_event',
    'calendar.find_events',
    'calendar.upsert_block',
}


@dataclass
class CommandRequest:
    id: str
    created_at: str
    action: str
    args: dict[str, Any]
    path: Path


def ensure_dirs():
    for p in [COMMANDS_DIR, RESULTS_DIR, LOGS_DIR, PROCESSED_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def log(message: str):
    line = f"[{now_iso()}] {message}\n"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open('a', encoding='utf-8') as f:
        f.write(line)
    print(line, end='')


def load_request(path: Path) -> CommandRequest:
    raw = json.loads(path.read_text(encoding='utf-8'))
    for field in ['id', 'created_at', 'action', 'args']:
        if field not in raw:
            raise ValueError(f'Missing required field: {field}')
    if raw['action'] not in ALLOWED_ACTIONS:
        raise ValueError(f'Action not allowed: {raw["action"]}')
    if not isinstance(raw['args'], dict):
        raise ValueError('args must be an object')
    return CommandRequest(str(raw['id']), str(raw['created_at']), str(raw['action']), raw['args'], path)


def result_path(cmd_id: str) -> Path:
    safe = cmd_id.replace('/', '-').replace('..', '-')
    return RESULTS_DIR / f'{safe}.result.json'


def write_result(cmd: CommandRequest, status: str, result: dict[str, Any] | None = None, error: str | None = None):
    payload = {'id': cmd.id, 'completed_at': now_iso(), 'status': status, 'action': cmd.action}
    if result is not None:
        payload['result'] = result
    if error is not None:
        payload['error'] = error
    result_path(cmd.id).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')


def parse_json_maybe(text: str) -> Any:
    text = text.strip()
    if not text:
        return {'message': ''}
    try:
        return json.loads(text)
    except Exception:
        return {'raw': text}


def run_calendar(args: list[str]) -> dict[str, Any]:
    if not CALENDAR_RUNNER.exists():
        raise RuntimeError(f'Calendar runner not found: {CALENDAR_RUNNER}')
    proc = subprocess.run(['bash', str(CALENDAR_RUNNER), *args], cwd=str(CALENDAR_DIR), capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f'calendar command failed ({proc.returncode})')
    return {'output': parse_json_maybe(proc.stdout), 'stderr': proc.stderr.strip(), 'returncode': proc.returncode}


def dispatch(cmd: CommandRequest) -> dict[str, Any]:
    a = cmd.action
    x = cmd.args

    if a == 'calendar.list_calendars':
        return run_calendar(['list-calendars'])
    if a == 'calendar.today':
        cli = ['today']
        if x.get('calendar'): cli += ['--calendar', str(x['calendar'])]
        if x.get('day'): cli += ['--day', str(x['day'])]
        if x.get('tz'): cli += ['--tz', str(x['tz'])]
        return run_calendar(cli)
    if a == 'calendar.upcoming':
        cli = ['upcoming']
        if x.get('calendar'): cli += ['--calendar', str(x['calendar'])]
        if x.get('limit'): cli += ['--limit', str(x['limit'])]
        return run_calendar(cli)
    if a == 'calendar.create_event':
        for field in ['title', 'start', 'end']:
            if field not in x: raise ValueError(f'Missing required arg: {field}')
        cli = ['create-event', '--title', str(x['title']), '--start', str(x['start']), '--end', str(x['end'])]
        if x.get('calendar'): cli += ['--calendar', str(x['calendar'])]
        if x.get('description'): cli += ['--description', str(x['description'])]
        return run_calendar(cli)
    if a == 'calendar.create_block':
        for field in ['title', 'day', 'start_time', 'duration']:
            if field not in x: raise ValueError(f'Missing required arg: {field}')
        cli = ['create-block', '--title', str(x['title']), '--day', str(x['day']), '--start-time', str(x['start_time']), '--duration', str(x['duration'])]
        if x.get('calendar'): cli += ['--calendar', str(x['calendar'])]
        if x.get('tz'): cli += ['--tz', str(x['tz'])]
        if x.get('description'): cli += ['--description', str(x['description'])]
        return run_calendar(cli)
    if a == 'calendar.delete_event':
        if 'event_id' not in x: raise ValueError('Missing required arg: event_id')
        cli = ['delete-event', '--event-id', str(x['event_id'])]
        if x.get('calendar'): cli += ['--calendar', str(x['calendar'])]
        return run_calendar(cli)
    if a == 'calendar.find_events':
        for field in ['day', 'query']:
            if field not in x: raise ValueError(f'Missing required arg: {field}')
        cli = ['find-events', '--day', str(x['day']), '--query', str(x['query'])]
        if x.get('calendar'): cli += ['--calendar', str(x['calendar'])]
        if x.get('tz'): cli += ['--tz', str(x['tz'])]
        return run_calendar(cli)
    if a == 'calendar.upsert_block':
        for field in ['title', 'day', 'start_time', 'duration']:
            if field not in x: raise ValueError(f'Missing required arg: {field}')
        cli = ['upsert-block', '--title', str(x['title']), '--day', str(x['day']), '--start-time', str(x['start_time']), '--duration', str(x['duration'])]
        if x.get('calendar'): cli += ['--calendar', str(x['calendar'])]
        if x.get('tz'): cli += ['--tz', str(x['tz'])]
        if x.get('description'): cli += ['--description', str(x['description'])]
        return run_calendar(cli)
    raise ValueError(f'No dispatcher for action: {a}')


def mark_processed(path: Path):
    shutil.move(str(path), str(PROCESSED_DIR / path.name))


def process_one(path: Path):
    log(f'Processing {path.name}')
    cmd = load_request(path)
    try:
        result = dispatch(cmd)
        write_result(cmd, 'ok', result=result)
        log(f'OK {cmd.id} {cmd.action}')
    except Exception as e:
        write_result(cmd, 'error', error=str(e))
        log(f'ERROR {cmd.id} {cmd.action} :: {e}')
    finally:
        mark_processed(path)


def run_loop():
    ensure_dirs()
    log('Runner started')
    while True:
        for path in sorted(COMMANDS_DIR.glob('*.json')):
            process_one(path)
        time.sleep(POLL_SECONDS)


if __name__ == '__main__':
    run_loop()
