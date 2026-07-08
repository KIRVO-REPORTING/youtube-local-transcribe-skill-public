# Examples

## YouTube Transcript to Timestamped Notes

```bash
video-to-notes process "https://www.youtube.com/watch?v=VIDEO_ID" --language en
```

Use this when you want a YouTube transcript, timestamped AI summary, local report, and optional Notion or Obsidian note.

## Bilibili Transcript and Summary

```bash
video-to-notes process "https://www.bilibili.com/video/BV..." --language zh
```

Use this for Bilibili videos that have downloadable captions or can be transcribed locally with Whisper fallback.

## Force Local Whisper

```bash
video-to-notes process "VIDEO_URL" --force-transcribe
```

Use this when captions are low quality and you want a local Whisper transcript instead.

## Use Browser Cookies

```bash
video-to-notes process "VIDEO_URL" --cookies-from-browser chrome
```

Use this when a platform requires the same access your browser already has.

## Publish to Obsidian

```bash
video-to-notes configure --environment obsidian
video-to-notes process "VIDEO_URL"
```

The Obsidian publisher creates Markdown notes inside your vault and maintains a video reports dashboard.

## Publish to Notion

```bash
video-to-notes configure --environment notion
video-to-notes process "VIDEO_URL"
```

The Notion publisher creates or updates a report page or database row when Notion credentials or an agent connector are available.
