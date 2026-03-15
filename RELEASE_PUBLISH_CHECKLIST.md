# Release Publish Checklist (v1.0.0)

Repo: https://github.com/duanaithcs-cloud/openclaw-quicksetup
Tag: `v1.0.0`

## 1) Mở trang tạo release
- https://github.com/duanaithcs-cloud/openclaw-quicksetup/releases/new?tag=v1.0.0

## 2) Điền thông tin
- **Release title:** `OpenClaw QuickSetup v1.0.0`
- **Description:** copy nội dung từ `RELEASE_NOTES_v1.0.0.md`

## 3) (Khuyến nghị) Upload file zip nhẹ
Tại máy local chạy:
```bash
python pack_release.py
```
File tạo ra:
- `output/release/openclaw-quicksetup-lite.zip`

Sau đó kéo thả file zip này vào phần **Attach binaries** trên trang release.

## 4) Publish
- Bấm **Publish release**.

---

## Mẫu nội dung release (copy/paste)

OpenClaw QuickSetup v1.0.0 – bản cài nhanh cho người mới (không chuyên kỹ thuật).

### Điểm nổi bật
- Workflow 1-2-3 rõ ràng: Nhập thông tin -> Test -> Cài đặt.
- Tích hợp Telegram + Zalo + ProxyPal trong một UI.
- Có kiểm tra PASS/FAIL trước khi áp cấu hình.
- Có one-click installer với backup + merge + restart + self-check.
- Có script đóng gói lite để chia sẻ nhanh.

### Cách chạy nhanh
1. Mở `launchers/46_OpenClaw_QuickSetup_UI.bat`
2. Nhập token + ID
3. Bấm `Test tất cả`
4. Bấm `Tạo + Cài đặt ngay (v2)`
