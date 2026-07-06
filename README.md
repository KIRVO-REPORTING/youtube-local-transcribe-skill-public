# youtube-local-transcribe

Caption first. Local Whisper when needed. Searchable local reports.

`youtube-local-transcribe` turns YouTube, Bilibili, TED, and other `yt-dlp` supported video URLs into local transcripts, grounded summaries, browser-readable HTML reports, and an optional Notion report database.

- [中文说明](#中文说明)
- [English](#english)

## 中文说明

### 这个项目是做什么的

`youtube-local-transcribe` 是一个面向 AI Coding Agent 和命令行用户的视频资料整理工具。它会优先下载视频自带字幕，在没有合适字幕时才使用本地 Whisper 转写，并把每个视频整理成可追溯的本地报告。

这个仓库包含两部分：

- `ytlt`: Python CLI，负责环境检测、字幕下载、本地 Whisper fallback、报告生成、Notion 发布和本地 dashboard。
- `codex-skill`: Codex 技能说明，让 Codex 知道如何调用 `ytlt`、读取转写文本、写出有时间戳依据的摘要报告。

### 要解决的问题

长视频、课程、访谈、发布会和研究材料通常有几个麻烦：

- 字幕、转写、摘要和来源链接分散，后续很难复查。
- 很多视频其实有字幕，不需要一上来就跑本地 Whisper。
- AI 摘要如果没有绑定原始 transcript 和时间戳，可信度和可追溯性很弱。
- 处理过的视频缺少统一索引，时间久了很难找到以前的报告。

这个项目把流程固定下来：字幕优先，本地转写作为兜底，所有结果落到本地 workspace，并生成可搜索的 HTML dashboard。需要时还能把最终报告同步到 Notion。

### 复制给 Codex 或 Claude Code 的一行配置指令

把下面这一行复制给 Codex 或 Claude Code，它就可以按这个项目的方式安装和配置：

```text
请安装并配置 youtube-local-transcribe：克隆 https://github.com/KIRVO-REPORTING/youtube-local-transcribe-skill-public，进入仓库后运行 python -m pip install -e .；如果当前工具是 Codex，请把 codex-skill 安装到 ~/.codex/skills/youtube-local-transcribe；只有在需要本地 Whisper fallback 时才运行 ytlt setup --execute；最后用 ytlt process "VIDEO_URL" --language zh --open 处理视频。
```

### 工作流程简介

1. 用户给出一个视频 URL。
2. `ytlt process "VIDEO_URL"` 调用 `yt-dlp` 获取元数据和字幕。
3. 工具优先使用人工字幕或自动字幕；字幕不可用时，才走本地 Whisper。
4. 每个视频会生成独立目录，包含 `metadata.json`、`transcript.txt` 和 `report.html`。
5. Codex 或其他 Agent 读取 `metadata.json` 与 `transcript.txt`，写入有依据的 `summary.md`。
6. `ytlt finalize "<video-folder>"` 重新渲染最终 HTML 报告，清理下载的视频文件，并刷新 dashboard。
7. 可选：使用 `--publish-notion` 把报告发布或更新到 Notion。

### 快速安装

```bash
git clone https://github.com/KIRVO-REPORTING/youtube-local-transcribe-skill-public.git
cd youtube-local-transcribe-skill-public
python -m pip install -e .
```

先处理一个带字幕的视频：

```bash
ytlt process "VIDEO_URL" --language zh --open
```

如果需要本地 Whisper fallback，再运行一次性设置：

```bash
ytlt setup --execute
```

`ytlt setup --execute` 会检测本机硬件、选择合适后端、确认 ffmpeg、下载推荐 Whisper 模型，并写入 workspace 配置。

默认 workspace：

```text
~/Documents/youtube
```

指定其它 workspace：

```bash
ytlt process "VIDEO_URL" --workspace /path/to/workspace
```

### 常用命令

| 场景 | 命令 |
|---|---|
| 下载字幕并生成报告 | `ytlt process "VIDEO_URL" --language zh --open` |
| 使用浏览器 cookies | `ytlt process "VIDEO_URL" --cookies-from-browser chrome` |
| 强制本地 Whisper 转写 | `ytlt process "VIDEO_URL" --force-transcribe` |
| 字幕缺失时不做本地转写 | `ytlt process "VIDEO_URL" --no-transcribe-fallback` |
| 写好 `summary.md` 后重新生成报告 | `ytlt finalize "/path/to/video-folder" --open` |
| 发布或更新 Notion 报告 | `ytlt finalize "/path/to/video-folder" --publish-notion` |
| 发布已有处理目录到 Notion | `ytlt publish-notion "/path/to/video-folder"` |
| 重建本地索引 | `ytlt rebuild-index` |
| 打开本地 dashboard | `ytlt serve --open` |

每个处理后的视频目录位于：

```text
<workspace>/processed/
```

目录通常包含：

- `metadata.json`: 视频标题、来源、平台、时长、发布时间、处理时间和 transcript 来源。
- `transcript.txt`: 字幕或本地 Whisper 生成的全文。
- `summary.md`: Agent 或用户写入的摘要。
- `report.html`: 浏览器可读报告。

### Codex Skill 安装

从克隆后的仓库安装：

```bash
mkdir -p "$HOME/.codex/skills/youtube-local-transcribe"
rsync -a --delete codex-skill/ "$HOME/.codex/skills/youtube-local-transcribe/"
```

Windows PowerShell：

```powershell
$target = Join-Path $HOME ".codex\skills\youtube-local-transcribe"; if (Test-Path $target) { Remove-Item $target -Recurse -Force }; New-Item -ItemType Directory -Force $target | Out-Null; Copy-Item ".\codex-skill\*" $target -Recurse -Force
```

替换已安装技能后，重启 Codex，让新的 `SKILL.md` 元数据生效。

然后把视频链接发给 Codex，或直接说：

```text
Use youtube-local-transcribe to process this video and create a summary report: VIDEO_URL
```

### 发布到 Notion

创建 Notion integration token，把目标页面或 data source 分享给该 integration，然后设置：

```bash
export NOTION_TOKEN="secret_..."
export NOTION_DATA_SOURCE_ID="..."
```

目标变量三选一：

- `NOTION_DATA_SOURCE_ID`: 推荐，用于 Notion database/data source dashboard。
- `NOTION_PARENT_PAGE_ID`: 在普通 Notion 页面下创建报告页面。
- `NOTION_DATABASE_ID`: 自动解析 database 的第一个 data source。

处理时发布：

```bash
ytlt process "VIDEO_URL" --language zh --publish-notion
```

已有目录发布：

```bash
ytlt publish-notion "/path/to/processed/video-folder"
```

发布成功后，`metadata.json` 会记录 `notion_page_id`、`notion_url` 和 `notion_synced_at`，后续发布会更新同一条 Notion 页面，避免重复。

### 本地开发

```bash
python -m pip install -e .
python -m unittest discover -s tests
```

字幕优先 smoke test：

```bash
ytlt process "https://www.ted.com/talks/sir_ken_robinson_do_schools_kill_creativity" --language en --no-transcribe-fallback
```

### 注意事项

- 需要 Python 3.9 或更新版本，推荐 Python 3.10+。
- 字幕永远优先于本地 Whisper。
- `ytlt setup --execute` 只在需要本地 Whisper fallback 时必须运行。
- 硬件模型选择规则见 `codex-skill/references/model-selection.md`。
- workspace、下载媒体、模型、虚拟环境和构建产物会被 `.gitignore` 排除。

## English

### What this project does

`youtube-local-transcribe` is a video knowledge capture workflow for AI coding agents and command-line users. It prefers existing captions, falls back to local Whisper only when captions are missing or unsuitable, and turns each video into a traceable local report.

This repository contains:

- `ytlt`: a Python CLI for machine probing, caption download, local Whisper fallback, report generation, Notion publishing, and local dashboard serving.
- `codex-skill`: a Codex skill wrapper that teaches Codex how to run `ytlt`, read transcripts, and write grounded timestamped summaries.

### Problem it solves

Long videos, courses, interviews, conference talks, and research material are hard to reuse when transcripts, summaries, and source links are scattered. Many videos already have captions, so running local Whisper first wastes time and compute. AI summaries are also hard to trust when they are not tied back to transcript text and timestamps.

This project makes the workflow repeatable: captions first, local transcription only as fallback, all artifacts stored under one local workspace, searchable HTML reports, and optional Notion publishing.

### One-line setup prompt for Codex or Claude Code

Copy this single line into Codex or Claude Code:

```text
Install and configure youtube-local-transcribe: clone https://github.com/KIRVO-REPORTING/youtube-local-transcribe-skill-public, run python -m pip install -e . from the repo, install codex-skill to ~/.codex/skills/youtube-local-transcribe if this is Codex, run ytlt setup --execute only when local Whisper fallback is needed, then process a video with ytlt process "VIDEO_URL" --language en --open.
```

### Workflow overview

1. The user provides a video URL.
2. `ytlt process "VIDEO_URL"` uses `yt-dlp` to fetch metadata and captions.
3. The tool uses manual or automatic captions first; if captions are unavailable, it can fall back to local Whisper.
4. Each video gets its own folder with `metadata.json`, `transcript.txt`, and `report.html`.
5. Codex or another agent reads `metadata.json` and `transcript.txt`, then writes a grounded `summary.md`.
6. `ytlt finalize "<video-folder>"` re-renders the final HTML report, removes retained downloaded video files, and refreshes the dashboard.
7. Optional: `--publish-notion` publishes or updates the report in Notion.

### Quick install

```bash
git clone https://github.com/KIRVO-REPORTING/youtube-local-transcribe-skill-public.git
cd youtube-local-transcribe-skill-public
python -m pip install -e .
```

Process a captioned video first:

```bash
ytlt process "VIDEO_URL" --language en --open
```

Run setup only when you need local Whisper fallback:

```bash
ytlt setup --execute
```

`ytlt setup --execute` probes the machine, selects the matching backend, verifies ffmpeg, downloads the recommended Whisper model, and writes workspace configuration.

Default workspace:

```text
~/Documents/youtube
```

Use another workspace:

```bash
ytlt process "VIDEO_URL" --workspace /path/to/workspace
```

### Common commands

| Use case | Command |
|---|---|
| Download captions and build a report | `ytlt process "VIDEO_URL" --language en --open` |
| Use browser cookies | `ytlt process "VIDEO_URL" --cookies-from-browser chrome` |
| Force local Whisper transcription | `ytlt process "VIDEO_URL" --force-transcribe` |
| Skip local transcription when captions are missing | `ytlt process "VIDEO_URL" --no-transcribe-fallback` |
| Re-render after writing `summary.md` | `ytlt finalize "/path/to/video-folder" --open` |
| Publish or update a Notion report | `ytlt finalize "/path/to/video-folder" --publish-notion` |
| Publish an existing folder to Notion | `ytlt publish-notion "/path/to/video-folder"` |
| Rebuild local index | `ytlt rebuild-index` |
| Open local dashboard | `ytlt serve --open` |

Each processed video folder is created under:

```text
<workspace>/processed/
```

Typical outputs:

- `metadata.json`: title, source URL, platform, duration, publish time, processing time, and transcript source.
- `transcript.txt`: transcript from captions or local Whisper.
- `summary.md`: summary written by an agent or user.
- `report.html`: browser-readable report.

### Codex skill install

From a cloned copy of this repo:

```bash
mkdir -p "$HOME/.codex/skills/youtube-local-transcribe"
rsync -a --delete codex-skill/ "$HOME/.codex/skills/youtube-local-transcribe/"
```

Windows PowerShell:

```powershell
$target = Join-Path $HOME ".codex\skills\youtube-local-transcribe"; if (Test-Path $target) { Remove-Item $target -Recurse -Force }; New-Item -ItemType Directory -Force $target | Out-Null; Copy-Item ".\codex-skill\*" $target -Recurse -Force
```

Restart Codex after replacing an installed skill so the new `SKILL.md` metadata is loaded.

Then send Codex a video URL or ask:

```text
Use youtube-local-transcribe to process this video and create a summary report: VIDEO_URL
```

### Publish to Notion

Create a Notion integration token, share the target page or data source with the integration, then set:

```bash
export NOTION_TOKEN="secret_..."
export NOTION_DATA_SOURCE_ID="..."
```

Use exactly one target:

- `NOTION_DATA_SOURCE_ID`: recommended for a Notion database/data source dashboard.
- `NOTION_PARENT_PAGE_ID`: create report pages under a normal Notion page.
- `NOTION_DATABASE_ID`: resolve the database's first data source automatically.

Publish while processing:

```bash
ytlt process "VIDEO_URL" --language en --publish-notion
```

Publish an existing processed folder:

```bash
ytlt publish-notion "/path/to/processed/video-folder"
```

After publishing, `metadata.json` records `notion_page_id`, `notion_url`, and `notion_synced_at`; later publishes update the same Notion page instead of creating duplicates.

### Local development

```bash
python -m pip install -e .
python -m unittest discover -s tests
```

Caption-first smoke test:

```bash
ytlt process "https://www.ted.com/talks/sir_ken_robinson_do_schools_kill_creativity" --language en --no-transcribe-fallback
```

### Notes

- Python 3.9+ is required. Python 3.10+ is recommended.
- Captions are always preferred before local Whisper.
- `ytlt setup --execute` is only required for local Whisper fallback.
- Hardware model selection lives in `codex-skill/references/model-selection.md`.
- Generated workspaces, downloaded media, models, virtual environments, and build metadata are ignored by `.gitignore`.
