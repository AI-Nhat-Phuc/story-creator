# DESIGN — Add i18n, Per-page Meta Tags, and Theme Refactor

> **Status**: DRAFT
> **Phase**: DESIGN
> **Date**: 2026-04-09

---

## Changed Files

| File | Change Type | Maps to Spec Clause |
|---|---|---|
| `frontend/package.json` | MODIFY | Spec §1 i18n, §2 meta |
| `frontend/src/main.jsx` | MODIFY | Spec §1 i18n, §2 meta |
| `frontend/src/i18n/index.js` | NEW | Spec §1 i18n |
| `frontend/src/i18n/locales/vi.json` | NEW | Spec §1 i18n |
| `frontend/src/i18n/locales/en.json` | NEW | Spec §1 i18n |
| `frontend/src/pages/Dashboard.jsx` | MODIFY | Spec §1, §2 |
| `frontend/src/pages/WorldsPage.jsx` | MODIFY | Spec §1, §2 |
| `frontend/src/pages/WorldDetailPage.jsx` | MODIFY | Spec §2 (via container) |
| `frontend/src/pages/NovelPage.jsx` | MODIFY | Spec §2 |
| `frontend/src/pages/StoriesPage.jsx` | MODIFY | Spec §2 (via container) |
| `frontend/src/pages/StoryDetailPage.jsx` | MODIFY | Spec §2 (via container) |
| `frontend/src/pages/StoryEditorPage.jsx` | MODIFY | Spec §1, §2 |
| `frontend/src/pages/StoryPrintPage.jsx` | MODIFY | Spec §1, §2 |
| `frontend/src/pages/LoginPage.jsx` | MODIFY | Spec §1, §2 |
| `frontend/src/pages/RegisterPage.jsx` | MODIFY | Spec §1, §2 |
| `frontend/src/pages/AdminPanel.jsx` | MODIFY | Spec §1, §2 |
| `frontend/src/containers/StoriesContainer.jsx` | MODIFY | Spec §1 |
| `frontend/src/containers/StoryDetailContainer.jsx` | MODIFY | Spec §1, §2 |
| `frontend/src/containers/WorldDetailContainer.jsx` | MODIFY | Spec §1, §2 |
| `frontend/src/containers/NovelContainer.jsx` | MODIFY | Spec §1, §2 |
| `frontend/src/components/Navbar.jsx` | MODIFY | Spec §1, §3 |
| `frontend/src/components/ThemeSelector.jsx` | MODIFY | Spec §1, §3 |
| `frontend/src/components/RoleBadge.jsx` | MODIFY | Spec §1 |

---

## i18n Configuration Interface

### `frontend/src/i18n/index.js`

```js
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import vi from './locales/vi.json'
import en from './locales/en.json'

const LANG_KEY = 'sc_lang'

i18n
  .use(initReactI18next)
  .init({
    resources: { vi: { translation: vi }, en: { translation: en } },
    lng: localStorage.getItem(LANG_KEY) ?? 'vi',
    fallbackLng: 'vi',
    interpolation: { escapeValue: false },  // React already escapes
  })

export default i18n
export { LANG_KEY }
```

### `frontend/src/main.jsx` additions

```jsx
import './i18n/index.js'             // must be before App import
import { HelmetProvider } from 'react-helmet-async'

// Wrap existing root render:
<HelmetProvider>
  <BrowserRouter>
    <App />
  </BrowserRouter>
</HelmetProvider>
```

---

## Locale Key Schema

All keys live in a single `translation` namespace. Dot-notation structure:

```
common.*          — shared across many components (loading, error, cancel, save…)
actions.*         — verb labels (create, edit, delete, view, logout…)
nav.*             — Navbar links and menu items
theme.*           — ThemeSelector mode/swatch/language labels
pages.dashboard.* — Dashboard page strings
pages.worlds.*    — WorldsPage strings
pages.worldDetail.*
pages.novel.*
pages.stories.*
pages.storyDetail.*
pages.storyEditor.*
pages.storyPrint.*
pages.login.*
pages.register.*
pages.admin.*
roles.*           — role display names (admin, moderator, premium, user)
meta.*            — <title> and <meta description> values
```

### Example `vi.json` skeleton

