/**
 * Tests for AuthContext — session persistence on deploy.
 *
 * Spec clauses covered:
 *   Business Rule #1 — token xóa khi và CHỈ KHI server trả 401
 *   Business Rule #2 — giữ token với network error / 5xx / cold start
 *
 * Tất cả test liên quan đến Business Rule #1/#2 sẽ FAIL cho đến khi
 * catch block trong verifyToken được sửa.
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { render, waitFor } from '@testing-library/react'
import React from 'react'
import { AuthProvider, useAuth } from './AuthContext'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Renders AuthProvider and exposes the context value via ref. */
function renderAuth() {
  let ctx = null
  function Probe() {
    ctx = useAuth()
    return null
  }
  render(
    <AuthProvider>
      <Probe />
    </AuthProvider>
  )
  return () => ctx
}

// ---------------------------------------------------------------------------
// Mock api module
// ---------------------------------------------------------------------------

vi.mock('../services/api', () => {
  const mockInterceptors = {
    request: { use: vi.fn(() => 1), eject: vi.fn() },
    response: { use: vi.fn(() => 2), eject: vi.fn() },
  }
  const api = { interceptors: mockInterceptors }
  const authAPI = { verify: vi.fn() }
  return { default: api, authAPI }
})

import { authAPI } from '../services/api'

// ---------------------------------------------------------------------------
// localStorage stub
// ---------------------------------------------------------------------------

beforeEach(() => {
  localStorage.clear()
  vi.clearAllMocks()
})

afterEach(() => {
  localStorage.clear()
})

// ---------------------------------------------------------------------------
// Business Rule #1 — 401 → xóa token
// ---------------------------------------------------------------------------

describe('Business Rule #1 — 401 clears the token', () => {
  it('removes token from localStorage when verify returns 401', async () => {
    localStorage.setItem('auth_token', 'old-token')

    const err = new Error('Unauthorized')
    err.response = { status: 401 }
    authAPI.verify.mockRejectedValue(err)

    const getCtx = renderAuth()

    await waitFor(() => expect(getCtx().loading).toBe(false))

    expect(localStorage.getItem('auth_token')).toBeNull()
    expect(getCtx().token).toBeNull()
    expect(getCtx().user).toBeNull()
  })
})

// ---------------------------------------------------------------------------
// Business Rule #2 — non-401 errors keep the token
// ---------------------------------------------------------------------------

describe('Business Rule #2 — non-401 errors keep the token', () => {
  it('keeps token when verify throws a network error (no response)', async () => {
    localStorage.setItem('auth_token', 'valid-token')

    const err = new Error('Network Error')
    // no err.response — simulates fetch failure / cold start
    authAPI.verify.mockRejectedValue(err)

    const getCtx = renderAuth()

    await waitFor(() => expect(getCtx().loading).toBe(false))

    // Token must survive
    expect(localStorage.getItem('auth_token')).toBe('valid-token')
    expect(getCtx().token).toBe('valid-token')
  })

  it('keeps token when verify returns 503 (Vercel cold start)', async () => {
    localStorage.setItem('auth_token', 'valid-token')

    const err = new Error('Service Unavailable')
    err.response = { status: 503 }
    authAPI.verify.mockRejectedValue(err)

    const getCtx = renderAuth()

    await waitFor(() => expect(getCtx().loading).toBe(false))

    expect(localStorage.getItem('auth_token')).toBe('valid-token')
    expect(getCtx().token).toBe('valid-token')
  })

  it('keeps token when verify returns 500', async () => {
    localStorage.setItem('auth_token', 'valid-token')

    const err = new Error('Internal Server Error')
    err.response = { status: 500 }
    authAPI.verify.mockRejectedValue(err)

    const getCtx = renderAuth()

    await waitFor(() => expect(getCtx().loading).toBe(false))

    expect(localStorage.getItem('auth_token')).toBe('valid-token')
    expect(getCtx().token).toBe('valid-token')
  })
})

// ---------------------------------------------------------------------------
// Happy path — 200 restores user
// ---------------------------------------------------------------------------

describe('Happy path — successful verify', () => {
  it('sets user when verify succeeds', async () => {
    localStorage.setItem('auth_token', 'valid-token')

    authAPI.verify.mockResolvedValue({
      data: { success: true, user: { username: 'alice', role: 'user' } },
    })

    const getCtx = renderAuth()

    await waitFor(() => expect(getCtx().loading).toBe(false))

    expect(getCtx().user).toEqual({ username: 'alice', role: 'user' })
    expect(localStorage.getItem('auth_token')).toBe('valid-token')
  })
})
