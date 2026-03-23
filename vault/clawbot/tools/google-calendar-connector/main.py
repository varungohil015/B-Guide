#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
BASE_DIR = Path(__file__).resolve().parent
CREDS_PATH = BASE_DIR / 'credentials.json'
TOKEN_PATH = BASE_DIR / 'token.json'
DEFAULT_CALENDAR = 'notfakeytch@gmail.com'
DEFAULT_TZ = '+05:30'


def get_service():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json(), encoding='utf-8')

    return build('calendar', 'v3', credentials=creds)


def list_calendars(service):
    result = service.calendarList().list().execute()
    items = result.get('items', [])
    for cal in items:
        print(f"{cal.get('summary')} :: {cal.get('id')}")


def print_events(events):
    if not events:
        print('No events found.')
        return
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        print(f"- {event.get('id')} :: {start} -> {end} :: {event.get('summary', '(no title)')}")


def upcoming(service, calendar_id: str, limit: int):
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=now,
        maxResults=limit,
        singleEvents=True,
        orderBy='startTime',
    ).execute()
    events = events_result.get('items', [])
    print_events(events)


def range_events(service, calendar_id: str, start_iso: str, end_iso: str, limit: int = 100):
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_iso,
        timeMax=end_iso,
        maxResults=limit,
        singleEvents=True,
        orderBy='startTime',
    ).execute()
    return events_result.get('items', [])


def create_event(service, calendar_id: str, title: str, start_iso: str, end_iso: str, description: str | None = None):
    body = {
        'summary': title,
        'start': {'dateTime': start_iso},
        'end': {'dateTime': end_iso},
    }
    if description:
        body['description'] = description
    event = service.events().insert(calendarId=calendar_id, body=body).execute()
    print(json.dumps({'id': event.get('id'), 'htmlLink': event.get('htmlLink')}, indent=2))


def delete_event(service, calendar_id: str, event_id: str):
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    print(json.dumps({'deleted': True, 'id': event_id}, indent=2))


def iso_for_local(date_str: str, time_str: str, tz: str):
    return f"{date_str}T{time_str}:00{tz}"


def today_bounds(day: str | None, tz: str):
    if day:
        target = dt.date.fromisoformat(day)
    else:
        target = dt.datetime.now().date()
    start = f"{target.isoformat()}T00:00:00{tz}"
    end = f"{target.isoformat()}T23:59:59{tz}"
    return start, end


def create_block(service, calendar_id: str, title: str, day: str, start_time: str, duration_min: int, tz: str, description: str | None = None):
    start_dt = dt.datetime.fromisoformat(f"{day}T{start_time}:00{tz}")
    end_dt = start_dt + dt.timedelta(minutes=duration_min)
    create_event(service, calendar_id, title, start_dt.isoformat(), end_dt.isoformat(), description)


def find_events(service, calendar_id: str, day: str, query: str, tz: str):
    start_iso, end_iso = today_bounds(day, tz)
    events = range_events(service, calendar_id, start_iso, end_iso)
    query_lower = query.lower()
    matched = [
        {
            'id': e.get('id'),
            'summary': e.get('summary'),
            'start': e.get('start', {}).get('dateTime', e.get('start', {}).get('date')),
            'end': e.get('end', {}).get('dateTime', e.get('end', {}).get('date')),
        }
        for e in events
        if query_lower in (e.get('summary', '').lower())
    ]
    print(json.dumps(matched, indent=2))


def upsert_block(service, calendar_id: str, title: str, day: str, start_time: str, duration_min: int, tz: str, description: str | None = None):
    start_iso, end_iso = today_bounds(day, tz)
    events = range_events(service, calendar_id, start_iso, end_iso)
    for e in events:
        if e.get('summary', '').strip().lower() == title.strip().lower():
            service.events().delete(calendarId=calendar_id, eventId=e['id']).execute()
    create_block(service, calendar_id, title, day, start_time, duration_min, tz, description)


def main():
    parser = argparse.ArgumentParser(description='Google Calendar connector for Clawbot')
    sub = parser.add_subparsers(dest='cmd', required=True)

    sub.add_parser('list-calendars')

    up = sub.add_parser('upcoming')
    up.add_argument('--calendar', default=DEFAULT_CALENDAR)
    up.add_argument('--limit', type=int, default=10)

    td = sub.add_parser('today')
    td.add_argument('--calendar', default=DEFAULT_CALENDAR)
    td.add_argument('--day', help='YYYY-MM-DD, defaults to today')
    td.add_argument('--tz', default=DEFAULT_TZ)

    ce = sub.add_parser('create-event')
    ce.add_argument('--calendar', default=DEFAULT_CALENDAR)
    ce.add_argument('--title', required=True)
    ce.add_argument('--start', required=True)
    ce.add_argument('--end', required=True)
    ce.add_argument('--description')

    cb = sub.add_parser('create-block')
    cb.add_argument('--calendar', default=DEFAULT_CALENDAR)
    cb.add_argument('--title', required=True)
    cb.add_argument('--day', required=True)
    cb.add_argument('--start-time', required=True)
    cb.add_argument('--duration', type=int, required=True)
    cb.add_argument('--tz', default=DEFAULT_TZ)
    cb.add_argument('--description')

    de = sub.add_parser('delete-event')
    de.add_argument('--calendar', default=DEFAULT_CALENDAR)
    de.add_argument('--event-id', required=True)

    fe = sub.add_parser('find-events')
    fe.add_argument('--calendar', default=DEFAULT_CALENDAR)
    fe.add_argument('--day', required=True)
    fe.add_argument('--query', required=True)
    fe.add_argument('--tz', default=DEFAULT_TZ)

    ub = sub.add_parser('upsert-block')
    ub.add_argument('--calendar', default=DEFAULT_CALENDAR)
    ub.add_argument('--title', required=True)
    ub.add_argument('--day', required=True)
    ub.add_argument('--start-time', required=True)
    ub.add_argument('--duration', type=int, required=True)
    ub.add_argument('--tz', default=DEFAULT_TZ)
    ub.add_argument('--description')

    args = parser.parse_args()
    service = get_service()

    if args.cmd == 'list-calendars':
        list_calendars(service)
    elif args.cmd == 'upcoming':
        upcoming(service, args.calendar, args.limit)
    elif args.cmd == 'today':
        start_iso, end_iso = today_bounds(args.day, args.tz)
        print_events(range_events(service, args.calendar, start_iso, end_iso))
    elif args.cmd == 'create-event':
        create_event(service, args.calendar, args.title, args.start, args.end, args.description)
    elif args.cmd == 'create-block':
        create_block(service, args.calendar, args.title, args.day, args.start_time, args.duration, args.tz, args.description)
    elif args.cmd == 'delete-event':
        delete_event(service, args.calendar, args.event_id)
    elif args.cmd == 'find-events':
        find_events(service, args.calendar, args.day, args.query, args.tz)
    elif args.cmd == 'upsert-block':
        upsert_block(service, args.calendar, args.title, args.day, args.start_time, args.duration, args.tz, args.description)


if __name__ == '__main__':
    main()
