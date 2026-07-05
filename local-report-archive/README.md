# Local Report Archive

This directory carries the local reports that existed before the Notion output branch was created.

- `root-workspace/` was copied from `/Users/ff/Documents/电商搜索`.
- `youtube-reports-workspace/` was copied from `/Users/ff/Documents/电商搜索/youtube_reports`.

Each workspace keeps its original `dashboard.html`, `index.json`, and `processed/` report folders so the dashboard links continue to work from the archived location.

The archived reports were also indexed in this Notion database:

- https://app.notion.com/p/82c3e1c2f57f489eab322f4898d0e4e6

Open a report by clicking its `Name` cell in the database. The row page itself contains the report summary and notes.

Use the Notion publisher on any archived report folder when migrating historical reports:

```bash
ytlt publish-notion "local-report-archive/root-workspace/processed/<video-folder>"
```
