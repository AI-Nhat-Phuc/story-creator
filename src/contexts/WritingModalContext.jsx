'use client'

import React, { createContext, useContext, useState, useRef, useCallback, useEffect } from 'react'
import TurndownService from 'turndown'
import { marked } from 'marked'
import { storiesAPI } from '../services/api'
import { useAuth } from './AuthContext'

const turndownSvc = new TurndownService({ headingStyle: 'atx', bulletListMarker: '-' })
const toMarkdown = (html) => turndownSvc.turndown(html || '')

const AUTO_SAVE_DELAY = 2_000

const WritingModalContext = createContext(null)

export function WritingModalProvider({ children, showToast }) {
  const { user } = useAuth()

  // Modal visibility state
  const [modalState, setModalState] = useState('closed') // 'closed' | 'open' | 'minimized'

  // Draft content state
  const [draft, setDraft] = useState({
    storyId: null,
    worldId: null,
    title: '',
    content: '',
    saveStatus: 'idle', // 'idle' | 'saving' | 'saved' | 'error'
    isPublished: false,
    isLoading: false,
  })

  // Mutable refs — avoid stale closures in doSave
  const draftRef = useRef({ title: '', content: '' })
  const lastSavedRef = useRef({ title: '', content: '' })
  const storyIdRef = useRef(null)
  const worldIdRef = useRef(null)
  const saveTimerRef = useRef(null)
  const editorRef = useRef(null)

  // Check for active draft when user logs in
  useEffect(() => {
    if (!user) return
    checkForActiveDraft()
  }, [user])

  const checkForActiveDraft = useCallback(async () => {
    try {
      const res = await storiesAPI.getMyDraft()
      const story = res.data?.story ?? res.data
      if (!story) return
      // Show modal only if draft exists and we're not already open
      setModalState((prev) => (prev === 'closed' ? 'minimized' : prev))
    } catch {
      // Not critical
    }
  }, [])

  const loadDraft = useCallback(async () => {
    setDraft((prev) => ({ ...prev, isLoading: true }))
    try {
      const res = await storiesAPI.getMyDraft()
      const story = res.data?.story ?? res.data
      if (!story) {
        setDraft((prev) => ({ ...prev, isLoading: false }))
        return
      }
      const rawContent = story.content || ''
      const htmlContent = story.format === 'markdown' ? marked.parse(rawContent) : rawContent
      const markdownBaseline = story.format === 'markdown' ? rawContent : toMarkdown(rawContent)

      storyIdRef.current = story.story_id
      worldIdRef.current = story.world_id
      draftRef.current = { title: story.title || '', content: htmlContent }
      lastSavedRef.current = { title: story.title || '', content: markdownBaseline }

      setDraft({
        storyId: story.story_id,
        worldId: story.world_id,
        title: story.title || '',
        content: htmlContent,
        saveStatus: 'saved',
        isPublished: story.visibility === 'public',
        isLoading: false,
      })
    } catch {
      setDraft((prev) => ({ ...prev, isLoading: false }))
    }
  }, [])

  const doSave = useCallback(async () => {
    const { title, content } = draftRef.current
    const markdownContent = toMarkdown(content)
    const last = lastSavedRef.current
    if (title === last.title && markdownContent === last.content) return

    setDraft((prev) => ({ ...prev, saveStatus: 'saving' }))
    try {
      if (!storyIdRef.current) {
        const worldId = worldIdRef.current
        if (!worldId) {
          setDraft((prev) => ({ ...prev, saveStatus: 'error' }))
          return
        }
        const res = await storiesAPI.create({
          world_id: worldId,
          title: title.trim() || '(no title)',
          content: markdownContent,
          visibility: 'draft',
          format: 'markdown',
        })
        storyIdRef.current = res.data.story_id
        setDraft((prev) => ({ ...prev, storyId: res.data.story_id }))
      } else {
        await storiesAPI.patch(storyIdRef.current, {
          title: title.trim() || '(no title)',
          content: markdownContent,
          format: 'markdown',
        })
      }
      lastSavedRef.current = { title: title.trim() || '(no title)', content: markdownContent }
      setDraft((prev) => ({ ...prev, saveStatus: 'saved' }))
    } catch {
      setDraft((prev) => ({ ...prev, saveStatus: 'error' }))
      showToast?.('Failed to save draft', 'error')
    }
  }, [showToast])

  const scheduleAutoSave = useCallback(() => {
    clearTimeout(saveTimerRef.current)
    saveTimerRef.current = setTimeout(doSave, AUTO_SAVE_DELAY)
  }, [doSave])

  const handleTitleChange = useCallback((value) => {
    draftRef.current = { ...draftRef.current, title: value }
    setDraft((prev) => ({ ...prev, title: value, saveStatus: 'idle' }))
    scheduleAutoSave()
  }, [scheduleAutoSave])

  const handleContentUpdate = useCallback(({ html }) => {
    draftRef.current = { ...draftRef.current, content: html }
    setDraft((prev) => ({ ...prev, content: html, saveStatus: 'idle' }))
    scheduleAutoSave()
  }, [scheduleAutoSave])

  const handleSave = useCallback(() => {
    clearTimeout(saveTimerRef.current)
    doSave()
  }, [doSave])

  const handlePublish = useCallback(async () => {
    if (!storyIdRef.current) await doSave()
    if (!storyIdRef.current) return
    try {
      await storiesAPI.update(storyIdRef.current, { visibility: 'public' })
      setDraft((prev) => ({ ...prev, isPublished: true, saveStatus: 'saved' }))
      showToast?.('Story published!', 'success')
      // After publish, close the modal — don't re-open this draft
      closeModal()
    } catch {
      showToast?.('Failed to publish', 'error')
    }
  }, [doSave, showToast])

  const openModal = useCallback(async () => {
    // Always refetch from server on open (server is source of truth)
    setModalState('open')
    await loadDraft()
  }, [loadDraft])

  const minimizeModal = useCallback(() => {
    setModalState('minimized')
  }, [])

  const closeModal = useCallback(() => {
    clearTimeout(saveTimerRef.current)
    setModalState('closed')
    // Reset state
    storyIdRef.current = null
    worldIdRef.current = null
    draftRef.current = { title: '', content: '' }
    lastSavedRef.current = { title: '', content: '' }
    setDraft({
      storyId: null, worldId: null, title: '', content: '',
      saveStatus: 'idle', isPublished: false, isLoading: false,
    })
  }, [])

  // Flush pending save on unmount
  useEffect(() => {
    return () => {
      clearTimeout(saveTimerRef.current)
    }
  }, [])

  return (
    <WritingModalContext.Provider value={{
      modalState,
      draft,
      editorRef,
      storyIdRef,
      openModal,
      minimizeModal,
      closeModal,
      handleTitleChange,
      handleContentUpdate,
      handleSave,
      handlePublish,
    }}>
      {children}
    </WritingModalContext.Provider>
  )
}

export function useWritingModal() {
  const ctx = useContext(WritingModalContext)
  if (!ctx) throw new Error('useWritingModal must be used inside WritingModalProvider')
  return ctx
}
