import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { storiesAPI, gptAPI, authAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import StoryEditorView from '../components/storyEditor/StoryEditorView'

function StoryEditorContainer({ showToast }) {
  const { storyId } = useParams()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { user } = useAuth()

  const isEditMode = Boolean(storyId)
  const worldId = searchParams.get('worldId')

  // Editor state
  const [editor, setEditor] = useState({
    title: '',
    content: '',
    saveStatus: 'idle',
    isPublished: false,
    isLoading: true,
  })

  // Track initial format for NovelEditor (only read once on load)
  const [initialFormat, setInitialFormat] = useState('html')

  // GPT state
  const [gpt, setGpt] = useState({ isLoading: false, suggestions: [] })
  const [selectionLength, setSelectionLength] = useState(0)

  // User signature
  const [userSignature, setUserSignature] = useState('')

  // Refs
  const storyIdRef = useRef(storyId || null)
  const lastSavedRef = useRef({ title: '', content: '' })
  const saveTimerRef = useRef(null)
  const editorRef = useRef(null)
  const gptSelectionRef = useRef(null)

  // Redirect if no auth
  useEffect(() => {
    if (user === null) {
      navigate('/login')
    }
  }, [user, navigate])

  // On mount: load story (edit mode) or check for draft (create mode)
  useEffect(() => {
    if (!user) return

    if (isEditMode) {
      loadStory()
    } else {
      checkForDraft()
    }

    loadUserSignature()
  }, [user, storyId])

  // Cleanup: flush pending save on unmount
  useEffect(() => {
    return () => {
      if (saveTimerRef.current) {
        clearTimeout(saveTimerRef.current)
        doSave()
      }
    }
  }, [])

  const loadStory = async () => {
    try {
      const res = await storiesAPI.getById(storyId)
      const data = res.data
      const fmt = data.format || 'plain'
      setInitialFormat(fmt)
      setEditor({
        title: data.title || '',
        content: data.content || '',
        saveStatus: 'idle',
        isPublished: data.visibility === 'public',
        isLoading: false,
      })
      lastSavedRef.current = { title: data.title || '', content: data.content || '' }
    } catch (err) {
      if (err.response?.status === 404) {
        showToast('Story not found', 'error')
        navigate('/stories')
      } else if (err.response?.status === 403) {
        showToast('Access denied', 'error')
        navigate('/stories')
      } else {
        showToast('Failed to load story', 'error')
        navigate('/stories')
      }
    }
  }

  const checkForDraft = async () => {
    // BR-7: must have worldId in create mode
    if (!worldId) {
      showToast('No world selected. Redirecting…', 'warning')
      navigate('/worlds')
      return
    }

    try {
      const res = await storiesAPI.getMyDraft()
      const draft = res.data
      if (draft && draft.story_id) {
        showToast('Resuming your draft', 'info')
        navigate(`/stories/${draft.story_id}/edit`)
        return
      }
    } catch {
      // 404 means no draft — fine
    }

    setEditor(prev => ({ ...prev, isLoading: false }))
  }

  const loadUserSignature = async () => {
    try {
      const res = await authAPI.getCurrentUser()
      setUserSignature(res.data?.signature || '')
    } catch {
      // signature not critical
    }
  }

  // ─── Derived (useMemo) ───────────────────────────────────────────────────

  const wordCount = useMemo(() => {
    const text = editorRef.current
      ? editorRef.current.getText()
      : editor.content.replace(/<[^>]+>/g, ' ')
    return text.trim() ? text.trim().split(/\s+/).filter(Boolean).length : 0
  }, [editor.content])

  const readTime = useMemo(() => Math.ceil(wordCount / 200), [wordCount])

  const headings = useMemo(() => {
    const json = editorRef.current?.getJSON()
    if (!json) return []
    return (json.content ?? [])
      .filter(n => n.type === 'heading')
      .map(n => ({ level: n.attrs?.level ?? 1, text: n.content?.[0]?.text ?? '' }))
  }, [editor.content])

  // ─── Save logic ─────────────────────────────────────────────────────────

  const doSave = useCallback(async () => {
    const { title, content } = editor
    const last = lastSavedRef.current

    // BR-1: skip if unchanged
    if (title === last.title && content === last.content) return

    // EC-4: skip if empty title in create mode
    if (!storyIdRef.current && !title.trim()) return

    setEditor(prev => ({ ...prev, saveStatus: 'saving' }))

    try {
      if (!storyIdRef.current) {
        // First save — POST
        const res = await storiesAPI.create({
          world_id: worldId,
          title: title.trim(),
          content,
          visibility: 'draft',
          format: 'html',
        })
        storyIdRef.current = res.data.story_id
      } else {
        // Subsequent saves — PATCH
        await storiesAPI.patch(storyIdRef.current, { title, content })
      }

      lastSavedRef.current = { title, content }
      setEditor(prev => ({ ...prev, saveStatus: 'saved' }))
    } catch {
      setEditor(prev => ({ ...prev, saveStatus: 'error' }))
    }
  }, [editor, worldId])

  const scheduleAutoSave = useCallback(() => {
    clearTimeout(saveTimerRef.current)
    saveTimerRef.current = setTimeout(doSave, 30_000)
  }, [doSave])

  const handleTitleChange = useCallback((value) => {
    setEditor(prev => ({ ...prev, title: value, saveStatus: 'idle' }))
    scheduleAutoSave()
  }, [scheduleAutoSave])

  const handleContentUpdate = useCallback(({ html, editor: editorInstance, selectionLength: selLen }) => {
    editorRef.current = editorInstance
    setEditor(prev => ({ ...prev, content: html, saveStatus: 'idle' }))
    setSelectionLength(selLen)
    scheduleAutoSave()
  }, [scheduleAutoSave])

  const handleSave = useCallback(() => {
    clearTimeout(saveTimerRef.current)
    doSave()
  }, [doSave])

  const handlePublish = useCallback(async () => {
    const id = storyIdRef.current
    if (!id) {
      await doSave()
    }
    const currentId = storyIdRef.current
    if (!currentId) {
      showToast('Save the story first', 'warning')
      return
    }
    try {
      await storiesAPI.update(currentId, { visibility: 'public' })
      setEditor(prev => ({ ...prev, isPublished: true }))
      showToast('Story published!', 'success')
    } catch {
      showToast('Failed to publish', 'error')
    }
  }, [doSave, showToast])

  const handleBack = useCallback(() => {
    if (storyIdRef.current) {
      navigate(`/stories/${storyIdRef.current}`)
    } else {
      navigate(worldId ? `/worlds/${worldId}` : '/stories')
    }
  }, [navigate, worldId])

  // ─── GPT tools ──────────────────────────────────────────────────────────

  const callGpt = useCallback(async (mode) => {
    const editorInstance = editorRef.current
    if (!editorInstance) return

    const { from, to } = editorInstance.state.selection
    const selected = editorInstance.state.doc.textBetween(from, to, ' ')

    // BR-2: selection must be ≥ 10 chars
    if (selected.length < 10) return

    gptSelectionRef.current = { from, to }
    setGpt({ isLoading: true, suggestions: [] })

    try {
      const res = await gptAPI.paraphrase(selected, mode)
      const suggestions = Array.isArray(res.data)
        ? res.data
        : res.data?.suggestions ?? [res.data?.result ?? '']
      setGpt({ isLoading: false, suggestions: suggestions.filter(Boolean) })
    } catch {
      showToast('GPT error', 'error')
      setGpt({ isLoading: false, suggestions: [] })
    }
  }, [showToast])

  const handleParaphrase = useCallback(() => callGpt('paraphrase'), [callGpt])
  const handleExpand = useCallback(() => callGpt('expand'), [callGpt])

  const handleApply = useCallback((suggestion) => {
    const editorInstance = editorRef.current
    const sel = gptSelectionRef.current
    if (!editorInstance || !sel) return
    editorInstance.chain().focus().deleteRange(sel).insertContent(suggestion).run()
    setGpt({ isLoading: false, suggestions: [] })
    gptSelectionRef.current = null
  }, [])

  const handleClearSuggestions = useCallback(() => {
    setGpt({ isLoading: false, suggestions: [] })
  }, [])

  // ─── Signature ──────────────────────────────────────────────────────────

  const handleInsertSignature = useCallback(() => {
    const editorInstance = editorRef.current
    if (!editorInstance || !userSignature) return

    // BR-10: skip if already inserted
    const text = editorInstance.getText()
    if (text.includes(`— ${userSignature}`)) {
      showToast('Signature already in document', 'info')
      return
    }

    editorInstance.chain().focus().insertContent(`<p>— ${userSignature}</p>`).run()
  }, [editorRef, userSignature, showToast])

  // ─── Render ─────────────────────────────────────────────────────────────

  const gptProps = {
    isLoading: gpt.isLoading,
    suggestions: gpt.suggestions,
    selectionLength,
    onParaphrase: handleParaphrase,
    onExpand: handleExpand,
    onApply: handleApply,
    onClear: handleClearSuggestions,
  }

  return (
    <StoryEditorView
      editor={editor}
      wordCount={wordCount}
      readTime={readTime}
      headings={headings}
      editorRef={editorRef}
      gpt={gptProps}
      userSignature={userSignature}
      onTitleChange={handleTitleChange}
      onContentUpdate={handleContentUpdate}
      onSave={handleSave}
      onPublish={handlePublish}
      onBack={handleBack}
      onInsertSignature={handleInsertSignature}
      initialFormat={initialFormat}
    />
  )
}

export default StoryEditorContainer
