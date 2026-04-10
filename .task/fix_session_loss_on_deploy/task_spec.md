# SPEC: Fix Session Loss on Deploy

> **Status**: APPROVED
> **Phase**: DESIGN
> **Date**: 2026-04-10

---

## Behavior

Khi Vercel triển khai phiên bản mới, serverless function cold-start có thể làm
request `/api/auth/verify` thất bại tạm thời (network error, timeout, 5xx).
Hiện tại `AuthContext.jsx` xóa token khỏi localStorage trong **mọi** trường hợp
lỗi — dẫn đến user bị đăng xuất dù token vẫn còn hợp lệ.

Fix: chỉ xóa token khi server trả về HTTP 401 (token thực sự bị từ chối).

## API Contract

Không thay đổi API backend. Fix hoàn toàn ở frontend.

```text
GET /api/auth/verify
Authorization: Bearer <token>

200 → token hợp lệ, trả về user info
401 → token không hợp lệ hoặc hết hạn  ← XÓA token
5xx → lỗi server (cold start, v.v.)     ← GIỮ token
network error / timeout                  ← GIỮ token
```

## Business Rules

1. Chỉ xóa `auth_token` khỏi localStorage khi server trả về **HTTP 401**.
2. Với mọi lỗi khác (network error, 4xx ≠ 401, 5xx, timeout):
   - Giữ nguyên token trong localStorage
   - Không set `user` state (giữ `null`)
   - Set `loading = false` để UI không bị treo
3. Response interceptor trong `AuthContext.jsx` (auto-logout on 401 cho
   non-auth endpoints) không cần thay đổi — đã đúng.
4. Nhánh `else` (`success: false` từ 200 response) giữ nguyên hành vi cũ.

## Edge Cases

- Vercel cold start → network error / 503 → giữ token, user thấy UI bình thường
- JWT_SECRET_KEY thay đổi → server trả 401 → xóa token (đúng)
- Token hết hạn 24h → server trả 401 → xóa token (đúng)
- Server trả 200 `success: false` → xóa token (giữ hành vi cũ, an toàn)

## Out of Scope

- Token refresh / rotation
- Tăng/giảm `token_expiry_hours`
- Thay đổi JWT_SECRET_KEY management
- Retry logic cho verify request
