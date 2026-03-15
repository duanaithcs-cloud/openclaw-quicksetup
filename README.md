# OpenClaw QuickSetup v3 (Telegram + Zalo + ProxyPal)

> Version: **v1.1.0**  
> Audience: người mới, không chuyên kỹ thuật

Bộ cài đặt nhanh OpenClaw theo workflow 1-2-3: **Nhập thông tin -> Test kết nối -> Cài đặt**.


Mục tiêu: tạo **file mồi + giao diện cực dễ** để người mới cài OpenClaw trên máy mới nhanh nhất, có kiểm tra PASS/FAIL trước khi cài.

## 1) Cách dùng nhanh (workflow 1-2-3)

1. Cài OpenClaw trên máy mới.
2. Chạy launcher: `APPS/Launchers/46_OpenClaw_QuickSetup_UI.bat`
3. Trong UI làm theo 3 bước:
   - **Bước 1:** Nhập Telegram/Zalo/ProxyPal
   - **Bước 2:** Bấm **Test tất cả** để kiểm tra PASS/FAIL
   - **Bước 3:** Bấm **Tạo file mồi cấu hình** hoặc **Tạo + Cài đặt ngay (v2)**

File mồi được sinh tại: `APPS/Projects/46_OpenClaw_QuickSetup/output/openclaw.bootstrap.json`

## Cài đặt one-click v2 (khuyên dùng)

Sau khi đã tạo file mồi ở bước UI, chạy:
- `APPS/Launchers/46_OpenClaw_QuickSetup_Install_v2.bat`

Bản v2 sẽ tự động:
1. Backup `~/.openclaw/openclaw.json`
2. Merge file mồi vào config hiện tại
3. Cài plugin Zalo (best-effort) nếu bật Zalo
4. Restart Gateway
5. Chạy self-check và xuất báo cáo tại:
   - `APPS/Projects/46_OpenClaw_QuickSetup/output/install_report.md`

---

## 2) Các đường dẫn quan trọng

### Telegram
- Tạo bot token: https://t.me/BotFather
- Lấy user ID: nhắn bot của bạn rồi xem log OpenClaw hoặc dùng bot ID checker.

### Zalo
- Zalo Bot Platform: https://bot.zaloplatforms.com
- Lưu ý: cần cài plugin Zalo trước khi dùng:
  - `openclaw plugins install @openclaw/zalo`

### ProxyPal
- Base URL thường dùng: `http://localhost:8317/v1`
- API key local thường dùng: `proxypal-local`
- File cấu hình ProxyPal thường nằm ở:
  - `%APPDATA%\ProxyPal\config.json`

### OpenClaw
- File cấu hình chính: `%USERPROFILE%\.openclaw\openclaw.json`

---

## 3) Chiến lược triển khai hợp lý nhất (khuyên dùng)

### Phase A - Onboarding an toàn cho người mới
- Mặc định bật Telegram trước (ít lỗi nhất).
- ProxyPal để model chính.
- Zalo để tuỳ chọn (vì cần plugin + token riêng).
- DM policy: `allowlist` để kiểm soát truy cập.

### Phase B - Mở rộng sau khi chạy ổn
- Bật thêm Zalo.
- Thêm fallback model.
- Tối ưu retry/network cho Telegram.

=> Cách này giảm lỗi triển khai và giúp người mới thành công ngay lần đầu.

---

## 4) Bảo mật
- Không chia sẻ token/bot key công khai.
- Không commit file chứa token thật lên Git.
- Chỉ đưa file mẫu/token placeholder cho người dùng mới.

## 5) Đóng gói nhẹ để chia sẻ

Chạy:
```bash
python pack_release.py
```

Gói zip xuất ra:
- `output/release/openclaw-quicksetup-lite.zip`

Gói này chỉ gồm file cần thiết để người mới cài nhanh (UI, installer, launcher, README).

## 6) Chất lượng dự án
- Có `LICENSE` (MIT)
- Có `CONTRIBUTING.md`
- Có `SECURITY.md`
- Có GitHub Action CI kiểm tra compile Python (`.github/workflows/ci.yml`)
