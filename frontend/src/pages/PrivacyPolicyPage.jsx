import React from 'react'
import {
  ShieldCheckIcon,
  InformationCircleIcon,
  LockClosedIcon,
  UserIcon,
  TrashIcon,
  EnvelopeIcon,
} from '@heroicons/react/24/outline'

/**
 * Public Privacy Policy page — required for Facebook App Review / Facebook Login.
 * Accessible at /privacy-policy without authentication.
 */
export default function PrivacyPolicyPage() {
  const appName = 'Story Creator'
  const contactEmail = import.meta.env.VITE_CONTACT_EMAIL || 'support@story-creator.app'
  const lastUpdated = '08/03/2025'

  return (
    <div className="min-h-screen bg-base-200 py-10 px-4">
      <div className="max-w-3xl mx-auto space-y-6">

        {/* Header */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body text-center">
            <ShieldCheckIcon className="w-14 h-14 text-primary mx-auto mb-2" />
            <h1 className="text-3xl font-bold">Chính Sách Quyền Riêng Tư</h1>
            <p className="text-base-content/60 text-sm">Privacy Policy — {appName}</p>
            <p className="text-base-content/50 text-xs mt-1">
              Cập nhật lần cuối / Last updated: {lastUpdated}
            </p>
          </div>
        </div>

        {/* Introduction */}
        <div className="card bg-base-100 shadow">
          <div className="card-body">
            <div className="flex items-center gap-2 mb-3">
              <InformationCircleIcon className="w-6 h-6 text-info shrink-0" />
              <h2 className="text-lg font-semibold">Giới Thiệu / Introduction</h2>
            </div>
            <p className="text-sm text-base-content/80 leading-relaxed">
              Ứng dụng <strong>{appName}</strong> coi trọng quyền riêng tư của người dùng.
              Chính sách này mô tả cách chúng tôi thu thập, sử dụng và bảo vệ thông tin của bạn,
              đặc biệt liên quan đến việc tích hợp với <strong>Facebook Platform</strong>.
            </p>
            <p className="text-sm text-base-content/60 leading-relaxed mt-2 italic">
              <strong>{appName}</strong> respects your privacy. This policy describes how we
              collect, use, and protect your information, particularly in connection with the{' '}
              <strong>Facebook Platform</strong> integration.
            </p>
          </div>
        </div>

        {/* Data Collected */}
        <div className="card bg-base-100 shadow">
          <div className="card-body">
            <div className="flex items-center gap-2 mb-3">
              <UserIcon className="w-6 h-6 text-warning shrink-0" />
              <h2 className="text-lg font-semibold">Dữ Liệu Chúng Tôi Thu Thập / Data We Collect</h2>
            </div>

            <p className="text-sm font-medium mb-2">Khi bạn kết nối tài khoản Facebook, chúng tôi có thể truy cập:</p>
            <ul className="text-sm text-base-content/80 space-y-2 list-none">
              {[
                {
                  vi: 'Thông tin hồ sơ công khai Facebook (tên, ảnh đại diện, ID người dùng)',
                  en: 'Public Facebook profile information (name, profile picture, user ID)',
                },
                {
                  vi: 'Danh sách các Facebook Page mà bạn quản lý',
                  en: 'List of Facebook Pages you manage',
                },
                {
                  vi: 'Nội dung bài đăng và bình luận trên các Page đó',
                  en: 'Post and comment content on those Pages',
                },
                {
                  vi: 'Facebook Access Token (dùng để thực hiện các thao tác thay mặt bạn)',
                  en: 'Facebook Access Token (used to perform actions on your behalf)',
                },
                {
                  vi: 'Số liệu tương tác: lượt thích, bình luận, chia sẻ',
                  en: 'Engagement metrics: likes, comments, shares',
                },
              ].map(({ vi, en }, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-primary mt-0.5">•</span>
                  <span>
                    {vi}
                    <br />
                    <span className="text-base-content/50 italic text-xs">{en}</span>
                  </span>
                </li>
              ))}
            </ul>

            <div className="mt-4 p-3 rounded-lg bg-info/10 text-xs text-base-content/70">
              <InformationCircleIcon className="inline w-4 h-4 mr-1 text-info" />
              Chúng tôi chỉ yêu cầu các quyền cần thiết:{' '}
              <code className="badge badge-sm badge-outline">pages_show_list</code>{' '}
              <code className="badge badge-sm badge-outline">pages_read_engagement</code>{' '}
              <code className="badge badge-sm badge-outline">pages_manage_posts</code>{' '}
              <code className="badge badge-sm badge-outline">pages_read_user_content</code>
            </div>
          </div>
        </div>

        {/* How We Use Data */}
        <div className="card bg-base-100 shadow">
          <div className="card-body">
            <div className="flex items-center gap-2 mb-3">
              <LockClosedIcon className="w-6 h-6 text-success shrink-0" />
              <h2 className="text-lg font-semibold">Cách Sử Dụng Dữ Liệu / How We Use Data</h2>
            </div>
            <ul className="text-sm text-base-content/80 space-y-2 list-none">
              {[
                {
                  vi: 'Hiển thị và quản lý bài đăng trên Facebook Page của bạn ngay trong ứng dụng',
                  en: 'Display and manage posts on your Facebook Page within the app',
                },
                {
                  vi: 'Tạo nội dung bài đăng tự động bằng trợ lý AI (GPT)',
                  en: 'Generate post content automatically with the AI assistant (GPT)',
                },
                {
                  vi: 'Tìm kiếm và lọc bài đăng theo từ khóa',
                  en: 'Search and filter posts by keyword',
                },
                {
                  vi: 'Xem thống kê tương tác (likes, comments, shares)',
                  en: 'View engagement statistics (likes, comments, shares)',
                },
              ].map(({ vi, en }, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-success mt-0.5">✓</span>
                  <span>
                    {vi}
                    <br />
                    <span className="text-base-content/50 italic text-xs">{en}</span>
                  </span>
                </li>
              ))}
            </ul>
            <p className="text-sm text-base-content/60 mt-4">
              Chúng tôi <strong>không</strong> bán, cho thuê hoặc chia sẻ dữ liệu Facebook của bạn
              với bất kỳ bên thứ ba nào vì mục đích thương mại.
            </p>
            <p className="text-xs text-base-content/50 italic mt-1">
              We do <strong>not</strong> sell, rent, or share your Facebook data with any third party
              for commercial purposes.
            </p>
          </div>
        </div>

        {/* Data Storage & Retention */}
        <div className="card bg-base-100 shadow">
          <div className="card-body">
            <div className="flex items-center gap-2 mb-3">
              <TrashIcon className="w-6 h-6 text-error shrink-0" />
              <h2 className="text-lg font-semibold">Lưu Trữ & Xoá Dữ Liệu / Storage & Deletion</h2>
            </div>
            <ul className="text-sm text-base-content/80 space-y-2 list-none">
              <li className="flex gap-2">
                <span className="text-primary mt-0.5">•</span>
                <span>
                  Access Token Facebook được lưu trữ tạm thời trong phiên làm việc và không được
                  lưu lâu dài trên máy chủ.
                  <br />
                  <span className="text-base-content/50 italic text-xs">
                    Facebook Access Tokens are stored temporarily in the session and are not
                    persisted long-term on the server.
                  </span>
                </span>
              </li>
              <li className="flex gap-2">
                <span className="text-primary mt-0.5">•</span>
                <span>
                  Nội dung bài đăng chỉ được đọc theo yêu cầu và không được lưu trong cơ sở dữ liệu
                  của ứng dụng.
                  <br />
                  <span className="text-base-content/50 italic text-xs">
                    Post content is only fetched on demand and is not stored in the application
                    database.
                  </span>
                </span>
              </li>
              <li className="flex gap-2">
                <span className="text-primary mt-0.5">•</span>
                <span>
                  Bạn có thể thu hồi quyền truy cập của ứng dụng bất kỳ lúc nào tại{' '}
                  <a
                    href="https://www.facebook.com/settings?tab=applications"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="link link-primary"
                  >
                    Cài đặt ứng dụng Facebook
                  </a>
                  .
                  <br />
                  <span className="text-base-content/50 italic text-xs">
                    You can revoke app access at any time via{' '}
                    <a
                      href="https://www.facebook.com/settings?tab=applications"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="link link-primary"
                    >
                      Facebook App Settings
                    </a>
                    .
                  </span>
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* Facebook Platform Compliance */}
        <div className="card bg-base-100 shadow">
          <div className="card-body">
            <div className="flex items-center gap-2 mb-3">
              <ShieldCheckIcon className="w-6 h-6 text-primary shrink-0" />
              <h2 className="text-lg font-semibold">
                Tuân Thủ Facebook Platform / Facebook Platform Compliance
              </h2>
            </div>
            <p className="text-sm text-base-content/80 leading-relaxed">
              Ứng dụng này tuân thủ{' '}
              <a
                href="https://developers.facebook.com/policy/"
                target="_blank"
                rel="noopener noreferrer"
                className="link link-primary"
              >
                Chính sách Nền tảng Facebook
              </a>{' '}
              và{' '}
              <a
                href="https://www.facebook.com/legal/terms"
                target="_blank"
                rel="noopener noreferrer"
                className="link link-primary"
              >
                Điều khoản Dịch vụ Facebook
              </a>
              . Dữ liệu từ Facebook chỉ được sử dụng cho các tính năng được mô tả trong chính
              sách này và không được dùng cho bất kỳ mục đích nào khác.
            </p>
            <p className="text-xs text-base-content/50 italic mt-2">
              This application complies with the{' '}
              <a
                href="https://developers.facebook.com/policy/"
                target="_blank"
                rel="noopener noreferrer"
                className="link link-primary"
              >
                Facebook Platform Policy
              </a>{' '}
              and{' '}
              <a
                href="https://www.facebook.com/legal/terms"
                target="_blank"
                rel="noopener noreferrer"
                className="link link-primary"
              >
                Facebook Terms of Service
              </a>
              . Data from Facebook is only used for the features described in this policy.
            </p>
          </div>
        </div>

        {/* Contact */}
        <div className="card bg-base-100 shadow">
          <div className="card-body">
            <div className="flex items-center gap-2 mb-3">
              <EnvelopeIcon className="w-6 h-6 text-secondary shrink-0" />
              <h2 className="text-lg font-semibold">Liên Hệ / Contact</h2>
            </div>
            <p className="text-sm text-base-content/80">
              Nếu bạn có câu hỏi về chính sách quyền riêng tư này, vui lòng liên hệ:
            </p>
            <p className="text-xs text-base-content/50 italic mt-1">
              If you have questions about this privacy policy, please contact us:
            </p>
            <a href={`mailto:${contactEmail}`} className="link link-primary text-sm mt-2 inline-block">
              {contactEmail}
            </a>
          </div>
        </div>

        {/* Footer note */}
        <p className="text-center text-xs text-base-content/40 pb-4">
          © {new Date().getFullYear()} {appName}. Tất cả quyền được bảo lưu / All rights reserved.
        </p>
      </div>
    </div>
  )
}
