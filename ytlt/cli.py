from __future__ import annotations

import argparse
import functools
import json
import shutil
import subprocess
import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any

from .captions import choose_caption_track, download_caption, write_transcript_from_caption
from .config import configured_model_path, config_path, model_cache_dir, model_cache_path, write_config
from .ffmpeg import resolve_ffmpeg_path
from .notion import NotionError, NotionPublishConfig, publish_report_to_notion
from .reporting import (
    SUMMARY_FILENAME,
    delete_video_files,
    make_video_folder,
    normalize_metadata,
    read_metadata,
    rebuild_index,
    summary_file_path,
    write_report,
)
from .spec import MODEL_MATRIX, default_workspace, install_commands, probe, recommend, should_cache_model, to_json
from .transcribe import download_model, transcribe_video


VIDEO_EXTENSIONS = {".mp4", ".mkv", ".webm", ".mov", ".m4v"}


def _workspace(value: str | None) -> Path:
    return Path(value).expanduser().resolve() if value else default_workspace().resolve()


def _import_yt_dlp():
    try:
        import yt_dlp
    except ImportError as exc:
        raise SystemExit("yt-dlp is required. Install with: python -m pip install yt-dlp") from exc
    return yt_dlp


def _add_notion_options(parser: argparse.ArgumentParser, *, include_publish_flag: bool = True) -> None:
    if include_publish_flag:
        parser.add_argument("--publish-notion", action="store_true", help="Publish or update the report in Notion.")
    parser.add_argument("--notion-token", help="Defaults to NOTION_TOKEN or NOTION_API_KEY.")
    parser.add_argument("--notion-parent-page-id", help="Create report pages under this Notion page.")
    parser.add_argument("--notion-data-source-id", help="Create report rows in this Notion data source.")
    parser.add_argument("--notion-database-id", help="Resolve the first data source from this Notion database.")
    parser.add_argument("--notion-version", help="Defaults to NOTION_VERSION or 2026-03-11.")


def _notion_config(args: argparse.Namespace) -> NotionPublishConfig:
    try:
        return NotionPublishConfig.from_values(
            token=args.notion_token,
            parent_page_id=args.notion_parent_page_id,
            data_source_id=args.notion_data_source_id,
            database_id=args.notion_database_id,
            api_version=args.notion_version,
        )
    except NotionError as exc:
        raise SystemExit(str(exc)) from exc


def _workspace_for_folder(folder: Path) -> Path:
    return folder.parent.parent if folder.parent.name == "processed" else default_workspace()


def _publish_folder_to_notion(folder: Path, workspace: Path, args: argparse.Namespace) -> dict[str, Any]:
    try:
        return publish_report_to_notion(folder, _notion_config(args), workspace=workspace)
    except NotionError as exc:
        raise SystemExit(str(exc)) from exc


def extract_info(url: str, *, cookies_from_browser: str | None = None, cookies: Path | None = None) -> dict[str, Any]:
    yt_dlp = _import_yt_dlp()
    opts: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
    }
    if cookies_from_browser:
        opts["cookiesfrombrowser"] = (cookies_from_browser,)
    if cookies:
        opts["cookiefile"] = str(cookies)
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)


def download_video(
    url: str,
    folder: Path,
    *,
    cookies_from_browser: str | None = None,
    cookies: Path | None = None,
    referer: str | None = None,
    ffmpeg_location: str | None = None,
) -> Path:
    yt_dlp = _import_yt_dlp()
    before = {path.resolve() for path in folder.glob("*")}
    opts: dict[str, Any] = {
        "noplaylist": True,
        "format": "bv*[height<=1080]+ba/b[height<=1080]/best",
        "merge_output_format": "mp4",
        "outtmpl": str(folder / "video.%(ext)s"),
        "quiet": False,
        "no_warnings": False,
        "writeinfojson": True,
    }
    resolved_ffmpeg = resolve_ffmpeg_path(explicit=ffmpeg_location)
    if resolved_ffmpeg:
        opts["ffmpeg_location"] = resolved_ffmpeg
    if cookies_from_browser:
        opts["cookiesfrombrowser"] = (cookies_from_browser,)
    if cookies:
        opts["cookiefile"] = str(cookies)
    if referer:
        opts["referer"] = referer
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    candidates = [
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS and path.resolve() not in before
    ]
    if not candidates:
        candidates = [path for path in folder.iterdir() if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS]
    if not candidates:
        raise RuntimeError(f"Could not find downloaded video in {folder}")
    return max(candidates, key=lambda path: path.stat().st_size)


