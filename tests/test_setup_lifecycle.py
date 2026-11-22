"""Windows lifecycle tests using a throwaway setup identity."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "installer"))
import build_installer as bi


@pytest.mark.skipif(not bi.CSC.is_file(), reason="Windows installer integration")
def test_scratch_install_replace_update_and_remove(tmp_path):
    """Give the scratch stub unique registry and shortcut names before executing it."""
    import subprocess
    import uuid
    import winreg
    import zipfile

    suffix = uuid.uuid4().hex
    source = (bi.HERE / "Setup.cs").read_text(encoding="utf-8")
    source = source.replace('Uninstall\\MyTranscribeMedical";', f'Uninstall\\MyTranscribeTest{suffix}";')
    source = source.replace('AppName = "MyTranscribe Medical";', f'AppName = "MyTranscribeTest{suffix}";')
    assert f'Uninstall\\MyTranscribeTest{suffix}";' in source and 'Uninstall\\MyTranscribeMedical";' not in source
    scratch = tmp_path / "Scratch.cs"
    scratch.write_text(source, encoding="utf-8")
    def compile_scratch(cmd, check):
        subprocess.run([*cmd[:-1], str(scratch)], check=check)
    stub = bi.compile_stub(tmp_path, bi.REPO / "src/assets/mytranscribe.ico", run=compile_scratch)
    dest = tmp_path / "app"
    backup = tmp_path / "app.backup-mine"  # looks like a setup leftover, but is not one
    backup.mkdir()
    marker = backup / "keep.txt"
    marker.write_text("unrelated")
    key = rf"Software\Microsoft\Windows\CurrentVersion\Uninstall\MyTranscribeTest{suffix}"

    def run_fixture(version, kind="full"):
        payload = tmp_path / "fixture.zip"
        with zipfile.ZipFile(payload, "w") as writer:
            writer.writestr("src/version.txt", version)
            writer.writestr("build_info.json", json.dumps(dict(version=version, device="any", kind=kind, python="3.11")))
            if kind == "full":
                writer.writestr("python/python.exe", b"fixture")
        setup = bi.join(stub, payload, tmp_path, version)
        return subprocess.run([setup, "/S", "/noshortcuts", f"/D={dest}"], timeout=30).returncode

    try:
        dest.mkdir()
        user_file = dest / "keep.txt"
        user_file.write_text("unrelated")
        assert run_fixture("occupied") != 0 and user_file.read_text() == "unrelated"
        user_file.unlink()
        assert run_fixture("1") == 0
        assert run_fixture("2") == 0
        # A setup stopped part-way leaves a partly unpacked copy, and may have set the installed
        # copy aside just before the swap: the next setup puts that copy back and removes the rest.
        leftovers = lambda: list(tmp_path.glob("app.stage-*")) + list(tmp_path.glob("app.backup-" + "?" * 32))
        (tmp_path / f"app.stage-{uuid.uuid4().hex}" / "src").mkdir(parents=True)
        dest.rename(tmp_path / f"app.backup-{uuid.uuid4().hex}")
        assert run_fixture("3", "update") == 0 and not leftovers()
        assert (dest / "src/version.txt").read_text() == "3"
        # An open installed file prevents replacement; the prior version must survive.
        with (dest / "build_info.json").open("rb"):
            assert run_fixture("4", "update") != 0
        assert (dest / "src/version.txt").read_text() == "3"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as handle:
            assert winreg.QueryValueEx(handle, "DisplayVersion")[0] == "3"
        # An update stopped after setting a file aside and before putting the new one in.
        aside = tmp_path / f"app.backup-{uuid.uuid4().hex}"
        aside.mkdir()
        (aside / "selftest.py").write_text("set aside")
        assert run_fixture("5", "update") == 0 and not leftovers()
        assert (dest / "selftest.py").read_text() == "set aside"
        (tmp_path / f"app.stage-{uuid.uuid4().hex}").mkdir()
        # Use a scratch helper from outside the target so the removal runs synchronously.
        helper = tmp_path / "scratch-remove.exe"
        helper.write_bytes(stub.read_bytes())
        subprocess.run([helper, "/uninstall", "/S", f"/from={dest}"], check=True, timeout=30)
        assert not dest.exists() and not leftovers() and marker.read_text() == "unrelated"
    finally:
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key)
        except FileNotFoundError:
            pass
