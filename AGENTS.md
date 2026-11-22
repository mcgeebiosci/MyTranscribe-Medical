# Notes for coding agents

- Read [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) first, especially "Rules that keep it trustworthy".
- Run `.venv\Scripts\python.exe -m pytest -q tests` before every commit; keep one concern per commit.
- Never commit audio, transcripts, patient or personal data, model weights or build output.
- Changes to what large-v3 works from need the full validation set; processor-only tuning stays
  gated on `device == "cpu"`.
- The development history, trial and validation tools are in
  https://github.com/seanmichaelmcgee/MyTranscribe (tag v2026.11.22): reuse them from there.
