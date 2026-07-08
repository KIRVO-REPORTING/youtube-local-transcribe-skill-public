# Quickstart

Use this quickstart to install video-to-notes and turn a video URL into a transcript, timestamped AI summary, and local HTML report.

## Install

```bash
git clone https://github.com/KIRVO-REPORTING/video-to-notes.git
cd video-to-notes
./install.sh
```

On Windows PowerShell:

```powershell
git clone https://github.com/KIRVO-REPORTING/video-to-notes.git
cd video-to-notes
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

## Configure

```bash
video-to-notes configure
```

The configuration flow asks for:

- Your usual transcript and report language.
- Whether to install a local Whisper fallback model.
- Whether the default output should be local HTML, Notion, or Obsidian.

## Process a Video

```bash
video-to-notes process "VIDEO_URL"
```

## Output Files

Each processed video folder includes:

- `metadata.json`: video source, title, platform, duration, channel, and transcript source.
- `transcript.txt`: downloaded captions or local Whisper transcript.
- `summary.md`: timestamped notes written by an agent or user.
- `report.html`: browser-readable report.

## Open the Dashboard

```bash
video-to-notes serve --open
```
