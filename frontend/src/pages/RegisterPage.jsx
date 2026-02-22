import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useGoogleLogin } from '@react-oauth/google'
import FacebookLogin from '@greatsumini/react-facebook-login'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import { BookOpenIcon } from '@heroicons/react/24/solid'

const FACEBOOK_APP_ID = import.meta.env.VITE_FACEBOOK_APP_ID

export default function RegisterPage() {
  const navigate = useNavigate()
  const { register, googleLogin, facebookLogin, isAuthenticated } = useAuth()
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [loading, setLoading] = useState(false)
  const [oauthLoading, setOauthLoading] = useState('')
  const [error, setError] = useState('')

  // Redirect if already logged in
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/')
    }
  }, [isAuthenticated, navigate])

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Mật khẩu xác nhận không khớp')
      setLoading(false)
      return
    }

    if (formData.password.length < 6) {
      setError('Mật khẩu phải có ít nhất 6 ký tự')
      setLoading(false)
      return
    }

    const result = await register(formData.username, formData.email, formData.password)

    setLoading(false)

    if (result.success) {
      navigate('/')
    } else {
      setError(result.message)
    }
  }

  // Google OAuth Handler
  const handleGoogleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      setOauthLoading('google')
      setError('')
      const result = await googleLogin(tokenResponse.access_token)
      setOauthLoading('')

      if (result.success) {
        navigate('/')
      } else {
        setError(result.message)
      }
    },
    onError: () => {
      setOauthLoading('')
      setError('Đăng ký Google thất bại')
    },
  })

  // Facebook OAuth Handler
  const handleFacebookSuccess = async (response) => {
    if (response.accessToken) {
      setOauthLoading('facebook')
      setError('')
      const result = await facebookLogin(response.accessToken)
      setOauthLoading('')

      if (result.success) {
        navigate('/')
      } else {
        setError(result.message)
      }
    }
  }

  const handleFacebookError = () => {
    setOauthLoading('')
    setError('Đăng ký Facebook thất bại')
  }

  return (
    <div className="flex justify-center items-center bg-gradient-to-br from-primary/10 via-base-200 to-secondary/10 min-h-screen">
      <div className="bg-base-100 shadow-2xl w-full max-w-md card">
        <div className="card-body">
          {/* Header */}
          <div className="mb-6 text-center">
            <h1 className="mb-2 font-bold text-4xl">
              <BookOpenIcon className="inline w-9 h-9" /> Story Creator
            </h1>
            <h2 className="font-semibold text-2xl">
              Đăng ký
            </h2>
          </div>

          {error && (
            <div className="mb-4 alert alert-error">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="stroke-current w-6 h-6 shrink-0"
                fill="none"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span>{error}</span>
            </div>
          )}

          {/* OAuth Buttons */}
          <div className="space-y-3 mb-6">
            {/* Google */}
            <button
              onClick={handleGoogleLogin}
              disabled={!!oauthLoading}
              className="justify-start gap-3 bg-white hover:bg-gray-50 border-2 border-gray-300 w-full font-medium text-gray-700 btn"
            >
              {oauthLoading === 'google' ? (
                <LoadingSpinner size="sm" />
              ) : (
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
              )}
              <span>Đăng ký</span>
            </button>

            {/* Facebook */}
            <FacebookLogin
              appId={FACEBOOK_APP_ID}
              onSuccess={handleFacebookSuccess}
              onFail={handleFacebookError}
              onProfileSuccess={() => {}}
              render={({ onClick }) => (
                <button
                  onClick={(e) => {
                    setOauthLoading('facebook')
                    onClick(e)
                  }}
                  disabled={!!oauthLoading}
                  className="justify-start gap-3 bg-white hover:bg-gray-50 border-2 border-gray-300 w-full font-medium text-gray-700 btn"
                >
                  {oauthLoading === 'facebook' ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    <svg className="w-5 h-5" fill="#1877F2" viewBox="0 0 24 24">
                      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                    </svg>
                  )}
                  <span>Đăng ký</span>
                </button>
              )}
            />
          </div>

          <div className="divider">HOẶC</div>

          <form onSubmit={handleSubmit}>
            <div className="form-control">
              <label className="label">
                <span className="label-text">Tên đăng nhập *</span>
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="input input-bordered"
                placeholder="Ít nhất 3 ký tự"
                required
                minLength={3}
                autoFocus
              />
            </div>

            <div className="mt-4 form-control">
              <label className="label">
                <span className="label-text">Email *</span>
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="input input-bordered"
                placeholder="example@email.com"
                required
              />
            </div>

            <div className="mt-4 form-control">
              <label className="label">
                <span className="label-text">Mật khẩu *</span>
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="input input-bordered"
                placeholder="Ít nhất 6 ký tự"
                required
                minLength={6}
              />
            </div>

            <div className="mt-4 form-control">
              <label className="label">
                <span className="label-text">Xác nhận mật khẩu *</span>
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                className="input input-bordered"
                placeholder="Nhập lại mật khẩu"
                required
              />
            </div>

            <div className="mt-6 form-control">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? <LoadingSpinner size="sm" /> : 'Đăng ký'}
              </button>
            </div>
          </form>

          <div className="mt-4 text-center">
            <p className="text-sm">
              Đã có tài khoản?{' '}
              <Link to="/login" className="link link-primary">
                Đăng nhập
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