def process_url(args: argparse.Namespace) -> int:
    workspace = _workspace(args.workspace)
    output_root = Path(args.output_root).expanduser().resolve() if args.output_root else workspace / "processed"
    output_root.mkdir(parents=True, exist_ok=True)

    info = extract_info(
        args.url,
        cookies_from_browser=args.cookies_from_browser,
        cookies=args.cookies.expanduser().resolve() if args.cookies else None,
    )
    track = None if args.force_transcribe else choose_caption_track(info, args.language, allow_auto=not args.no_auto_subs)
    if not track and args.no_transcribe_fallback and not args.force_transcribe:
        raise SystemExit("No usable captions found and --no-transcribe-fallback was set.")
    transcript_source = track.source if track else "local_whisper"
    metadata = normalize_metadata(info, args.url, transcript_source=transcript_source)
    folder = make_video_folder(output_root, metadata)

    transcript_path = folder / "transcript.txt"
    caption_path: Path | None = None
    video_path: Path | None = None
    profile = recommend(probe(workspace))

    if track:
        try:
            caption_path = download_caption(track, folder)
            write_transcript_from_caption(caption_path, transcript_path)
            metadata["caption_file"] = caption_path.name
            metadata["caption_language"] = track.language
            metadata["caption_ext"] = track.ext
        except Exception as exc:
            if args.no_transcribe_fallback:
                raise
            print(f"Caption path failed, falling back to local transcription: {exc}", file=sys.stderr)
            transcript_source = "local_whisper"
            metadata = normalize_metadata(info, args.url, transcript_source=transcript_source)

    if transcript_source == "local_whisper":
        configured_model = configured_model_path(workspace, profile)
        model_override = args.model or configured_model
        ffmpeg_path = resolve_ffmpeg_path(workspace)
        video_path = download_video(
            args.url,
            folder,
            cookies_from_browser=args.cookies_from_browser,
            cookies=args.cookies.expanduser().resolve() if args.cookies else None,
            referer=args.referer,
            ffmpeg_location=ffmpeg_path,
        )
        transcript_path = transcribe_video(
            video_path,
            folder,
            profile,
            language=args.language,
            model_override=model_override,
            backend_override=args.backend,
            device_override=args.device,
            compute_type_override=args.compute_type,
        )
        metadata["video_file"] = video_path.name
        metadata["model_profile"] = profile.id
        metadata["model"] = model_override or profile.model
        metadata["model_source"] = profile.model
        if configured_model and not args.model:
            metadata["model_config"] = str(config_path(workspace))
        metadata["backend"] = args.backend or profile.backend
        metadata["device"] = args.device or profile.device
        metadata["compute_type"] = args.compute_type or profile.compute_type
        metadata["ffmpeg"] = ffmpeg_path

    metadata["transcript_file"] = transcript_path.name
    metadata_path = folder / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path = write_report(folder, metadata)
    if args.delete_video and transcript_source == "local_whisper":
        delete_video_files(folder, metadata)
    index = rebuild_index(workspace)

    payload = {
        "folder": str(folder),
        "metadata": str(metadata_path),
        "transcript": str(transcript_path),
        "report": str(report_path),
        "transcript_source": transcript_source,
        "caption": str(caption_path) if caption_path else None,
        "dashboard": str(workspace / "dashboard.html"),
        "report_count": len(index.get("reports", [])),
    }
    if getattr(args, "publish_notion", False):
        payload["notion"] = _publish_folder_to_notion(folder, workspace, args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.open:
        webbrowser.open(report_path.resolve().as_uri())
    return 0


def finalize(args: argparse.Namespace) -> int:
    folder = args.folder.expanduser().resolve()
    metadata = read_metadata(folder)
    if not metadata:
        raise SystemExit(f"Missing or invalid metadata.json in {folder}")
    summary_path = folder / SUMMARY_FILENAME
    if args.summary_file:
        shutil.copyfile(args.summary_file.expanduser().resolve(), summary_path)
    active_summary = summary_file_path(folder)
    if not active_summary.exists() or active_summary.stat().st_size == 0:
        raise SystemExit(f"Missing or empty {SUMMARY_FILENAME} in {folder}")
    report_path = write_report(folder, metadata)
    deleted = delete_video_files(folder, metadata)
    workspace = _workspace_for_folder(folder)
    rebuild_index(workspace)
    payload = {"report": str(report_path), "deleted_video_files": deleted}
    if getattr(args, "publish_notion", False):
        payload["notion"] = _publish_folder_to_notion(folder, workspace, args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.open:
        webbrowser.open(report_path.resolve().as_uri())
    return 0


def run_publish_notion(args: argparse.Namespace) -> int:
    folder = args.folder.expanduser().resolve()
    workspace = Path(args.workspace).expanduser().resolve() if args.workspace else _workspace_for_folder(folder)
    result = _publish_folder_to_notion(folder, workspace, args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def run_probe(args: argparse.Namespace) -> int:
    spec = probe(_workspace(args.workspace))
    print(to_json(spec), end="")
    return 0


def run_recommend(args: argparse.Namespace) -> int:
    spec = probe(_workspace(args.workspace))
    profile = recommend(spec)
    print(to_json({"spec": spec, "recommendation": profile}), end="")
    return 0


def run_matrix(_: argparse.Namespace) -> int:
    print(json.dumps(MODEL_MATRIX, ensure_ascii=False, indent=2) + "\n", end="")
    return 0


def run_install(args: argparse.Namespace) -> int:
    workspace = _workspace(args.workspace)
    spec = probe(workspace)
    profile = recommend(spec)
    target = model_cache_dir(workspace)
    commands = install_commands(profile, Path.cwd(), model_target=target)
    print(
        to_json(
            {
                "workspace": str(workspace),
                "config": str(config_path(workspace)),
                "recommendation": profile,
                "model_target": str(target),
                "commands": commands,
                "execute": args.execute,
            }
        ),
        end="",
    )
    if not args.execute:
        return 0
    for cmd in commands:
        subprocess.run(cmd, check=True)
    model_path = model_cache_path(workspace, profile.model) if should_cache_model(profile) and profile.model else None
    configured_spec = probe(workspace)
    written = write_config(workspace, configured_spec, profile, model_path=model_path)
    print(
        to_json(
            {
                "configured": str(written),
                "model_path": str(model_path) if model_path else None,
                "ffmpeg": configured_spec.ffmpeg,
            }
        ),
        end="",
    )
    return 0


def run_download_model(args: argparse.Namespace) -> int:
    target = args.target.expanduser().resolve() if args.target else None
    path = download_model(args.model, target)
    print(json.dumps({"model": args.model, "path": str(path)}, ensure_ascii=False, indent=2))
    return 0


def run_rebuild_index(args: argparse.Namespace) -> int:
    workspace = _workspace(args.workspace)
    payload = rebuild_index(workspace)
    print(json.dumps({"dashboard": str(workspace / "dashboard.html"), "reports": len(payload["reports"])}, indent=2))
    return 0


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, workspace: Path, **kwargs: Any) -> None:
        self.workspace = workspace
        super().__init__(*args, directory=str(workspace), **kwargs)

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html", "/dashboard.html"}:
            rebuild_index(self.workspace)
            self.path = "/dashboard.html"
        return super().do_GET()

    def log_message(self, format: str, *args: Any) -> None:
        print(f"{self.address_string()} - {format % args}", file=sys.stderr)


def run_serve(args: argparse.Namespace) -> int:
    workspace = _workspace(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    rebuild_index(workspace)
    handler = functools.partial(DashboardHandler, workspace=workspace)
    server = HTTPServer((args.host, args.port), handler)
    host, port = server.server_address
    url = f"http://{host}:{port}/"
    print(f"Serving video report dashboard at {url}")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ytlt", description="Caption-first local video transcription toolkit.")
    sub = parser.add_subparsers(dest="command", required=True)

    probe_parser = sub.add_parser("probe", help="Inspect local machine specs.")
    probe_parser.add_argument("--workspace")
    probe_parser.set_defaults(func=run_probe)

    recommend_parser = sub.add_parser("recommend", help="Recommend a local transcription profile.")
    recommend_parser.add_argument("--workspace")
    recommend_parser.set_defaults(func=run_recommend)

    matrix_parser = sub.add_parser("matrix", help="Print the model selection matrix.")
    matrix_parser.set_defaults(func=run_matrix)

    install_parser = sub.add_parser("install", help="Print or execute the recommended install plan.")
    install_parser.add_argument("--workspace")
    install_parser.add_argument("--dry-run", action="store_true", help="Print the install plan without running it.")
    install_parser.add_argument("--execute", action="store_true", help="Run the printed commands.")
    install_parser.set_defaults(func=run_install)

    setup_parser = sub.add_parser("setup", help="Configure backend and download the hardware-recommended model.")
    setup_parser.add_argument("--workspace")
    setup_parser.add_argument("--dry-run", action="store_true", help="Print the setup plan without running it.")
    setup_parser.add_argument("--execute", action="store_true", help="Run setup and write workspace config.json.")
    setup_parser.set_defaults(func=run_install)

    model_parser = sub.add_parser("download-model", help="Download a Hugging Face model snapshot.")
    model_parser.add_argument("model")
    model_parser.add_argument("--target", type=Path)
    model_parser.set_defaults(func=run_download_model)

    process_parser = sub.add_parser("process", help="Process one video URL.")
    process_parser.add_argument("url")
    process_parser.add_argument("--workspace")
    process_parser.add_argument("--output-root")
    process_parser.add_argument("--language")
    process_parser.add_argument("--force-transcribe", action="store_true")
    process_parser.add_argument("--no-auto-subs", action="store_true")
    process_parser.add_argument("--no-transcribe-fallback", action="store_true")
    process_parser.add_argument("--backend", choices=["faster-whisper", "mlx"])
    process_parser.add_argument("--model")
    process_parser.add_argument("--device")
    process_parser.add_argument("--compute-type")
    process_parser.add_argument("--cookies-from-browser")
    process_parser.add_argument("--cookies", type=Path)
    process_parser.add_argument("--referer")
    process_parser.add_argument("--delete-video", action=argparse.BooleanOptionalAction, default=True)
    process_parser.add_argument("--open", action="store_true")
    _add_notion_options(process_parser)
    process_parser.set_defaults(func=process_url)

    finalize_parser = sub.add_parser("finalize", help="Render final report.html after summary.md is written.")
    finalize_parser.add_argument("folder", type=Path)
    finalize_parser.add_argument("--summary-file", type=Path)
    finalize_parser.add_argument("--open", action="store_true")
    _add_notion_options(finalize_parser)
    finalize_parser.set_defaults(func=finalize)

    notion_parser = sub.add_parser("publish-notion", help="Publish or update an existing processed report in Notion.")
    notion_parser.add_argument("folder", type=Path)
    notion_parser.add_argument("--workspace")
    _add_notion_options(notion_parser, include_publish_flag=False)
    notion_parser.set_defaults(func=run_publish_notion)

    rebuild_parser = sub.add_parser("rebuild-index", help="Rebuild index.json and dashboard.html from past reports.")
    rebuild_parser.add_argument("--workspace")
    rebuild_parser.set_defaults(func=run_rebuild_index)

    serve_parser = sub.add_parser("serve", help="Serve the local report dashboard.")
    serve_parser.add_argument("--workspace")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8765)
    serve_parser.add_argument("--open", action="store_true")
    serve_parser.set_defaults(func=run_serve)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
