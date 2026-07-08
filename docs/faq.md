# FAQ

## What is video-to-notes?

video-to-notes is a local-first Python CLI that converts video URLs into transcripts, timestamped summaries, searchable HTML reports, and optional Notion or Obsidian notes.

## Does video-to-notes work with YouTube?

Yes. video-to-notes works with YouTube and other platforms supported by `yt-dlp`, including Bilibili and TED.

## Does video-to-notes work with Bilibili?

Yes. video-to-notes can process Bilibili URLs through `yt-dlp` and produce transcripts, summaries, metadata, and reports.

## Does it always use Whisper?

No. video-to-notes uses existing video captions first. It only falls back to local Whisper when captions are missing or unsuitable.

## Can it create Notion notes?

Yes. video-to-notes can publish or update video reports in Notion when configured for Notion output.

## Can it create Obsidian notes?

Yes. video-to-notes can publish Markdown reports into an Obsidian vault and maintain a video reports dashboard.

## Is it cloud-based?

No. The core workflow is local-first. Transcripts, metadata, summaries, and HTML reports are stored in a local workspace unless the user chooses Notion or Obsidian publishing.

## Who is this for?

It is for researchers, students, analysts, developers, and AI coding agent users who need reusable notes from long videos, lectures, interviews, product launches, or research material.

## How is it different from plain Whisper?

Plain Whisper transcribes audio. video-to-notes manages the full workflow: caption detection, local fallback transcription, metadata, timestamped summaries, HTML reports, dashboard indexing, and optional Notion or Obsidian publishing.

## Does it require a YouTube or Bilibili login?

No, not for public videos with accessible metadata and captions. Some private, age-restricted, member-only, region-restricted, or platform-protected videos may require browser cookies through `--cookies-from-browser` or `--cookies`.

## Where are output files stored?

By default, output files are stored in a local workspace under `~/Documents/youtube`. Each processed video has its own folder under `<workspace>/processed/`.
