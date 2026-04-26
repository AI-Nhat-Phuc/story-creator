'use client'

/**
 * Thin compatibility shim that mimics the react-router-dom v6 APIs this
 * project uses (useNavigate, useParams, useSearchParams, Link) on top of
 * Next.js App Router primitives. Lets existing pages / containers /
 * components keep their call sites unchanged — only the import path
 * changes from 'react-router-dom' to '../utils/router-compat'.
 */

import NextLink from 'next/link'
import {
  useRouter,
  useParams as useNextParams,
  useSearchParams as useNextSearchParams,
} from 'next/navigation'
import React from 'react'

// useNavigate() — returns a function callable as navigate('/path') or
// navigate(-1) (go back) or navigate(path, { replace: true }).
export function useNavigate() {
  const router = useRouter()
  return React.useCallback(
    (to, options = {}) => {
      if (typeof to === 'number') {
        if (to < 0) router.back()
        else router.forward()
        return
      }
      if (options.replace) router.replace(to)
      else router.push(to)
    },
    [router]
  )
}

// useParams() — Next.js's useParams returns the same { paramName: value }
// shape, so we just re-export it.
export function useParams() {
  return useNextParams() ?? {}
}

// useSearchParams() — react-router-dom returns [URLSearchParams, setter];
// Next.js returns a read-only URLSearchParams. We expose the same tuple
// shape with a setter that performs router.replace().
export function useSearchParams() {
  const searchParams = useNextSearchParams()
  const router = useRouter()

  const setSearchParams = React.useCallback(
    (input, options = {}) => {
      const next =
        typeof input === 'function' ? input(searchParams) : input
      const params = next instanceof URLSearchParams
        ? next
        : new URLSearchParams(next)
      const qs = params.toString()
      const path = typeof window !== 'undefined'
        ? window.location.pathname
        : ''
      const url = qs ? `${path}?${qs}` : path
      if (options.replace) router.replace(url)
      else router.push(url)
    },
    [router, searchParams]
  )

  return [searchParams, setSearchParams]
}

// Link — accept the react-router-dom `to` prop and forward to next/link as
// `href`. Preserves children and any other props (className, onClick, …).
export function Link({ to, replace, children, ...rest }) {
  return (
    <NextLink href={to} replace={replace} {...rest}>
      {children}
    </NextLink>
  )
}

export default Link
