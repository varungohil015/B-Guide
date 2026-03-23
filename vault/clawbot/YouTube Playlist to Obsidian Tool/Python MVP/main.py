#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import re
import time
import urllib.request
from html import unescape
from pathlib import Path

from yt_dlp import YoutubeDL


def slugify(value: str) -> str:
    value = (value or '').lower()
    value = re.sub(r'[^a-z0-9]+', '-', value)
    value = re.sub(r'-{2,}', '-', value).strip('-')
    return value[:120] or 'untitled'


def format_timestamp(seconds) -> str:
    total = max(0, int(float(seconds or 0)))
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def parse_json3_subtitle(data: str):
    payload = json.loads(data)
    events = payload.get('events', [])
    lines = []
    for event in events:
        if 'segs' not in event:
            continue
        text = ''.join(seg.get('utf8', '') for seg in event.get('segs', []))
        text = unescape(text).replace('\n', ' ').strip()
        if not text:
            continue
        lines.append({
            'start': (event.get('tStartMs') or 0) / 1000,
            'dur': (event.get('dDurationMs') or 0) / 1000,
            'text': re.sub(r'\s+', ' ', text),
        })
    return lines


def parse_vtt_subtitle(data: str):
    lines = []
    blocks = re.split(r'\n\s*\n', data.replace('\r', ''))
    for block in blocks:
        if '-->' not in block:
            continue
        chunk_lines = [
            line for line in block.split('\n')
            if line and '-->' not in line and not line.isdigit() and not line.startswith('WEBVTT')
        ]
        text = ' '.join(chunk_lines).strip()
        text = re.sub(r'<[^>]+>', '', text)
        text = unescape(re.sub(r'\s+', ' ', text))
        if not text:
            continue
        m = re.search(r'(\d{2}:)?\d{2}:\d{2}\.\d{3}', block)
        start = 0
        if m:
            parts = m.group(0).split(':')
            if len(parts) == 3:
                start = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
            else:
                start = int(parts[0]) * 60 + float(parts[1])
        lines.append({'start': start, 'dur': 0, 'text': text})
    return lines


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode('utf-8', errors='replace')


def pick_subtitle_track(info: dict, lang: str):
    subtitles = info.get('subtitles') or {}
    auto = info.get('automatic_captions') or {}
    wanted = [lang]
    if lang != 'en':
        wanted.append('en')

    for source_name, source in [('subtitles', subtitles), ('automatic_captions', auto)]:
        for code in wanted:
            tracks = source.get(code) or []
            if not tracks:
                continue
            preferred = sorted(
                tracks,
                key=lambda t: (0 if t.get('ext') == 'json3' else 1, 0 if t.get('ext') == 'vtt' else 1)
            )
            for track in preferred:
                if track.get('url'):
                    return source_name, code, track
    return None, None, None


def build_markdown(video: dict, transcript: list, exported_at: str, json_name: str) -> str:
    body = '\n'.join(f"**{format_timestamp(item['start'])}** {item['text']}" for item in transcript) or '_No transcript text found._'
    return f"# {video['title']}\n\n## Metadata\n- Video ID: `{video['id']}`\n- YouTube: {video['url']}\n- Channel: {video.get('channel') or 'Unknown'}\n- Playlist: {video.get('playlist_title') or 'Unknown'}\n- Exported: {exported_at}\n- Source JSON: `{json_name}`\n\n## Transcript\n\n{body}\n"


def build_clean_markdown(video: dict, transcript: list, exported_at: str) -> str:
    text = re.sub(r'\s+', ' ', ' '.join(item['text'] for item in transcript)).strip() or '_No transcript text found._'
    return f"# {video['title']}\n\n## Metadata\n- Video ID: `{video['id']}`\n- YouTube: {video['url']}\n- Channel: {video.get('channel') or 'Unknown'}\n- Playlist: {video.get('playlist_title') or 'Unknown'}\n- Exported: {exported_at}\n\n## Transcript\n\n{text}\n"


def fetch_playlist_entries(url: str, limit: int | None):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': 'in_playlist',
        'playlistend': limit,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    entries = info.get('entries') or []
    playlist_title = info.get('title')
    results = []
    for idx, entry in enumerate(entries, start=1):
        video_id = entry.get('id')
        if not video_id:
            continue
        results.append({
            'id': video_id,
            'title': entry.get('title') or f'Video {idx}',
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'channel': entry.get('channel') or entry.get('uploader'),
            'playlist_title': playlist_title,
        })
    return results


def fetch_video_info(url: str):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'writesubtitles': False,
    }
    with YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)


def write_text(path: Path, content: str, overwrite: bool):
    if path.exists() and not overwrite:
        return False
    path.write_text(content, encoding='utf-8')
    return True


