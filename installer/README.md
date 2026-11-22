# Windows installer

`build_installer.py` turns the app into a Windows 11 installer that brings its own Python, so
users install nothing else. Nothing is downloaded during a build: it packs the build PC's Python,
the packages the app imports, the app and the chosen speech model.

## Builds

| Build | Option | Size | For |
|---|---|---|---|
| **Every PC** (the one published) | `--every-pc` | 1.2 GB | any PC: small.en inside; with an NVIDIA card, large-v3 is downloaded after asking |
| Processor-only | (none) | 0.7 GB | PCs without an NVIDIA card |
| Graphics-card edition | `--gpu` | 3.8 GB | NVIDIA PCs, large-v3 inside; installs beside the others under its own name |

## Building

Needs Windows 11 (its .NET Framework 4.8 C# compiler builds the installer program), the
development environment from `requirements.txt`, and a faster-whisper model folder from Hugging
Face (for example `Systran/faster-whisper-small.en`). A `SOURCE.txt` in the model folder is copied
into the install's `THIRD-PARTY.txt`.

```powershell
.venv\Scripts\python.exe installer\build_installer.py --every-pc --model <folder>\faster-whisper-small.en --version 2026.11.22 --out <folder>
```

About a minute. Output: `MyTranscribe-Medical-Setup-<version>.exe`. Windows will not start a
program of 4 GiB or more, so a larger build comes as the program plus a `.data` file beside it.
Build a **full installer** whenever bundled dependencies change. An update package replaces the
app source, release metadata and uninstaller in a registered copy with the matching runtime.

The builder copies application files listed in [app-files.txt](app-files.txt). Update this list
when adding runtime source or assets. After assembling the executable, the builder checks its
source inventory and bytes, licence notice, bundled package versions and absence of Python caches.
Use a fresh build directory for a release.

## What the installer does

- **Windows 11 only** (build 22000 or later); on older Windows it says so and stops.
- **Licence page:** shows `LICENSE-NOTICE.txt` and installs only after "I accept".
- **Per user, no administrator rights:** `%LOCALAPPDATA%\Programs\MyTranscribe Medical`, desktop
  and Start-menu shortcuts, an entry in Settings → Apps. Updating keeps the user's settings.
- **Switches:** `/S` (silent; accepts the licence), `/D=<folder>`, `/noshortcuts`. Uninstall:
  `"<folder>\Uninstall MyTranscribe.exe" /uninstall [/S]`. Log: `%TEMP%\MyTranscribe-setup.log`.

## What goes in

- `python\`: a private Python 3.11, isolated by `python311._pth`.
- `python\Lib\site-packages\`: what the app imports, and what that needs. Qt is trimmed to QtCore,
  QtGui, QtWidgets, SVG and the Windows plugins. PyAV is replaced by a placeholder (the app never
  decodes audio files; its FFmpeg links GPL encoders). NVIDIA: cuBLAS only, the one NVIDIA library
  CTranslate2 loads for Whisper (cuDNN and NVRTC were measured as never loaded).
- `src\`, `models\`, `selftest.py`, `LICENSE-NOTICE.txt`, `THIRD-PARTY.txt` (every component,
  its licence and where its text is) and `licenses\` (the texts wheels leave out).

## Testing an installer

- **Self-test:** `<install>\python\python.exe <install>\selftest.py` checks imports, the hardware,
  the model and a decode; with an NVIDIA card it also checks that cuBLAS loads from the install.
- **Release checks:** exercise the final download on a disposable Windows profile or VM as a
  standard user, record a local antivirus result, and publish the SHA-256 of the exact file
  offered. If adding an Authenticode signature, check payload detection on the signed artifact:
  the current format reads a trailer at the end of the file.
- **Processor path on an NVIDIA PC:** set `CUDA_VISIBLE_DEVICES=-1`.
- **Do not test the real installer on a PC with a real install of the same build:** both use one
  Apps entry, and uninstalling a test copy removes it. Compile a copy of `Setup.cs` with another
  `RegKey` for tests.