```json
{
  "common": {
    "loading": "Đang tải...",
    "error": "Có lỗi xảy ra",
    "cancel": "Hủy",
    "save": "Lưu",
    "delete": "Xóa",
    "confirm": "Xác nhận",
    "noData": "Không có dữ liệu",
    "retry": "Tải lại"
  },
  "actions": {
    "create": "Tạo mới",
    "edit": "Chỉnh sửa",
    "delete": "Xóa",
    "view": "Xem chi tiết",
    "logout": "Đăng xuất",
    "login": "Đăng nhập",
    "register": "Đăng ký"
  },
  "nav": {
    "dashboard": "Dashboard",
    "worlds": "Thế giới",
    "stories": "Câu chuyện",
    "admin": "Admin",
    "login": "Đăng nhập",
    "logoutConfirmTitle": "Xác nhận đăng xuất",
    "logoutConfirmMsg": "Bạn có chắc chắn muốn đăng xuất khỏi tài khoản?"
  },
  "theme": {
    "light": "Sáng",
    "dark": "Tối",
    "custom": "Tuỳ chỉnh",
    "primary": "Chính",
    "secondary": "Phụ",
    "accent": "Nhấn",
    "background": "Nền",
    "surface": "Bề mặt",
    "language": "Ngôn ngữ",
    "vi": "Tiếng Việt",
    "en": "English"
  },
  "roles": {
    "admin": "Quản trị viên",
    "moderator": "Kiểm duyệt viên",
    "premium": "Premium",
    "user": "Người dùng"
  },
  "meta": {
    "dashboard": {
      "title": "Dashboard – Story Creator",
      "description": "Tổng quan thống kê thế giới, câu chuyện và hạn mức của bạn."
    },
    "worlds": {
      "title": "Thế giới – Story Creator",
      "description": "Khám phá và quản lý các thế giới hư cấu của bạn."
    },
    "worldDetail": {
      "titleTemplate": "{{name}} – Story Creator",
      "titleFallback": "Thế giới – Story Creator",
      "description": "Chi tiết thế giới: nhân vật, địa điểm, câu chuyện liên quan."
    },
    "novel": {
      "titleTemplate": "Tiểu thuyết: {{name}} – Story Creator",
      "titleFallback": "Tiểu thuyết – Story Creator",
      "descriptionTemplate": "Đọc tiểu thuyết tổng hợp từ thế giới {{name}}."
    },
    "stories": {
      "title": "Câu chuyện – Story Creator",
      "description": "Danh sách tất cả câu chuyện. Tạo và quản lý tác phẩm của bạn."
    },
    "storyCreate": {
      "title": "Tạo câu chuyện – Story Creator",
      "description": "Viết câu chuyện mới với trình soạn thảo tích hợp AI."
    },
    "storyEdit": {
      "titleTemplate": "Chỉnh sửa: {{name}} – Story Creator",
      "titleFallback": "Chỉnh sửa câu chuyện – Story Creator",
      "description": "Chỉnh sửa nội dung câu chuyện."
    },
    "storyDetail": {
      "titleTemplate": "{{name}} – Story Creator",
      "titleFallback": "Câu chuyện – Story Creator",
      "description": "Chi tiết câu chuyện: nội dung, nhân vật, dòng thời gian."
    },
    "storyPrint": {
      "titleTemplate": "In: {{name}} – Story Creator",
      "titleFallback": "In câu chuyện – Story Creator",
      "description": "Xem trước bản in câu chuyện."
    },
    "login": {
      "title": "Đăng nhập – Story Creator",
      "description": "Đăng nhập vào Story Creator để quản lý thế giới và câu chuyện của bạn."
    },
    "register": {
      "title": "Đăng ký – Story Creator",
      "description": "Tạo tài khoản Story Creator miễn phí."
    },
    "admin": {
      "title": "Quản trị – Story Creator",
      "description": "Bảng điều khiển quản trị hệ thống."
    }
  },
  "pages": {
    "dashboard": {
      "title": "Dashboard",
      "refresh": "Tải lại",
      "noStats": "Không có dữ liệu thống kê",
      "publicNote": "Bạn đang xem dữ liệu công khai",
      "publicNoteDetail": "để xem thêm nội dung riêng tư của bạn và được chia sẻ",
      "totalWorlds": "Thế giới",
      "totalWorldsDesc": "Tổng số thế giới đã tạo",
      "totalStories": "Câu chuyện",
      "totalStoriesDesc": "Tổng số câu chuyện",
      "breakdown": "Phân loại dữ liệu",
      "publicBreakdown": "Dữ liệu công khai",
      "quota": "Quota của bạn",
      "publicWorlds": "Thế giới công khai",
      "publicStories": "Câu chuyện công khai",
      "slotsRemaining": "Còn {{count}} slot"
    },
    "worlds": {
      "title": "Thế giới",
      "createBtn": "+ Tạo thế giới mới",
      "adminTooltip": "Admin chỉ quản lý hệ thống, không tạo nội dung",
      "loginTooltip": "Vui lòng đăng nhập để tạo thế giới",
      "emptyAuth": "Chưa có thế giới nào. Hãy tạo thế giới đầu tiên!",
      "emptyAnon": "Chưa có thế giới công khai nào. Vui lòng đăng nhập để tạo thế giới.",
      "createModal": "Tạo thế giới mới",
      "worldName": "Tên thế giới *",
      "worldType": "Loại thế giới",
      "description": "Mô tả *",
      "descPlaceholder": "Nhập mô tả thế giới hoặc dùng GPT để tự động tạo...",
      "charCount": "{{count}} ký tự",
      "gptHint": "Click nút bên trên để GPT tạo mô tả tự động",
      "gptGenerating": "Đang tạo...",
      "gptAnalyzing": "Đang phân tích với GPT...",
      "previewAnalysis": "Xem trước phân tích",
      "analysisResult": "Kết quả phân tích",
      "noEntities": "Không phát hiện nhân vật hoặc địa điểm nào.",
      "createAndAnalyze": "Tạo & Phân tích",
      "processing": "Đang xử lý...",
      "viewDetail": "Xem chi tiết",
      "worldTypes": {
        "fantasy": "Fantasy - Thế giới phép thuật",
        "sci-fi": "Sci-Fi - Khoa học viễn tưởng",
        "modern": "Modern - Hiện đại",
        "historical": "Historical - Lịch sử"
      }
    },
    "login": {
      "title": "Đăng nhập",
      "username": "Tên đăng nhập",
      "password": "Mật khẩu",
      "loginBtn": "Đăng nhập",
      "loggingIn": "Đang đăng nhập...",
      "noAccount": "Chưa có tài khoản?",
      "registerLink": "Đăng ký ngay",
      "orDivider": "HOẶC",
      "googleFailed": "Đăng nhập Google thất bại"
    },
    "register": {
      "title": "Đăng ký",
      "username": "Tên đăng nhập",
      "email": "Email",
      "password": "Mật khẩu",
      "confirmPassword": "Xác nhận mật khẩu",
      "registerBtn": "Đăng ký",
      "hasAccount": "Đã có tài khoản?",
      "loginLink": "Đăng nhập"
    },
    "admin": {
      "title": "Quản trị hệ thống",
      "noAccess": "Bạn không có quyền truy cập trang này"
    },
    "storyEditor": {
      "newTitle": "Tạo câu chuyện mới",
      "editTitle": "Chỉnh sửa câu chuyện"
    },
    "storyPrint": {
      "title": "In câu chuyện"
    }
  }
}
```

