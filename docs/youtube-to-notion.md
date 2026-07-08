# How to turn a YouTube video into timestamped Notion notes

## Problem

You want reusable notes from a YouTube video, but a raw transcript is hard to review and a one-off summary is hard to verify later.

## What video-to-notes Does

video-to-notes downloads available YouTube captions first, falls back to local Whisper only when needed, generates transcript and metadata files, and can publish the final report to Notion.

## Installation

```bash
git clone https://github.com/KIRVO-REPORTING/video-to-notes.git
cd video-to-notes
./install.sh
```

## Command

Configure Notion output:

```bash
video-to-notes configure --environment notion
```

Process a YouTube video:

```bash
video-to-notes process "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Output Files

The local workspace keeps:

- `metadata.json`
- `transcript.txt`
- `summary.md`
- `report.html`

When Notion publishing is configured, the report can also be written to a Notion page or database row.

## Common Errors

### The video has no captions

Run `video-to-notes configure` and enable the recommended local Whisper fallback model.

### The video requires sign-in

Use browser cookies:

```bash
video-to-notes process "VIDEO_URL" --cookies-from-browser chrome
```

### Notion publishing is not configured

Use a connected Notion agent connector where available, or configure CLI Notion credentials for command-line publishing.

## FAQ

### Does this always use Whisper?

No. Captions are used first. Local Whisper is only used as a fallback.

### Can I keep the report local?

Yes. Use `--environment local` or configure local output.
