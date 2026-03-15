import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
REL = OUT / "release"
PKG = REL / "openclaw-quicksetup-lite"

KEEP = [
    "quicksetup_ui.py",
    "install_v2.py",
    "README.md",
    "../..\\Launchers\\46_OpenClaw_QuickSetup_UI.bat",
    "../..\\Launchers\\46_OpenClaw_QuickSetup_Install_v2.bat",
]


def main():
    REL.mkdir(parents=True, exist_ok=True)
    if PKG.exists():
        shutil.rmtree(PKG)
    PKG.mkdir(parents=True, exist_ok=True)

    for rel in KEEP:
        src = (ROOT / rel).resolve()
        if not src.exists():
            continue
        dest = PKG / src.name
        shutil.copy2(src, dest)

    zip_base = REL / "openclaw-quicksetup-lite"
    if (zip_base.with_suffix('.zip')).exists():
        (zip_base.with_suffix('.zip')).unlink()
    shutil.make_archive(str(zip_base), "zip", PKG)
    print(str(zip_base.with_suffix('.zip')))


if __name__ == "__main__":
    main()
