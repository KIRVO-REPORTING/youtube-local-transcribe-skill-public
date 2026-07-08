# Security Policy

## Reporting a Vulnerability

Please report security issues privately through GitHub's private vulnerability reporting if it is enabled for this repository. If private reporting is not available, open a minimal issue asking for a maintainer contact path without including exploit details.

## Sensitive Data

video-to-notes can process browser cookies, video metadata, transcripts, summaries, and optional Notion or Obsidian publishing credentials. Do not commit:

- Browser cookie exports
- Notion integration tokens
- Private transcripts
- Downloaded videos
- Local workspace output

## Supported Versions

Security fixes are currently applied to the latest `main` branch and the latest public release.
