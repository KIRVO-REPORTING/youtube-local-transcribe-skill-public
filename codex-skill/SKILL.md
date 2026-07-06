---
name: youtube-local-transcribe
description: Caption-first local video archiving, transcription, summarization, report generation, default clean Notion database publishing, dashboard workflow, concise final answers, and video-topic thread titles for YouTube, youtu.be, Bilibili, b23.tv, BV, av, ep, ss, and other yt-dlp supported video URLs. Use when the user sends a bare video link or asks to download subtitles, transcribe locally, summarize a video, create notes, generate an HTML report, publish to Notion, create a Notion report database, sync local reports, open a local browser report, inspect past video reports, or serve a local report dashboard.
---

# YouTube Local Transcribe

Use this workflow for bare video URLs and explicit video transcription, summary, archive, Notion sync, or report requests. Prefer downloadable subtitles first; use local Whisper only when captions are missing, unsuitable, or the user forces transcription. Publish or update the clean Notion report by default after local finalization unless the user explicitly asks for local-only output or Notion is unavailable.

## Current Artifact Workflow

For bare video links, report requests, Notion sync requests, or the current clean report output, produce the current artifact directly:

1. Process the video with `ytlt process`, preferring captions and falling back to local Whisper only when needed.
2. Read `metadata.json` and `transcript.txt`; write `summary.md` with an answer-first overview and timestamped Key Points grounded in the transcript.
3. Run `ytlt finalize "<video-folder>"` to refresh the local `report.html` and dashboard index.
4. Publish or update the Notion database row report by default. The Notion row opened from `Name` is the report content page.
5. Rename the current Codex thread to a concise video-topic title when a thread-title tool is available and the current thread id can be resolved.
6. Return the Notion report row URL as the primary output, plus the database URL and local `report.html` path.

Do not stop at only a local HTML report or dashboard for bare links or report requests unless the user explicitly asks for local-only output or Notion publishing is blocked. Local files remain the backing archive; Notion is the reader-facing deliverable.

Keep user-facing progress and final responses focused on the video result. Avoid dumping download, transcode, caption conversion, test, command, codec, cleanup, or file-by-file process logs unless the user asks for that detail or the workflow fails.

The current Notion artifact is:

- Parent page with a short `报告数据库` section and concise sync status.
- Database named `本地视频报告数据库`.
- One row per report. Opening `Name` shows the report body itself.
- No duplicate detail page, no `Report Page` property, and no `Status` property.
- Row body sections: `Summary`, `Key Points`, `Notes`, source/local metadata, and a final folded `Transcript` block.
- Timestamped Key Points are clickable source-video links that seek to the start second.

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
ytlt process "VIDEO_URL" --publish-notion
```

The processor creates a per-video folder under `<workspace>/processed/`, writes `metadata.json`, `transcript.txt`, and `report.html`, and updates `index.json` plus `dashboard.html`.
When local Whisper is needed, it uses the configured model path from `<workspace>/config.json` unless `--model` is provided.

The JSON output includes the folder and report paths. Read `metadata.json` and `transcript.txt` before summarizing.

## Write The Summary

Write a grounded Markdown summary to `<video-folder>/summary.md`. Use the user's language unless the user requests another language. Prefer an answer-first structure with timestamped Key Points and optional one-level nested supporting bullets.

Do not force every point into `Point` / `Evidence` / `Implication` labels. Use top-level bullets for the video's major conclusions, claims, risks, decisions, or methods. Use nested bullets only when a point needs transcript-backed support, examples, numbers, caveats, or subclaims. Do not add nested bullets just to satisfy the shape.

Use this structure:

```text
Summary

One-paragraph answer-first summary naming the video's core conclusion.

Key Points

- [mm:ss-mm:ss] Point 1.
  - [mm:ss-mm:ss] Supporting detail, example, subclaim, number, or caveat.
  - [mm:ss-mm:ss] Another supporting detail when it materially helps.

- [mm:ss-mm:ss] Point 2.
- [mm:ss-mm:ss] Point 3.

Notes

