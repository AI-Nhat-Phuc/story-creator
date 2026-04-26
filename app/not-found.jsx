import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex flex-col justify-center items-center bg-base-200 min-h-screen text-center">
      <h1 className="mb-2 font-bold text-5xl">404</h1>
      <p className="mb-6 text-base-content/70">Trang không tồn tại.</p>
      <Link href="/" className="btn btn-primary">
        Về trang chủ
      </Link>
    </div>
  )
}
