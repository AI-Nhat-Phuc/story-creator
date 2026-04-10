# DESIGN: Fix Session Loss on Deploy

> **Status**: APPROVED
> **Phase**: IMPLEMENT
> **Date**: 2026-04-10

---

## Changed Files

| File | Change Type | Maps to Spec Clause |
| ---- | ----------- | ------------------- |
| `frontend/src/contexts/AuthContext.jsx` | MODIFY | Business Rules #1, #2 |

## Schema / Interface Changes

Không có — fix thuần frontend.

## Model Changes

Không có.

## Logic Change

**Trước** (`AuthContext.jsx` lines 58–62):
```javascript
} catch (error) {
    console.error('Token verification failed:', error)
    localStorage.removeItem('auth_token')
    setToken(null)
}
```

**Sau**:
```javascript
} catch (error) {
    console.error('Token verification failed:', error)
    // Spec Business Rule #1: chỉ xóa token khi server trả 401
    if (error.response?.status === 401) {
        localStorage.removeItem('auth_token')
        setToken(null)
    }
    // Các lỗi khác (network, 5xx, cold start): giữ token
}
```