- Caveats about subtitle quality, audio quality, uncertain terms, or incomplete transcript.
```

For video reports, each Key Point bullet and nested supporting bullet should start with a bracketed timestamp or time range such as `[01:24-02:44]`, using the transcript's actual timing. Use `[hh:mm:ss-hh:mm:ss]` for videos longer than one hour. The report renderer and CLI Notion publisher convert bracketed timestamps into clickable source-video links that seek to the start time, so keep the timestamp at the beginning of each bullet. When writing report content through the Notion connector Markdown path, avoid colons in the linked label because Notion can split the link; use an inline link like `[01m24s-02m44s](https://www.youtube.com/watch?v=VIDEO_ID&t=84)` instead of leaving it as plain text.

For long videos, consider parallel drafting after reading the full transcript once. Treat a video as long when it is roughly over 45 minutes, has a very large transcript, or naturally breaks into many segments. Split the transcript into contiguous timestamp ranges and, when subagents or parallel work are available, draft each range independently into candidate Key Points. Each parallel draft must receive only the metadata, its transcript slice, neighboring boundary context when needed, and the output structure above. The main agent must then merge the drafts into one coherent `summary.md`, remove repetition, normalize point wording, verify timestamp ranges against the transcript, and keep the final response focused on the report rather than the coordination process.

Finalize:

```bash
ytlt finalize "<video-folder>"
```

Finalization re-renders `report.html`, deletes any retained downloaded `video.*` media file, and refreshes the dashboard index. Continue into Notion publishing before responding unless the user explicitly asked for local-only output or Notion is unavailable.

## Notion Publishing

Use Notion publishing by default for bare video links and report requests. Skip it only when the user explicitly asks for local-only output, the environment has neither CLI Notion credentials nor a connected Notion app, or publishing fails after a reasonable retry. If skipped or blocked, state the reason in the final response and still return the local report path.

For CLI-based publishing, the required environment is:

```bash
export NOTION_TOKEN="secret_..."
```

Set exactly one target:

```bash
export NOTION_DATA_SOURCE_ID="..."
export NOTION_PARENT_PAGE_ID="..."
export NOTION_DATABASE_ID="..."
```

Prefer `NOTION_DATA_SOURCE_ID` for a Notion database/data-source dashboard. Use `NOTION_PARENT_PAGE_ID` only when the user wants plain child pages under a normal Notion page. `NOTION_DATABASE_ID` resolves the database's first data source automatically.

When CLI credentials and a target are available, publish during finalization or publish the already processed folder:

```bash
ytlt finalize "<video-folder>" --publish-notion
ytlt publish-notion "<video-folder>"
```

When Notion publishing succeeds, the JSON output includes `notion.notion_url`. Include that link in the final response alongside the local dashboard link. The publisher stores `notion_page_id`, `notion_url`, and `notion_synced_at` in `metadata.json`; later publishes update the same Notion page.

When running in Codex with a connected Notion app but no `NOTION_TOKEN`, use the Notion connector after `ytlt finalize`. Use the clean Notion database layout below. Do not claim the CLI wrote to Notion unless `--publish-notion` or `ytlt publish-notion` was used.

In final responses, lead with the video title and Notion row URL. Include the local report path only as the backing archive.

### Clean Notion Database Layout

When syncing reports to Notion, create or reuse one parent page as the workspace landing page. Keep this page clean:

- Add a short `报告数据库` section with the report database.
- Add a concise sync status section.
- Do not create separate report detail pages. The database row opened from `Name` is the report content page.
- Do not leave individual report pages scattered on the landing page.

Create or reuse a database named `本地视频报告数据库` under the parent page. Match the local dashboard columns:

- `Name` title
- `Platform` select: `youtube`, `bilibili`, `video`
- `Transcript Source` select: `manual_subtitle`, `auto_subtitle`, `local_whisper`, `unknown`
- `Channel` rich text
- `Source URL` URL
- `Published` date
- `Processed` date
- `Processing Seconds` number
- `Duration Seconds` number
- `Summary` rich text
- `Local Report` rich text

Create database views:

- `Dashboard`: core columns, sorted by `Processed` descending.
- `All Reports`: same as Dashboard.
- `Captions`: filter `Transcript Source = manual_subtitle`.
- `Whisper`: filter `Transcript Source = local_whisper`.
- `Recent`: recent reports without status filtering.

For each report, create one database row as the only Notion report page. Put the report content directly inside that row page so opening `Name` shows metadata, source link, summary, Key Points, notes, local report path, and the full transcript. The full transcript should be included by default as the final folded `Transcript` block, not as always-expanded page text.

Use this row body structure:

```text
## Summary
One answer-first summary paragraph.

## Key Points
- [01m24s-02m44s](SOURCE_URL_WITH_t=84) Main conclusion.
  - [01m30s-01m40s](SOURCE_URL_WITH_t=90) Concrete transcript-backed detail, example, number, or caveat.

## Notes
- Caveats about subtitles, transcription, uncertain terms, or source claims.

## Source And Local Files
- Source: SOURCE_URL
- Platform: youtube | bilibili | video
- Channel: CHANNEL
- Published: DATE
- Transcript Source: manual_subtitle | auto_subtitle | local_whisper
- Processing Seconds: PROCESSING_SECONDS
- Local Report: /absolute/path/to/report.html

<toggle title="Transcript">
Full transcript text.
</toggle>
```

Before syncing existing local reports, scan for folders containing both `metadata.json` and `report.html`; also read `index.json` when present. Deduplicate by `source_url`, then `platform + id`, then folder path. Skip evaluation and `.test-workspace` artifacts unless the user asks for every local report or explicitly includes tests.

After syncing, write the following fields back to each relevant `metadata.json` when possible:

- `notion_parent_page_id`, `notion_parent_url`
- `notion_database_id`, `notion_database_url`
- `notion_data_source_id`
- `notion_database_row_id`, `notion_database_row_url`
- `notion_page_id`, `notion_url` pointing to the same database row page
- `notion_synced_at`
- `notion_sync_method`

## Thread Title And Final Response

After reading `metadata.json`, derive the user-facing title from the source video's real title. If it is too long, trim it to a concise topic title of about 45-60 characters. Do not name the thread with generic workflow words such as `transcribe`, `caption`, `download`, or `youtube-local-transcribe`.

When a Codex thread-management tool is available and the current thread id can be resolved, rename the current thread to that concise video-topic title before the final response. If the thread id cannot be resolved, continue without blocking the report.

Final responses should use this shape:

```text
Completed: VIDEO_TITLE

Notion report: NOTION_ROW_URL
Local report: /absolute/path/to/report.html

Summary: One concise answer-first paragraph.

Key Points

- [mm:ss-mm:ss] Main point.
  - [mm:ss-mm:ss] Optional supporting detail or caveat.
- [mm:ss-mm:ss] Second main point.

Notes: Only include caveats or failures that affect trust in the result. Do not include the full transcript in the chat response; it is included in Notion as the final folded Transcript block.
```

Keep this response compact. Include conversion/process details only when they change the outcome, explain a failure, or the user explicitly asks for them.

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
