# Developing MyTranscribe Medical

## Run from source

Windows 11, 64-bit Python 3.11.

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe src\gui_med.py
```

`MyTranscribe.bat` starts the same without a console window.

- **NVIDIA card:** `requirements.txt` installs NVIDIA's cuBLAS into `.venv`, and the app finds it
  there (`fw_engine.register_cuda_dll_dirs`). No CUDA toolkit is needed.
- **Models** are downloaded from Hugging Face on first start, after asking: large-v3 (3 GB) with
  an NVIDIA card, small.en (0.5 GB) without. They go to `%USERPROFILE%\.cache\huggingface`; set
  `HF_HUB_CACHE` to keep them elsewhere.
- **Behind security software or a proxy that re-signs secure connections,** pip older than 24.2
  needs `pip install --use-feature=truststore -r requirements.txt`. The app itself checks
  downloads against Windows' certificate store (`truststore`).
- **Settings and log:** `%APPDATA%\MyTranscribe\settings.json` and
  `%LOCALAPPDATA%\MyTranscribe\mytranscribe.log`. Point `APPDATA` and `LOCALAPPDATA` at other
  folders to start as on a fresh PC.
- **Overrides** (`hw_profile.choose_config`): `MYTRANSCRIBE_DEVICE=cpu`, `MYTRANSCRIBE_MODEL`,
  `MYTRANSCRIBE_COMPUTE_TYPE`, `MYTRANSCRIBE_CPU_THREADS`.

## Tests

```powershell
.venv\Scripts\python.exe -m pytest -q tests
```

About 630 tests in 40 seconds, with no microphone, graphics card or model: `tests/fakes.py`
stands in for them. The GUI tests open real Qt windows. `test_phi_clipboard::test_copy_text_roundtrip`
fails while another program holds the clipboard.

## How it fits together

Microphone → `chunked_transcriber` (pieces of about 30 s while you talk, the rest at Stop) →
`fw_engine` (faster-whisper) → the text layer → `phi_clipboard` (copy, paste) or `live_insert`
(typing while you dictate).

| Area | Modules |
|---|---|
| Window and settings | `gui_med` (the app), `gui_qt` (its base window), `options_dialog`, `setup_wizard`, `log_window`, `settings`, `triggers` (keys and mouse buttons), `app_log`, `qt_gc` |
| Audio | `audio_devices`, `mic_ready` (microphone kept open, with pre-roll), `mic_check` (level check), `sound_utils` (chimes) |
| Recognition | `engines` (recognisers, bundled models, the download question), `hw_profile` (model, device and compute type for this PC), `fw_engine`, `chunked_transcriber`, `pause_flow` (pause-aware dictation) |
| Text | `text_fixes`, `spoken_numbers`, `dictation_fixes`, `voice_commands` (spoken formatting and punctuation), `drug_names`, `classical_terms`, `vocab` (topic prompts), `vocab_correct`, `prompt_loader` |
| Languages | `lang_packs`, `lang_commands` (Spanish and French, experimental) |
| Optional | `medasr_engine`, `onnx_engine`: other recognisers, shown only when their packages are installed (setup is in the development repository). `transcriber_v12`: the original app's transcriber, kept for `gui_qt`'s base class. |

Data: `src/vocab/` (drug names, medical terms, corrections), `src/prompts/`, `src/assets/`.

## Rules that keep it trustworthy

- **large-v3 on a graphics card is the validated path.** What it works from (model revision,
  beams, prompt, corrections, windows) changes only with the full validation set behind it.
- **Processor-only tuning stays on the processor:** small.en's settings, short windows and the
  classical-term fixer are gated on `device == "cpu"` (`fw_engine`,
  `classical_terms.GRAPHICS_CARD_TOO`). Test that the graphics-card path is unchanged.
- **Fixers never invent:** a word is changed only to a real entry, and only where the sentence
  says one belongs (`test_drug_names.py`, `test_classical_terms.py`).
- **Nothing leaves the PC:** the model hub stays offline except for one download the user agreed
  to (`engines.build(allow_download=True)`); audio is never written to disk; the log never holds
  dictated text.
- **Qt objects live and die on the GUI thread:** worker threads emit signals, and Python's
  garbage collector runs on the GUI thread only (`qt_gc`); with PySide6, anything else can abort
  the process.
- **A missing model is asked for, never assumed:** declined or failed downloads fall back to the
  installer's small.en (`engines.fallback_model`).

## The installer

[installer/README.md](../installer/README.md).

## Releasing

1. Tests pass.
2. Build `--every-pc` from a clean checkout (see the installer guide).
3. Install it on a test PC or profile, and run its `selftest.py` with and without the NVIDIA card
   (`CUDA_VISIBLE_DEVICES=-1` hides it).
4. Publish the installer with its SHA256.

If the repository moves, update the address in `installer/LICENSE-NOTICE.txt` (the installer
shows it) and in the README.

## History

This repository starts from release 2026.11.22. The development history (every measurement
round, the trial and validation tools, the synthetic voice sets, the original Linux app) is in
the [development repository](https://github.com/seanmichaelmcgee/MyTranscribe/tree/v2026.11.22).
