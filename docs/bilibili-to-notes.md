# How to turn a Bilibili video into transcripts and AI summaries

## Problem

Bilibili videos can be useful for research, lectures, product demos, and technical talks, but the transcript, summary, source URL, and timestamps are often scattered.

## What video-to-notes Does

video-to-notes uses `yt-dlp` to inspect Bilibili video metadata and captions, writes a local transcript, creates a timestamped report workflow, and can publish notes to local HTML, Notion, or Obsidian.

## Installation

```bash
git clone https://github.com/KIRVO-REPORTING/video-to-notes.git
cd video-to-notes
./install.sh
```

## Command

```bash
video-to-notes process "https://www.bilibili.com/video/BV..." --language zh
```

If Bilibili requires browser access:

```bash
video-to-notes process "https://www.bilibili.com/video/BV..." --language zh --cookies-from-browser chrome
```

## Output Files

- `metadata.json`: source URL, title, platform, duration, and transcript source.
- `transcript.txt`: captions or local Whisper transcript.
- `summary.md`: timestamped AI notes.
- `report.html`: local browser-readable report.

## Common Errors

### Captions are unavailable

Enable local Whisper fallback with:

```bash
video-to-notes configure
```

### Bilibili access is restricted

Pass browser cookies from an already signed-in browser session.

## FAQ

### Does this support BV links?

Yes. BV links are handled through `yt-dlp` when metadata and captions are accessible.

### Can this publish Bilibili notes to Obsidian?

Yes. Configure Obsidian output with `video-to-notes configure --environment obsidian`.
