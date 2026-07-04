---
name: youtube-local-transcribe
description: Caption-first local video archiving, transcription, summarization, report generation, and dashboard workflow for YouTube, youtu.be, Bilibili, b23.tv, BV, av, ep, ss, and other yt-dlp supported video URLs. Use when the user sends a bare video link or asks to download subtitles, transcribe locally, summarize a video, create notes, generate an HTML report, open a local browser report, inspect past video reports, or serve a local report dashboard.
---

# YouTube Local Transcribe

Use this workflow for bare video URLs and explicit video transcription, summary, archive, or report requests. Prefer downloadable subtitles first; use local Whisper only when captions are missing, unsuitable, or the user forces transcription.

## Setup Check

If `ytlt` is not installed, ask the user to install the public package or run from the repository root:

```bash
python -m pip install -e .
ytlt probe
ytlt setup --dry-run
ytlt setup --execute
```

`ytlt setup --execute` detects the local hardware, installs the matching backend plus `imageio-ffmpeg`, verifies ffmpeg, downloads the recommended model into `<workspace>/models`, and writes `<workspace>/config.json` with the resolved ffmpeg path. When deciding what model or backend to install, read `references/model-selection.md`.

## Process One Video

Run:

```bash
ytlt process "VIDEO_URL"
```

Useful options:

```bash
ytlt process "VIDEO_URL" --language zh
ytlt process "VIDEO_URL" --cookies-from-browser chrome
ytlt process "VIDEO_URL" --force-transcribe
ytlt process "VIDEO_URL" --open
```

The processor creates a per-video folder under `<workspace>/processed/`, writes `metadata.json`, `transcript.txt`, and `report.html`, and updates `index.json` plus `dashboard.html`.
When local Whisper is needed, it uses the configured model path from `<workspace>/config.json` unless `--model` is provided.

The JSON output includes the folder and report paths. Read `metadata.json` and `transcript.txt` before summarizing.

## Write The Summary

Write a grounded Markdown summary to `<video-folder>/summary.md`. Use the user's language unless the user requests another language.

Use this structure:

```text
Summary

One-paragraph answer-first summary.

Key Points

- [mm:ss-mm:ss] Point 1
- [mm:ss-mm:ss] Point 2
- [mm:ss-mm:ss] Point 3

Notes

- Caveats about subtitle quality, audio quality, uncertain terms, or incomplete transcript.
```

For video reports, key point bullets must start with a bracketed timestamp or time range such as `[01:24-02:44]`, using the transcript's actual timing. Use `[hh:mm:ss-hh:mm:ss]` for videos longer than one hour. The report renderer converts bracketed timestamps into clickable source-video links that seek to the start time, so keep the timestamp at the beginning of each key point.

Finalize:

```bash
ytlt finalize "<video-folder>"
```

Finalization re-renders `report.html`, deletes any retained downloaded `video.*` media file, and refreshes the dashboard index.

## Dashboard

Open or serve previous reports:

```bash
ytlt rebuild-index
ytlt serve --open
```

`ytlt serve` binds to `127.0.0.1` by default and opens a local dashboard of past reports. Do not expose the server publicly unless the user explicitly asks.

## Output Contract

Each processed folder should contain:

- `metadata.json`: source URL, title, channel, platform, publish time, duration, processing time, and `transcript_source`
- `transcript.txt`: subtitle-derived or local Whisper transcript
- `summary.md`: Codex-written summary, after the summary step
- `report.html`: browser-readable report

`transcript_source` is one of:

- `manual_subtitle`
- `auto_subtitle`
- `local_whisper`

Do not rely on generated summaries without reading the transcript and metadata.
