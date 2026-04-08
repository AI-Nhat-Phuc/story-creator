import React, { createContext, useState, useContext, useEffect } from 'react'
import { authAPI } from '../services/api'
import api from '../services/api'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  // Start with loading=true so protected routes wait for token verification before
  // deciding whether the user is authenticated. Without this, navigating directly
  // to a protected URL causes an immediate redirect to /login because user===null
  // before verifyToken resolves (visible as a race condition on Vercel cold starts).
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('auth_token'))

  // Setup axios response interceptor to handle 401 errors
  // (Request interceptor with token is in api.js at module level to avoid race conditions)
  useEffect(() => {
    // Response interceptor to handle 401 errors
    const responseInterceptor = api.interceptors.response.use(
      (response) => response,
      (error) => {
        // Skip auto-logout for auth endpoints (e.g. login with wrong credentials returns 401)
        const isAuthEndpoint = error.config?.url?.includes('/auth/')
        if (error.response?.status === 401 && !isAuthEndpoint) {
          logout()
        }
        return Promise.reject(error)
      }
    )

    return () => {
      api.interceptors.response.eject(responseInterceptor)
    }
  }, [])

  // Verify token on mount
  useEffect(() => {
    const verifyToken = async () => {
      const savedToken = localStorage.getItem('auth_token')
      if (savedToken) {
        try {
          const response = await authAPI.verify()
          if (response.data.success) {
            setUser(response.data.user)
          } else {
            localStorage.removeItem('auth_token')
            setToken(null)
          }
        } catch (error) {
          console.error('Token verification failed:', error)
          localStorage.removeItem('auth_token')
          setToken(null)
        }
      }
      setLoading(false)
    }

    verifyToken()
  }, [])

  const login = async (username, password) => {
    try {
      const response = await authAPI.login({ username, password })
      if (response.data.success) {
        const { token: newToken, user: userData } = response.data
        localStorage.setItem('auth_token', newToken)
        setToken(newToken)
        setUser(userData)
        return { success: true, message: response.data.message }
      }
      return { success: false, message: response.data.message }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.error?.message
          || (error.response ? 'Đăng nhập thất bại. Vui lòng thử lại.' : 'Không thể kết nối đến server.'),
      }
    }
  }

  const register = async (username, email, password) => {
    try {
      const response = await authAPI.register({ username, email, password })
      if (response.data.success) {
        const { token: newToken, user: userData } = response.data
        localStorage.setItem('auth_token', newToken)
        setToken(newToken)
        setUser(userData)
        return { success: true, message: response.data.message }
      }
      return { success: false, message: response.data.message }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.error?.message
          || (error.response ? 'Đăng ký thất bại. Vui lòng thử lại.' : 'Không thể kết nối đến server.'),
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    setToken(null)
    setUser(null)
  }

  const changePassword = async (oldPassword, newPassword) => {
    try {
      const response = await authAPI.changePassword({
        old_password: oldPassword,
        new_password: newPassword,
      })
      return {
        success: response.data.success,
        message: response.data.message,
      }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.error?.message
          || (error.response ? 'Đổi mật khẩu thất bại. Vui lòng thử lại.' : 'Không thể kết nối đến server.'),
      }
    }
  }

  const googleLogin = async (accessToken) => {
    try {
      const response = await authAPI.googleLogin(accessToken)
      if (response.data.success) {
        const { token: newToken, user: userData } = response.data
        localStorage.setItem('auth_token', newToken)
        setToken(newToken)
        setUser(userData)
        return { success: true, message: response.data.message }
      }
      return { success: false, message: response.data.message }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.error?.message
          || (error.response ? 'Đăng nhập Google thất bại. Vui lòng thử lại.' : 'Không thể kết nối đến server.'),
      }
    }
  }

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    changePassword,
    googleLogin,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
