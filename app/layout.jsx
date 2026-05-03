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

// Runs synchronously in <head> before first paint — no React involved.
// Applies the stored custom theme vars immediately so users never see
// the default light flash. Modifies document.documentElement only
// (document.body is null at this point), hence suppressHydrationWarning
// on <html> (not <body>).
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
        // First-ever custom load: vars not cached yet.
        // Add a class on <html> that hides content via CSS until
        // ThemeProvider mounts and removes it.
        html.classList.add('theme-loading');
      }
    }
  } catch(e) {}
})()`

export default function RootLayout({ children }) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
