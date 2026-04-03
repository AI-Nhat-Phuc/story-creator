# SPEC — separate prod nonprod data

> **Status**: DRAFT
> **Phase**: SPEC
> **Date**: 2026-04-03

---

## Behavior

Hệ thống phân biệt hai môi trường dữ liệu dựa trên biến môi trường `APP_ENV`:

- `APP_ENV=production` → dùng database **prod** (bắt đầu trống)
- `APP_ENV=development` (hoặc không set) → dùng database **nonprod/dev**

Khi chạy trên **Vercel**:
- Nếu `MONGODB_URI` được set: dùng MongoDB với tên database khác nhau theo env
- Nếu không có `MONGODB_URI`: dùng TinyDB với đường dẫn file khác nhau theo env

Khi chạy **local**:
- Nếu `MONGODB_URI` được set: tương tự Vercel
- Nếu không: TinyDB với file khác nhau theo env

Dữ liệu **prod hiện tại được reset** (trống hoàn toàn) sau khi tách.

## API Contract

Không thay đổi API contract. Đây là infrastructure change — các endpoint giữ nguyên.

## Business Rules

1. `APP_ENV=production` → MongoDB DB name: `story_creator_prod` / TinyDB path: `story_creator_prod.db`
2. `APP_ENV=staging` → MongoDB DB name: `story_creator_staging` / TinyDB path: `story_creator_staging.db`
3. `APP_ENV=development` hoặc không set → MongoDB DB name: `story_creator_dev` / TinyDB path: `story_creator.db` (giữ nguyên để không break local dev)
4. `STORY_DB_PATH` env var vẫn override tất cả (ưu tiên cao nhất) — backward compatible
5. Prod data bắt đầu fresh: nếu đang dùng MongoDB, drop collection prod cũ (hoặc dùng db name mới `story_creator_prod` thay vì `story_creator` cũ)
6. Nonprod data (db name `story_creator` cũ hoặc `story_creator.db`) không bị xóa

## Edge Cases

- Nếu `APP_ENV` không hợp lệ (e.g. `APP_ENV=xyz`) → fallback về `development`, log warning
- Nếu MongoDB init fail ở prod → fallback TinyDB với đường dẫn prod tương ứng (hiện tại)
- Vercel luôn set `VERCEL=1`, nhưng `APP_ENV` phải được set **thủ công** trong Vercel dashboard

## Out of Scope

- Migration data từ env này sang env khác
- UI để chọn environment
- Multi-tenant hay per-user database isolation
- Xóa data MongoDB production cũ (db name `story_creator`) — giữ nguyên, chỉ không dùng nữa