---

## Helmet Usage Pattern (per page)

```jsx
import { Helmet } from 'react-helmet-async'
import { useTranslation } from 'react-i18next'

// Static title page (e.g. LoginPage):
const { t } = useTranslation()
<Helmet>
  <title>{t('meta.login.title')}</title>
  <meta name="description" content={t('meta.login.description')} />
</Helmet>

// Dynamic title page (e.g. WorldDetailPage):
const title = worldName
  ? t('meta.worldDetail.titleTemplate', { name: worldName })
  : t('meta.worldDetail.titleFallback')
<Helmet>
  <title>{title}</title>
  <meta name="description" content={t('meta.worldDetail.description')} />
</Helmet>
```

---

## Language Toggle Pattern (ThemeSelector)

```jsx
import { useTranslation } from 'react-i18next'
import { LANG_KEY } from '../i18n/index.js'

const { t, i18n } = useTranslation()

const switchLanguage = (lang) => {
  i18n.changeLanguage(lang)
  localStorage.setItem(LANG_KEY, lang)
}

// Render two buttons: 'vi' / 'en', highlight active
```

---

## New Method Signatures (Frontend)

```js
// i18n/index.js — exported helpers
export default i18n           // configured i18next instance
export const LANG_KEY = 'sc_lang'

// No new React components created — Helmet and useTranslation used inline per page
```
