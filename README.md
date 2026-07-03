# youtube-local-transcribe

Caption-first local transcription workflow for YouTube, Bilibili, TED, and other `yt-dlp` supported video URLs.

This repository contains:

- `ytlt`: a Python CLI for machine probing, hardware-aware setup, caption download, local Whisper fallback transcription, HTML report generation, and dashboard serving.
- `codex-skill`: a Codex skill wrapper that tells Codex how to run the CLI and write grounded summaries from generated transcripts.

## Features

- Prefer manual or automatic captions before running local Whisper.
- Support plain subtitle files and HLS subtitle playlists such as segmented `.m3u8` VTT captions.
- Detect Apple Silicon, NVIDIA CUDA, CPU RAM, and ffmpeg availability.
- Download the hardware-recommended Whisper model during initial setup.
- Store setup state in `<workspace>/config.json` and models in `<workspace>/models`.
- Generate per-video `metadata.json`, `transcript.txt`, `summary.txt`, and `report.html`.
- Build and serve a local searchable dashboard of processed reports.
- Keep downloaded video files out of final report folders after finalization.

## Requirements

- Python 3.9 or newer. Python 3.10+ is recommended because recent `yt-dlp` versions deprecate Python 3.9.
- Network access for `yt-dlp`, captions, and optional Hugging Face model downloads.
- Enough disk space for Whisper models when local transcription is needed.

The package depends on `yt-dlp` and `imageio-ffmpeg` by default. Setup also verifies that an ffmpeg binary can be resolved from the system, `YTLT_FFMPEG`, workspace config, or `imageio-ffmpeg`.

## Install And Setup

From the repository root:

```bash
python -m pip install -e .
ytlt probe
ytlt setup --dry-run
ytlt setup --execute
```

`ytlt setup --execute`:

1. Probes the local machine.
2. Installs the matching backend extra.
3. Verifies ffmpeg availability.
4. Downloads the recommended Whisper model into `<workspace>/models`.
5. Writes `<workspace>/config.json`.

The default workspace is:

```text
~/Documents/youtube
```

Use another workspace with:

```bash
ytlt setup --workspace /path/to/workspace --execute
```

## Hardware Model Selection

| Local hardware | Backend | Default model |
|---|---|---|
| Apple Silicon, 16 GB+ unified memory | `mlx` | `mlx-community/whisper-large-v3-turbo` |
| Apple Silicon, 8-15 GB unified memory | `mlx` | `mlx-community/whisper-small` |
| NVIDIA CUDA, 10 GB+ VRAM | `faster-whisper` | `Systran/faster-whisper-large-v3-turbo` |
| NVIDIA CUDA, 6-9 GB VRAM | `faster-whisper` | `Systran/faster-whisper-large-v3-turbo` |
| NVIDIA CUDA, 4-5 GB VRAM | `faster-whisper` | `Systran/faster-whisper-small` |
| CPU only, 16 GB+ RAM | `faster-whisper` | `Systran/faster-whisper-small` |
| CPU only, 8-15 GB RAM | `faster-whisper` | `Systran/faster-whisper-base` |
| CPU only, under 8 GB RAM | `faster-whisper` | `Systran/faster-whisper-tiny` |

Captions are still preferred when available, even if a local model has been configured.

## Process A Video

```bash
ytlt process "VIDEO_URL" --language zh
```

Useful options:

```bash
ytlt process "VIDEO_URL" --language en
ytlt process "VIDEO_URL" --cookies-from-browser chrome
ytlt process "VIDEO_URL" --force-transcribe
ytlt process "VIDEO_URL" --no-transcribe-fallback
ytlt process "VIDEO_URL" --open
```

The processor creates one folder per video under:

```text
<workspace>/processed/
```

Each processed folder contains:

- `metadata.json`
- `transcript.txt`
- `report.html`
- `summary.txt` after a summary is written and finalized

When local Whisper is needed, `ytlt process` uses the configured model path from `<workspace>/config.json` unless `--model` is supplied.

## Finalize A Report

After writing a plain-text summary to `<video-folder>/summary.txt`, run:

```bash
ytlt finalize "<video-folder>"
```

Finalization re-renders `report.html`, deletes retained `video.*` media files from that folder, and rebuilds the dashboard index.

## Dashboard

Rebuild the index:

```bash
ytlt rebuild-index
```

Serve the dashboard locally:

```bash
ytlt serve --open
```

The server binds to `127.0.0.1` by default.

## Codex Skill Install

Copy `codex-skill` into your Codex skills directory:

```bash
mkdir -p "$HOME/.codex/skills"
rm -rf "$HOME/.codex/skills/youtube-local-transcribe"
cp -R codex-skill "$HOME/.codex/skills/youtube-local-transcribe"
```

Restart Codex after replacing an installed skill so the new `SKILL.md` metadata is loaded.

## Development

Install locally:

```bash
python -m pip install -e .
```

Run tests:

```bash
python -m unittest discover -s tests
```

Run a setup dry run:

```bash
ytlt setup --dry-run
```

Run a lightweight caption-first processing test:

```bash
ytlt process "https://www.ted.com/talks/sir_ken_robinson_do_schools_kill_creativity" --language en --no-transcribe-fallback
```

## Repository Layout

```text
ytlt/                  Python CLI package
codex-skill/           Codex skill wrapper
tests/                 Unit tests
pyproject.toml         Package metadata
README.md              Project documentation
```

Generated workspaces, downloaded media, models, virtual environments, and build metadata are ignored by `.gitignore`.
