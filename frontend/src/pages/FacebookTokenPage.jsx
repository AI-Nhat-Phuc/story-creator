import React, { useState } from 'react'
import {
  KeyIcon,
  ClipboardDocumentIcon,
  CheckCircleIcon,
  ArrowTopRightOnSquareIcon,
} from '@heroicons/react/24/outline'

/**
 * Public page that guides users through obtaining a Facebook Access Token
 * via Facebook's Graph API Explorer or manual app setup.
 *
 * This page does NOT require authentication.
 */
export default function FacebookTokenPage() {
  const [copied, setCopied] = useState(false)
  const [token, setToken] = useState('')

  const appId = import.meta.env.FACEBOOK_APP_ID || ''

  const graphExplorerUrl = 'https://developers.facebook.com/tools/explorer/'
  const oauthUrl = appId
    ? `https://www.facebook.com/v19.0/dialog/oauth?client_id=${appId}&redirect_uri=${encodeURIComponent(window.location.origin + '/facebook-token')}&scope=pages_show_list,pages_read_engagement,pages_manage_posts,pages_read_user_content`
    : null

  const handleCopy = () => {
    if (!token) return
    navigator.clipboard.writeText(token)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Check for OAuth redirect code in URL
  const urlParams = new URLSearchParams(window.location.search)
  const oauthCode = urlParams.get('code')

  return (
    <div className="flex justify-center items-center bg-base-200 p-4 min-h-screen">
      <div className="bg-base-100 shadow-xl w-full max-w-2xl card">
        <div className="card-body">
          <div className="text-center">
            <KeyIcon className="mx-auto mb-2 w-12 h-12 text-primary" />
            <h1 className="font-bold text-2xl">Lấy Facebook Access Token</h1>
            <p className="mt-1 text-base-content/60">
              Token cần thiết để quản lý bài đăng trên Facebook Page.
            </p>
          </div>

          <div className="mt-6 divider">Cách 1: Graph API Explorer (Khuyên dùng)</div>

          <div className="space-y-3">
            <p className="text-sm">
              Truy cập <strong>Graph API Explorer</strong> của Facebook để lấy token nhanh chóng:
            </p>
            <ol className="space-y-2 pl-5 text-sm list-decimal">
              <li>
                Mở{' '}
                <a
                  href={graphExplorerUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="link link-primary"
                >
                  Graph API Explorer
                  <ArrowTopRightOnSquareIcon className="inline ml-1 w-3 h-3" />
                </a>
              </li>
              <li>Chọn ứng dụng Facebook của bạn (hoặc tạo mới)</li>
              <li>
                Click <strong>"Generate Access Token"</strong>
              </li>
              <li>
                Cấp quyền: <code className="badge-outline badge badge-sm">pages_show_list</code>{' '}
                <code className="badge-outline badge badge-sm">pages_read_engagement</code>{' '}
                <code className="badge-outline badge badge-sm">pages_manage_posts</code>{' '}
                <code className="badge-outline badge badge-sm">pages_read_user_content</code>
              </li>
              <li>Copy token và dán vào ô bên dưới</li>
            </ol>
            <a
              href={graphExplorerUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary btn-sm"
            >
              <ArrowTopRightOnSquareIcon className="w-4 h-4" />
              Mở Graph API Explorer
            </a>
          </div>

          {oauthUrl && (
            <>
              <div className="mt-4 divider">Cách 2: Đăng nhập trực tiếp</div>
              <div className="space-y-3">
                <p className="text-sm">
                  Đăng nhập bằng tài khoản Facebook để cấp quyền cho ứng dụng tự động:
                </p>
                <a
                  href={oauthUrl}
                  className="btn-outline btn btn-sm"
                >
                  <ArrowTopRightOnSquareIcon className="w-4 h-4" />
                  Đăng nhập Facebook &amp; cấp quyền
                </a>
                {oauthCode && (
                  <div className="bg-success/10 p-3 rounded-lg">
                    <p className="font-semibold text-success text-sm">
                      <CheckCircleIcon className="inline mr-1 w-4 h-4" />
                      Đã nhận authorization code!
                    </p>
                    <p className="mt-1 text-xs text-base-content/60 break-all">
                      Code: <code>{oauthCode}</code>
                    </p>
                    <p className="mt-1 text-xs text-base-content/50">
                      Sử dụng code này để exchange lấy access token qua API backend (POST /api/facebook/token/exchange).
                    </p>
                  </div>
                )}
              </div>
            </>
          )}

          <div className="mt-4 divider">Token của bạn</div>

          <div className="space-y-3">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Dán Access Token vào đây..."
                className="flex-1 input input-bordered"
                value={token}
                onChange={(e) => setToken(e.target.value)}
              />
              <button
                className={`btn ${copied ? 'btn-success' : 'btn-outline'}`}
                onClick={handleCopy}
                disabled={!token}
              >
                {copied ? (
                  <CheckCircleIcon className="w-5 h-5" />
                ) : (
                  <ClipboardDocumentIcon className="w-5 h-5" />
                )}
              </button>
            </div>
            {token && (
              <p className="text-success text-xs">
                <CheckCircleIcon className="inline mr-1 w-3 h-3" />
                Token đã sẵn sàng. Copy và dán vào trang{' '}
                <a href={`/facebook?key=story-creator-fb-2024`} className="link link-primary">
                  Facebook Manager
                </a>
                .
              </p>
            )}
          </div>

          <div className="bg-warning/10 mt-6 p-4 rounded-lg">
            <p className="font-semibold text-warning text-sm">
              <KeyIcon className="inline mr-1 w-4 h-4" />
              Lưu ý bảo mật
            </p>
            <ul className="mt-1 pl-4 text-xs text-base-content/60 list-disc">
              <li>Không chia sẻ Access Token cho người khác</li>
              <li>Token có thời hạn — hãy lấy lại khi hết hạn</li>
              <li>Chỉ cấp quyền cần thiết cho ứng dụng</li>
              <li>Sử dụng long-lived token cho ứng dụng sản xuất</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
