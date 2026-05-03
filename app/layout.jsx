import './globals.css'
import Providers from './Providers'

export const metadata = {
  title: 'Story Creator – Tạo & Quản lý Thế giới Hư cấu',
  description:
    'Xây dựng thế giới hư cấu, viết câu chuyện và phát triển nhân vật với sự hỗ trợ của AI. Nền tảng sáng tác dành cho nhà văn.',
  keywords: [
    'story creator',
    'viết truyện',
    'thế giới hư cấu',
    'nhân vật',
    'câu chuyện',
    'AI sáng tác',
  ],
  authors: [{ name: 'Story Creator' }],
  robots: { index: true, follow: true },
  openGraph: {
    type: 'website',
    url: 'https://story-creator-cyan.vercel.app/',
    title: 'Story Creator – Tạo & Quản lý Thế giới Hư cấu',
    description:
      'Xây dựng thế giới hư cấu, viết câu chuyện và phát triển nhân vật với sự hỗ trợ của AI.',
    locale: 'vi_VN',
  },
  twitter: {
    card: 'summary',
    title: 'Story Creator – Tạo & Quản lý Thế giới Hư cấu',
    description:
      'Xây dựng thế giới hư cấu, viết câu chuyện và phát triển nhân vật với sự hỗ trợ của AI.',
  },
  icons: { icon: '/icon.ico' },
}

export const viewport = {
  themeColor: '#5b21b6',
  width: 'device-width',
  initialScale: 1,
}

// Inline script runs synchronously before first paint — no React involved.
// It reads sc_theme from localStorage and applies the custom CSS vars
// immediately so custom-theme users never see the default light flash.
const themeScript = `(function(){
  try {
    var s = localStorage.getItem('sc_theme');
    if (!s) return;
    var t = JSON.parse(s);
    var html = document.documentElement;
    if (t.mode === 'dark') {
      html.setAttribute('data-theme', 'sc-dark');
    } else if (t.mode === 'custom') {
      if (t.cssVars && t.base) {
        html.setAttribute('data-theme', t.base);
        var v = t.cssVars;
        for (var k in v) { html.style.setProperty(k, v[k]); }
      } else {
        // First-ever custom load: no vars cached yet — hide until JS applies them
        document.body ? (document.body.style.visibility = 'hidden') : null;
        document.addEventListener('DOMContentLoaded', function() {
          document.body && (document.body.style.visibility = 'hidden');
        });
      }
    }
  } catch(e) {}
})()`

export default function RootLayout({ children }) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <head>
        {/* eslint-disable-next-line @next/next/no-sync-scripts */}
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body suppressHydrationWarning>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
