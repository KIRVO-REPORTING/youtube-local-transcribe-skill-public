from __future__ import annotations

import datetime as dt
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .spec import InstallProfile, MachineSpec


CONFIG_FILENAME = "config.json"


def config_path(workspace: Path) -> Path:
    return workspace / CONFIG_FILENAME


def model_cache_dir(workspace: Path) -> Path:
    return workspace / "models"


def model_cache_path(workspace: Path, model: str) -> Path:
    return model_cache_dir(workspace) / model.replace("/", "__")


def read_config(workspace: Path) -> dict[str, Any] | None:
    path = config_path(workspace)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return None


def write_config(
    workspace: Path,
    spec: MachineSpec,
    profile: InstallProfile,
    *,
    model_path: Path | str | None = None,
) -> Path:
    workspace.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "workspace": str(workspace),
        "machine": asdict(spec),
        "profile": asdict(profile),
        "ffmpeg": {
            "path": spec.ffmpeg,
        },
        "model": {
            "source": profile.model,
            "path": str(model_path) if model_path else None,
        },
    }
    path = config_path(workspace)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def configured_model_path(workspace: Path, profile: InstallProfile) -> str | None:
    config = read_config(workspace)
    if not config:
        return None
    if (config.get("profile") or {}).get("id") != profile.id:
        return None
    model = config.get("model") or {}
    if model.get("source") != profile.model:
        return None
    path_value = model.get("path")
    if not path_value:
        return None
    path = Path(path_value).expanduser()
    return str(path) if path.exists() else None
