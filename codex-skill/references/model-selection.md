# Model Selection

Read this reference when installing the public video transcription workflow on a new machine, troubleshooting local transcription performance, or deciding which model/backend to use.

## First Rule

If the video has downloadable manual or automatic subtitles in a suitable language, do not install or run Whisper for that video. Use the subtitle file to create `transcript.txt`.

## Hardware Matrix

| Local spec | Backend | Default model | Device / compute | Notes |
|---|---|---|---|---|
| Downloadable manual or auto captions | none | none | none | Use captions directly; fastest and lowest cost |
| Apple Silicon, >=16 GB unified memory | `mlx` | `mlx-community/whisper-large-v3-turbo` | MLX | macOS default profile |
| Apple Silicon, 8-15 GB unified memory | `mlx` | `mlx-community/whisper-small` | MLX | Safer for long videos; manually upgrade for short videos |
| NVIDIA CUDA, >=10 GB VRAM | `faster-whisper` | `Systran/faster-whisper-large-v3-turbo` | `cuda` / `float16` | Fast GPU default |
| NVIDIA CUDA, 6-9 GB VRAM | `faster-whisper` | `Systran/faster-whisper-large-v3-turbo` | `cuda` / `int8_float16` | Lower VRAM profile |
| NVIDIA CUDA, 4-5 GB VRAM | `faster-whisper` | `Systran/faster-whisper-small` | `cuda` / `int8_float16` | Conservative GPU profile |
| CPU only, >=16 GB RAM | `faster-whisper` | `Systran/faster-whisper-small` | `cpu` / `int8` | Slow but usable |
| CPU only, 8-15 GB RAM | `faster-whisper` | `Systran/faster-whisper-base` | `cpu` / `int8` | Mainstream CPU fallback |
| CPU only, <8 GB RAM | `faster-whisper` | `Systran/faster-whisper-tiny` | `cpu` / `int8` | Minimal fallback; quality is limited |
| AMD GPU / ROCm | `faster-whisper` CPU path | `Systran/faster-whisper-small` | `cpu` / `int8` | Treat GPU acceleration as experimental until validated |

## Install Commands

Always start with:

```bash
ytlt probe
ytlt recommend
ytlt setup --dry-run
```

Run the plan only after checking it:

```bash
ytlt setup --execute
```

`setup --execute` downloads the hardware-recommended model into `<workspace>/models` and writes `<workspace>/config.json`. `ytlt install --execute` remains a compatible alias for the same setup behavior.

For manual installs:

```bash
# Apple Silicon
python -m pip install -e ".[mlx]"

# NVIDIA CUDA or CPU
python -m pip install -e ".[faster-whisper]"
```

## Overrides

Use explicit overrides only when the default recommendation is wrong or the user requests a different quality/speed tradeoff:

```bash
ytlt process "VIDEO_URL" --force-transcribe --backend faster-whisper --model Systran/faster-whisper-medium --device cpu --compute-type int8
ytlt process "VIDEO_URL" --force-transcribe --backend mlx --model mlx-community/whisper-large-v3-turbo
```
