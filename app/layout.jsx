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

export default function RootLayout({ children }) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
