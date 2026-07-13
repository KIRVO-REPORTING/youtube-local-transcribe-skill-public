# Notion Publishing

Read this reference only when the user requests Notion or `preferences.output_environment` is `notion`.

## Choose one publishing path

1. If `NOTION_TOKEN` or `NOTION_API_KEY` and exactly one target ID are available, use the CLI after `summary.md` and `tags.json` are complete:

   ```bash
   video-to-notes finalize "VIDEO_FOLDER" --environment notion
   ```

   Supported targets are `NOTION_DATA_SOURCE_ID`, `NOTION_DATABASE_ID`, or `NOTION_PARENT_PAGE_ID`. Prefer the data source target for the report database.
2. If no CLI token exists but a Notion connector is connected, finalize with `--environment local`, then create or update the database row through the connector.
3. If neither path is available, return the completed local report and state that Notion credentials/connection are missing.

Never run `process` with the Notion environment: that can publish a preliminary report before the summary exists. Never claim success unless the CLI or connector returns a Notion URL.

## Database contract

Create or reuse one database named `本地视频报告数据库`. Use one row per report; the row opened from `Name` is the report page. Do not create a duplicate detail page.

Use these properties:

- `Name` title
- `Platform` select
- `Transcript Source` select
- `Channel` rich text
- `Source URL` URL
- `Published` date
- `Processed` date
- `Processing Seconds` number
- `Duration Seconds` number
- `Summary` rich text
- `Local Report` rich text
- `Tags` multi-select populated only from `tags.json`

Useful views are `Dashboard`, `All Reports`, `Captions`, `Whisper`, and `Recent`. Do not require a `Status` or `Report Page` property.

## Row body

Write the report content directly into the database row:

```text
## Summary
Answer-first summary.

## Key Points
- [01m24s-02m44s](SOURCE_URL_WITH_t=84) Transcript-backed point.

## Notes
Only trust-affecting caveats.

## Source And Local Files
- Source: SOURCE_URL
- Platform: youtube | bilibili | video
- Channel: CHANNEL
- Published: DATE
- Transcript Source: manual_subtitle | auto_subtitle | local_whisper
- Processing Seconds: VALUE
- Local Report: /absolute/path/to/report.html
- Tags: values from tags.json

<toggle title="Transcript">
Full transcript text.
</toggle>
```

Keep the transcript folded at the end instead of always expanded. Convert Key Point timestamps into clickable links to the source start time.

## Deduplication and local metadata

Deduplicate in this order: `source_url`, then `platform + id`, then folder path. Update the existing row rather than creating a second row.

After connector publishing, write returned values to `metadata.json` when possible:

- `notion_parent_page_id`, `notion_parent_url`
- `notion_database_id`, `notion_database_url`
- `notion_data_source_id`
- `notion_database_row_id`, `notion_database_row_url`
- `notion_page_id`, `notion_url` pointing to the same row
- `notion_synced_at`, `notion_sync_method`

Skip evaluation and `.test-workspace` artifacts during bulk sync unless explicitly requested.
