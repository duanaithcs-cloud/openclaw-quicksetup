import json
import subprocess
import sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BOOTSTRAP = ROOT / "output" / "openclaw.bootstrap.json"
HOME = Path.home()
OPENCLAW_DIR = HOME / ".openclaw"
CFG_PATH = OPENCLAW_DIR / "openclaw.json"
BACKUP_DIR = OPENCLAW_DIR / "backups"
REPORT = ROOT / "output" / "install_report.md"


def deep_merge(base, patch):
    if not isinstance(base, dict) or not isinstance(patch, dict):
        return deepcopy(patch)
    out = deepcopy(base)
    for k, v in patch.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = deepcopy(v)
    return out


def run_cmd(args):
    p = subprocess.run(args, capture_output=True, text=True)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


def main():
    OPENCLAW_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    (ROOT / "output").mkdir(parents=True, exist_ok=True)

    if not BOOTSTRAP.exists():
        print(f"[ERROR] Chưa có file mồi: {BOOTSTRAP}")
        print("Hãy chạy quicksetup_ui.py trước để tạo bootstrap.")
        return 1

    bootstrap = json.loads(BOOTSTRAP.read_text(encoding="utf-8"))
    current = {}

    backup_path = None
    if CFG_PATH.exists():
        current = json.loads(CFG_PATH.read_text(encoding="utf-8"))
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"openclaw.json.before_quicksetup_v2_{ts}.bak"
        backup_path.write_text(CFG_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    merged = deep_merge(current, bootstrap)
    CFG_PATH.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("# OpenClaw QuickSetup v2 - Install Report")
    lines.append("")
    lines.append(f"- Time: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"- Bootstrap: `{BOOTSTRAP}`")
    lines.append(f"- Target config: `{CFG_PATH}`")
    if backup_path:
        lines.append(f"- Backup: `{backup_path}`")
    else:
        lines.append("- Backup: *(không có config cũ để backup)*")

    # Zalo plugin best-effort
    zalo_enabled = bool(merged.get("channels", {}).get("zalo", {}).get("enabled"))
    if zalo_enabled:
        code, out, err = run_cmd(["openclaw", "plugins", "install", "@openclaw/zalo"])
        lines.append("")
        lines.append("## Zalo plugin install")
        lines.append(f"- Exit code: `{code}`")
        if out:
            lines.append("```text")
            lines.append(out[:2500])
            lines.append("```")
        if err:
            lines.append("```text")
            lines.append(err[:1500])
            lines.append("```")

    # restart gateway
    code_r, out_r, err_r = run_cmd(["openclaw", "gateway", "restart"])
    lines.append("")
    lines.append("## Gateway restart")
    lines.append(f"- Exit code: `{code_r}`")
    if out_r:
        lines.append("```text")
        lines.append(out_r[:2500])
        lines.append("```")
    if err_r:
        lines.append("```text")
        lines.append(err_r[:1500])
        lines.append("```")

    # health checks
    checks = [
        ["openclaw", "status"],
        ["openclaw", "gateway", "status"],
    ]
    lines.append("")
    lines.append("## Self-check")
    for cmd in checks:
        code, out, err = run_cmd(cmd)
        lines.append(f"### {' '.join(cmd)}")
        lines.append(f"- Exit code: `{code}`")
        if out:
            lines.append("```text")
            lines.append(out[:2500])
            lines.append("```")
        if err:
            lines.append("```text")
            lines.append(err[:1500])
            lines.append("```")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] Đã áp dụng cấu hình. Report: {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
