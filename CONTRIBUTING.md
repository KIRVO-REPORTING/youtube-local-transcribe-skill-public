# Contributing

Thanks for considering a contribution to video-to-notes.

## Development Setup

```bash
git clone https://github.com/KIRVO-REPORTING/video-to-notes.git
cd video-to-notes
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
```

## Tests

Run the test suite before opening a pull request:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m compileall ytlt
```

## Pull Requests

- Keep changes focused.
- Add or update tests when behavior changes.
- Update README or docs when user-facing commands or workflows change.
- Do not commit generated local workspaces, transcripts, downloaded videos, credentials, or browser cookies.