def main():
    parser = argparse.ArgumentParser(description='Export YouTube playlist transcripts into Obsidian-friendly markdown files.')
    parser.add_argument('--playlist', required=True, help='YouTube playlist URL')
    parser.add_argument('--output', required=True, help='Output folder')
    parser.add_argument('--clean', action='store_true', help='Also create no-timestamp versions in _clean/')
    parser.add_argument('--index', action='store_true', help='Create index.md overview')
    parser.add_argument('--lang', default='en', help='Preferred subtitle language (default: en)')
    parser.add_argument('--delay-ms', type=int, default=750, help='Delay between videos')
    parser.add_argument('--limit', type=int, help='Only process first N videos')
    parser.add_argument('--prefix-date', action='store_true', help='Prefix filenames with YYYY-MM-DD')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')
    args = parser.parse_args()

    output_dir = Path(args.output).expanduser().resolve()
    clean_dir = output_dir / '_clean'
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.clean:
        clean_dir.mkdir(parents=True, exist_ok=True)

    exported_at = dt.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
    export_date = exported_at[:10]

    videos = fetch_playlist_entries(args.playlist, args.limit)
    if not videos:
        raise SystemExit('No videos found in playlist.')

    results = []
    for i, video in enumerate(videos, start=1):
        try:
            info = fetch_video_info(video['url'])
            source_name, lang_code, track = pick_subtitle_track(info, args.lang)
            if not track:
                raise RuntimeError('No transcript/caption track available')
            subtitle_text = fetch_text(track['url'])
            ext = track.get('ext') or 'vtt'
            transcript = parse_json3_subtitle(subtitle_text) if ext == 'json3' else parse_vtt_subtitle(subtitle_text)
            transcript = [item for item in transcript if item.get('text')]
            if not transcript:
                raise RuntimeError('Transcript track was empty')

            base = f"{export_date}-" if args.prefix_date else ''
            base += f"{slugify(video['title'])}-{video['id']}"
            md_name = f'{base}.md'
            json_name = f'{base}.json'

            payload = {
                'metadata': {
                    'videoId': video['id'],
                    'videoTitle': video['title'],
                    'videoUrl': video['url'],
                    'channel': video.get('channel'),
                    'playlistTitle': video.get('playlist_title'),
                    'exportDate': exported_at,
                    'subtitleSource': source_name,
                    'subtitleLanguage': lang_code,
                    'subtitleFormat': ext,
                },
                'transcript': [
                    {
                        'start': item['start'],
                        'dur': item.get('dur', 0),
                        'time': format_timestamp(item['start']),
                        'text': item['text'],
                    }
                    for item in transcript
                ],
            }

            md_written = write_text(output_dir / md_name, build_markdown(video, transcript, exported_at, json_name), args.overwrite)
            json_written = write_text(output_dir / json_name, json.dumps(payload, indent=2, ensure_ascii=False), args.overwrite)
            if args.clean:
                write_text(clean_dir / md_name, build_clean_markdown(video, transcript, exported_at), args.overwrite)

            results.append({**video, 'status': 'ok', 'language': lang_code, 'source': source_name, 'format': ext, 'transcriptLines': len(transcript), 'written': {'markdown': md_written, 'json': json_written}})
            print(f"[{i}/{len(videos)}] OK  {video['title']}")
        except Exception as exc:
            results.append({**video, 'status': 'missing-transcript', 'error': str(exc)})
            print(f"[{i}/{len(videos)}] SKIP {video['title']} :: {exc}")
        if i < len(videos) and args.delay_ms > 0:
            time.sleep(args.delay_ms / 1000)

    if args.index:
        success = sum(1 for item in results if item['status'] == 'ok')
        missing = len(results) - success
        lines = [
            '# Playlist transcript import',
            '',
            '## Run metadata',
            f'- Playlist URL: {args.playlist}',
            f'- Exported: {exported_at}',
            f'- Output folder: {output_dir}',
            f'- Requested language: {args.lang}',
            f'- Videos discovered: {len(videos)}',
            f'- Notes created: {success}',
            f'- Missing transcript: {missing}',
            '',
            '## Results',
            '',
        ]
        for idx, item in enumerate(results, start=1):
            if item['status'] == 'ok':
                lines.append(f"{idx}. {item['title']} — {item['transcriptLines']} lines ({item['language']}, {item['source']})")
            else:
                lines.append(f"{idx}. {item['title']} — _missing transcript_ ({item['error']})")
        (output_dir / 'index.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    summary = {
        'playlistUrl': args.playlist,
        'outputDir': str(output_dir),
        'exportedAt': exported_at,
        'totalVideos': len(videos),
        'successCount': sum(1 for item in results if item['status'] == 'ok'),
        'missingCount': sum(1 for item in results if item['status'] != 'ok'),
        'results': results,
    }
    (output_dir / 'import-summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Done. {summary['successCount']}/{summary['totalVideos']} videos exported.")


if __name__ == '__main__':
    main()
