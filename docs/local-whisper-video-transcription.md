# Local Whisper video transcription with caption-first fallback

## Problem

Plain local Whisper transcription is useful, but many videos already have captions. Running local transcription for every video can waste compute and still leave you without metadata, reports, dashboard indexing, or publishing.

## What video-to-notes Does

video-to-notes checks for existing captions first. It only runs local Whisper when captions are missing or unsuitable, then stores transcript files, metadata, timestamped summaries, and local HTML reports in one workspace.

## Installation

```bash
git clone https://github.com/KIRVO-REPORTING/video-to-notes.git
cd video-to-notes
./install.sh
```

## Command

Configure a recommended local Whisper fallback:

```bash
video-to-notes configure --model-choice recommended --execute
```

Process a video:

```bash
video-to-notes process "VIDEO_URL"
```

Force local Whisper even when captions exist:

```bash
video-to-notes process "VIDEO_URL" --force-transcribe
```

## Output Files

- `transcript.txt`: local Whisper transcript or downloaded caption transcript.
- `metadata.json`: transcript source and video metadata.
- `report.html`: searchable local report.
- local dashboard index under the configured workspace.

## Common Errors

### Whisper backend is missing

Run:

```bash
video-to-notes configure --model-choice recommended --execute
```

### Captions are poor quality

Use `--force-transcribe` to prefer local Whisper.

### No local fallback is configured

Re-run `video-to-notes configure` and choose the recommended model instead of `none`.

## FAQ

### Is video-to-notes a replacement for Whisper?

No. It wraps Whisper in a larger video-to-notes workflow that also handles captions, metadata, reports, indexing, Notion, and Obsidian.

### Does local Whisper send transcripts to a cloud service?

No. The local Whisper fallback runs locally through the configured backend.
