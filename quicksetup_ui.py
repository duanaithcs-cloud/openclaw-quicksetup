import json
import subprocess
import threading
import urllib.error
import urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "openclaw.bootstrap.json"
INSTALLER = ROOT / "install_v2.py"


def http_json(url, headers=None, timeout=12):
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8", errors="replace")
    return json.loads(body)


def deep_get(d, path, default=""):
    cur = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur


def build_config(values):
    telegram_enabled = bool(values["telegram_token"].strip())
    zalo_enabled = bool(values["zalo_token"].strip())

    cfg = {
        "models": {
            "mode": "merge",
            "providers": {
                "proxypal": {
                    "baseUrl": values["proxypal_base"].strip() or "http://localhost:8317/v1",
                    "apiKey": values["proxypal_key"].strip() or "proxypal-local",
                    "api": "openai-completions",
                    "models": [
                        {"id": "gpt-5.3-codex", "name": "GPT-5.3 Codex (ProxyPal)"},
                        {"id": "gpt-5.3-codex-spark", "name": "GPT-5.3 Codex Spark (ProxyPal)"},
                    ],
                }
            },
        },
        "agents": {
            "defaults": {
                "model": {
                    "primary": "proxypal/gpt-5.3-codex",
                    "fallbacks": ["openai-codex/gpt-5.3-codex"],
                },
                "models": {
                    "proxypal/gpt-5.3-codex": {"params": {"transport": "sse"}},
                    "proxypal/gpt-5.3-codex-spark": {},
                    "openai-codex/gpt-5.3-codex": {},
                },
            }
        },
        "channels": {},
        "plugins": {"entries": {}},
    }

    if telegram_enabled:
        allow = values["telegram_allow"].strip()
        cfg["channels"]["telegram"] = {
            "enabled": True,
            "botToken": values["telegram_token"].strip(),
            "dmPolicy": "allowlist",
            "allowFrom": [allow] if allow else [],
            "groupPolicy": "allowlist",
            "groupAllowFrom": [allow] if allow else [],
            "streaming": "off",
            "timeoutSeconds": 45,
            "network": {"autoSelectFamily": True, "dnsResultOrder": "ipv4first"},
        }
        cfg["plugins"]["entries"]["telegram"] = {"enabled": True}

    if zalo_enabled:
        allow_zalo = values["zalo_allow"].strip()
        cfg["channels"]["zalo"] = {
            "enabled": True,
            "botToken": values["zalo_token"].strip(),
            "dmPolicy": "allowlist",
            "allowFrom": [allow_zalo] if allow_zalo else [],
            "groupPolicy": "allowlist",
            "groupAllowFrom": [allow_zalo] if allow_zalo else [],
        }
        cfg["plugins"]["entries"]["zalo"] = {"enabled": True}

    return cfg


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenClaw QuickSetup v3 - Cài đặt dễ cho người mới")
        self.root.geometry("980x760")

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        self.entries = {}
        self.status_vars = {
            "telegram": tk.StringVar(value="Telegram: chưa test"),
            "zalo": tk.StringVar(value="Zalo: chưa test"),
            "proxypal": tk.StringVar(value="ProxyPal: chưa test"),
        }

        self._build_ui()
        self._load_existing_if_any()

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=14)
        outer.pack(fill="both", expand=True)

        title = ttk.Label(
            outer,
            text="OpenClaw QuickSetup v3 (Telegram + Zalo + ProxyPal)",
            font=("Segoe UI", 14, "bold"),
        )
        title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        subtitle = ttk.Label(
            outer,
            text="Workflow 1-2-3: Nhập thông tin -> Test kết nối -> Tạo file mồi / Cài đặt ngay",
            foreground="#555",
        )
        subtitle.grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 12))

        card = ttk.LabelFrame(outer, text="Bước 1 - Nhập thông tin", padding=12)
        card.grid(row=2, column=0, columnspan=3, sticky="nsew")

        fields = [
            ("Telegram Bot Token", "telegram_token", True),
            ("Telegram User ID (allowFrom)", "telegram_allow", False),
            ("Zalo Bot Token (tuỳ chọn)", "zalo_token", True),
            ("Zalo User ID (allowFrom)", "zalo_allow", False),
            ("ProxyPal Base URL", "proxypal_base", False),
            ("ProxyPal API Key", "proxypal_key", True),
        ]
        defaults = {
            "proxypal_base": "http://localhost:8317/v1",
            "proxypal_key": "proxypal-local",
        }

        for i, (label, key, secret) in enumerate(fields):
            ttk.Label(card, text=label).grid(row=i, column=0, sticky="w", pady=6)
            ent = ttk.Entry(card, width=82, show="*" if secret else "")
            ent.grid(row=i, column=1, sticky="ew", padx=(10, 0), pady=6)
            if key in defaults:
                ent.insert(0, defaults[key])
            self.entries[key] = ent

        card.columnconfigure(1, weight=1)

        actions = ttk.LabelFrame(outer, text="Bước 2 - Test kết nối", padding=12)
        actions.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=(10, 0))

        ttk.Button(actions, text="Test Telegram", command=self.test_telegram).grid(row=0, column=0, padx=(0, 8), pady=2)
        ttk.Button(actions, text="Test Zalo", command=self.test_zalo).grid(row=0, column=1, padx=(0, 8), pady=2)
        ttk.Button(actions, text="Test ProxyPal", command=self.test_proxypal).grid(row=0, column=2, padx=(0, 8), pady=2)
        ttk.Button(actions, text="Test tất cả", command=self.test_all).grid(row=0, column=3, pady=2)

        self.lbl_tg = ttk.Label(actions, textvariable=self.status_vars["telegram"])
        self.lbl_zl = ttk.Label(actions, textvariable=self.status_vars["zalo"])
        self.lbl_pp = ttk.Label(actions, textvariable=self.status_vars["proxypal"])
        self.lbl_tg.grid(row=1, column=0, columnspan=4, sticky="w", pady=(8, 2))
        self.lbl_zl.grid(row=2, column=0, columnspan=4, sticky="w", pady=2)
        self.lbl_pp.grid(row=3, column=0, columnspan=4, sticky="w", pady=2)

        install = ttk.LabelFrame(outer, text="Bước 3 - Tạo file mồi / Cài đặt", padding=12)
        install.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=(10, 0))

        ttk.Button(install, text="Tạo file mồi cấu hình", command=self.save_bootstrap).grid(row=0, column=0, padx=(0, 8), sticky="w")
        ttk.Button(install, text="Tạo + Cài đặt ngay (v2)", command=self.install_now).grid(row=0, column=1, sticky="w")

        self.output_path_var = tk.StringVar(value=f"File mồi: {OUT_FILE}")
        ttk.Label(install, textvariable=self.output_path_var, foreground="#555").grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        note = ttk.Label(
            outer,
            text=(
                "Nguồn token: Telegram @BotFather | Zalo bot.zaloplatforms.com\n"
                "Khuyến nghị cho người mới: chạy Telegram + ProxyPal trước, bật Zalo sau."
            ),
            foreground="#555",
        )
        note.grid(row=5, column=0, columnspan=3, sticky="w", pady=(10, 8))

        ttk.Label(outer, text="Log:").grid(row=6, column=0, sticky="w")
        self.log = tk.Text(outer, height=14, wrap="word")
        self.log.grid(row=7, column=0, columnspan=3, sticky="nsew", pady=(4, 0))

        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(7, weight=1)

    def _append_log(self, text):
        self.log.insert("end", text + "\n")
        self.log.see("end")

    def _set_status(self, key, ok, text):
        self.status_vars[key].set(text)
        widget = {"telegram": self.lbl_tg, "zalo": self.lbl_zl, "proxypal": self.lbl_pp}[key]
        if ok is True:
            widget.configure(foreground="#0a7f2e")
        elif ok is False:
            widget.configure(foreground="#b00020")
        else:
            widget.configure(foreground="#7a5a00")

    def _validate_id_if_present(self, value, name):
        value = value.strip()
        if value and not value.isdigit():
            raise ValueError(f"{name} phải là số (numeric ID).")

    def _collect_values(self):
        vals = {k: e.get() for k, e in self.entries.items()}
        self._validate_id_if_present(vals.get("telegram_allow", ""), "Telegram User ID")
        self._validate_id_if_present(vals.get("zalo_allow", ""), "Zalo User ID")
        if not vals["telegram_token"].strip() and not vals["zalo_token"].strip():
            raise ValueError("Cần nhập ít nhất Telegram token hoặc Zalo token.")
        return vals

    def _load_existing_if_any(self):
        if not OUT_FILE.exists():
            return
        try:
            data = json.loads(OUT_FILE.read_text(encoding="utf-8"))
            self.entries["telegram_token"].delete(0, "end")
            self.entries["telegram_token"].insert(0, deep_get(data, ["channels", "telegram", "botToken"], ""))
            self.entries["telegram_allow"].delete(0, "end")
            self.entries["telegram_allow"].insert(0, (deep_get(data, ["channels", "telegram", "allowFrom"], [""]) or [""])[0])

            self.entries["zalo_token"].delete(0, "end")
            self.entries["zalo_token"].insert(0, deep_get(data, ["channels", "zalo", "botToken"], ""))
            self.entries["zalo_allow"].delete(0, "end")
            self.entries["zalo_allow"].insert(0, (deep_get(data, ["channels", "zalo", "allowFrom"], [""]) or [""])[0])

            self.entries["proxypal_base"].delete(0, "end")
            self.entries["proxypal_base"].insert(0, deep_get(data, ["models", "providers", "proxypal", "baseUrl"], "http://localhost:8317/v1"))
            self.entries["proxypal_key"].delete(0, "end")
            self.entries["proxypal_key"].insert(0, deep_get(data, ["models", "providers", "proxypal", "apiKey"], "proxypal-local"))
            self._append_log(f"[INFO] Đã nạp sẵn dữ liệu từ {OUT_FILE}")
        except Exception as e:
            self._append_log(f"[WARN] Không nạp được bootstrap cũ: {e}")

    def test_telegram(self):
        token = self.entries["telegram_token"].get().strip()
        if not token:
            self._set_status("telegram", None, "Telegram: chưa nhập token")
            self._append_log("[Telegram] Chưa nhập token.")
            return
        url = f"https://api.telegram.org/bot{token}/getMe"
        try:
            data = http_json(url)
            if data.get("ok"):
                uname = data.get("result", {}).get("username", "unknown")
                self._set_status("telegram", True, f"Telegram: PASS (@{uname})")
                self._append_log(f"[Telegram] PASS - @{uname}")
            else:
                self._set_status("telegram", False, "Telegram: FAIL (token invalid)")
                self._append_log(f"[Telegram] FAIL - {data}")
        except Exception as e:
            self._set_status("telegram", False, "Telegram: FAIL (network/token)")
            self._append_log(f"[Telegram] ERROR - {e}")

    def test_zalo(self):
        token = self.entries["zalo_token"].get().strip()
        if not token:
            self._set_status("zalo", None, "Zalo: chưa nhập token")
            self._append_log("[Zalo] Chưa nhập token.")
            return
        url = "https://openapi.zalo.me/v2.0/oa/getoa"
        headers = {"access_token": token}
        try:
            data = http_json(url, headers=headers)
            err = data.get("error")
            if err in (0, None):
                name = data.get("data", {}).get("name", "OA")
                self._set_status("zalo", True, f"Zalo: PASS ({name})")
                self._append_log(f"[Zalo] PASS - {name}")
            else:
                self._set_status("zalo", False, f"Zalo: FAIL (error={err})")
                self._append_log(f"[Zalo] FAIL - {data}")
        except urllib.error.HTTPError as e:
            self._set_status("zalo", False, f"Zalo: FAIL (HTTP {e.code})")
            self._append_log(f"[Zalo] HTTP ERROR {e.code} - {e.reason}")
        except Exception as e:
            self._set_status("zalo", False, "Zalo: FAIL (network/token)")
            self._append_log(f"[Zalo] ERROR - {e}")

    def test_proxypal(self):
        base = self.entries["proxypal_base"].get().strip() or "http://localhost:8317/v1"
        key = self.entries["proxypal_key"].get().strip() or "proxypal-local"
        url = base.rstrip("/") + "/models"
        headers = {"Authorization": f"Bearer {key}"}
        try:
            data = http_json(url, headers=headers)
            count = len(data.get("data", [])) if isinstance(data, dict) else 0
            if count > 0:
                self._set_status("proxypal", True, f"ProxyPal: PASS ({count} models)")
                self._append_log(f"[ProxyPal] PASS - models={count}")
            else:
                self._set_status("proxypal", False, "ProxyPal: FAIL (no models)")
                self._append_log(f"[ProxyPal] FAIL - {data}")
        except urllib.error.HTTPError as e:
            self._set_status("proxypal", False, f"ProxyPal: FAIL (HTTP {e.code})")
            self._append_log(f"[ProxyPal] HTTP ERROR {e.code} - {e.reason}")
        except Exception as e:
            self._set_status("proxypal", False, "ProxyPal: FAIL (network/key)")
            self._append_log(f"[ProxyPal] ERROR - {e}")

    def test_all(self):
        self.test_telegram()
        self.test_zalo()
        self.test_proxypal()

    def save_bootstrap(self):
        try:
            values = self._collect_values()
        except Exception as e:
            messagebox.showerror("Thiếu dữ liệu", str(e))
            return

        cfg = build_config(values)
        OUT_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        self.output_path_var.set(f"File mồi: {OUT_FILE}")
        self._append_log(f"[OK] Đã tạo file mồi: {OUT_FILE}")
        messagebox.showinfo("Đã tạo file mồi", f"Đã tạo:\n{OUT_FILE}")

    def install_now(self):
        self.save_bootstrap()
        if not INSTALLER.exists():
            messagebox.showerror("Thiếu installer", f"Không tìm thấy: {INSTALLER}")
            return

        def _run():
            self._append_log("[RUN] Đang chạy installer v2...")
            p = subprocess.run(["python", str(INSTALLER)], capture_output=True, text=True)
            if p.stdout:
                self._append_log(p.stdout.strip())
            if p.stderr:
                self._append_log(p.stderr.strip())
            if p.returncode == 0:
                self._append_log("[OK] Cài đặt hoàn tất.")
                messagebox.showinfo("Hoàn tất", "Cài đặt hoàn tất. Xem log/report để kiểm tra.")
            else:
                self._append_log(f"[ERROR] Installer trả mã {p.returncode}")
                messagebox.showerror("Lỗi", "Cài đặt thất bại. Xem log để biết chi tiết.")

        threading.Thread(target=_run, daemon=True).start()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
