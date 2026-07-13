# Obsidian Publishing

Read this reference only when the user requests Obsidian or `preferences.output_environment` is `obsidian`.

Set `OBSIDIAN_VAULT_PATH` or pass `--obsidian-vault`. Optional settings are `OBSIDIAN_REPORTS_DIR` and `OBSIDIAN_INDEX_NOTE`.

After `summary.md` and `tags.json` are ready, publish during finalization:

```bash
video-to-notes finalize "VIDEO_FOLDER" --environment obsidian
```

For an already finalized report or a workspace sync:

```bash
video-to-notes publish-obsidian "VIDEO_FOLDER"
video-to-notes sync-obsidian
```

The note should include source metadata, timestamp-linked summary sections, local report path, and the full transcript unless `--obsidian-no-transcript` is requested. YAML `tags` must come only from `tags.json`.

Return `obsidian_note_path` or `obsidian_note_uri` and the local report path. Later publishes should update the same note. If no vault is configured, keep and return the local report rather than treating the whole workflow as failed.
