# Changelog

## v1.0.0 - 2026-03-15

### Added
- QuickSetup UI v3 theo workflow 1-2-3 cho người mới.
- Test kết nối trực tiếp trong UI:
  - Telegram (Bot API getMe)
  - Zalo (OA endpoint best-effort)
  - ProxyPal (/v1/models)
- Nút **Tạo + Cài đặt ngay** ngay trong UI.
- Installer v2 tự động:
  - backup `~/.openclaw/openclaw.json`
  - merge bootstrap config
  - cài plugin Zalo (best-effort)
  - restart gateway
  - self-check + report
- Script đóng gói nhẹ `pack_release.py`.

### Notes
- Dành cho Windows + Python cài sẵn.
- Không commit dữ liệu output/token/secrets.
