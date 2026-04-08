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

  const worldId = searchParams.get('worldId')

  const [editor, setEditor] = useState({
    title: '',
    content: '',
    saveStatus: 'idle',
    isPublished: false,
    isLoading: true,
  })
  const [initialFormat, setInitialFormat] = useState('html')
  const [gpt, setGpt] = useState({ isLoading: false, suggestions: [], selectionLength: 0 })
  const [userSignature, setUserSignature] = useState('')

  // Refs — mirror mutable values so doSave is always reading current data (no stale closures)
  const storyIdRef = useRef(storyId || null)
  const worldIdRef = useRef(worldId)
  const editorDataRef = useRef({ title: '', content: '' })
  const lastSavedRef = useRef({ title: '', content: '' })
  const saveTimerRef = useRef(null)
  const editorRef = useRef(null)
  const gptSelectionRef = useRef(null)

  useEffect(() => {
    if (user === null) {
      navigate('/login')
    }
  }, [user, navigate])

  useEffect(() => {
    if (!user) return
    const storyLoad = storyId ? loadStory() : checkForDraft()
    Promise.all([storyLoad, loadUserSignature()])
  }, [user, storyId])

  useEffect(() => {
    return () => {
      clearTimeout(saveTimerRef.current)
      doSave()
    }
  }, [])

  const loadStory = async () => {
    try {
      const res = await storiesAPI.getById(storyId)
      const data = res.data
      const title = data.title || ''
      const content = data.content || ''
      storyIdRef.current = storyId
      setInitialFormat(data.format || 'plain')
      editorDataRef.current = { title, content }
      lastSavedRef.current = { title, content }
      setEditor({ title, content, saveStatus: 'idle', isPublished: data.visibility === 'public', isLoading: false })
    } catch (err) {
      showToast(err.response?.status === 403 ? 'Access denied' : 'Story not found', 'error')
      navigate('/stories')
    }
  }

  const checkForDraft = async () => {
    if (!worldId) {
      showToast('No world selected. Redirecting…', 'warning')
      navigate('/worlds')
      return
    }
    setEditor(prev => ({ ...prev, isLoading: false }))
  }

  const loadUserSignature = async () => {
    try {
      const res = await authAPI.getCurrentUser()
      setUserSignature(res.data?.signature || '')
    } catch {
      // not critical
    }
  }

  const wordCount = useMemo(() => {
    const raw = editorRef.current
      ? editorRef.current.getText()
      : editor.content.replace(/<[^>]+>/g, ' ')
    const trimmed = raw.trim()
    return trimmed ? trimmed.split(/\s+/).filter(Boolean).length : 0
  }, [editor.content])

  const readTime = useMemo(() => Math.ceil(wordCount / 200), [wordCount])

  const headings = useMemo(() => {
    const json = editorRef.current?.getJSON()
    if (!json) return []
    return (json.content ?? [])
      .filter(n => n.type === 'heading')
      .map(n => ({ level: n.attrs?.level ?? 1, text: n.content?.[0]?.text ?? '' }))
  }, [editor.content])

  // doSave reads from refs — stable callback, no stale closure issues
  const doSave = useCallback(async () => {
    const { title, content } = editorDataRef.current
    const last = lastSavedRef.current
    if (title === last.title && content === last.content) return
    if (!storyIdRef.current && !title.trim()) return

    setEditor(prev => ({ ...prev, saveStatus: 'saving' }))
    try {
      if (!storyIdRef.current) {
        const res = await storiesAPI.create({
          world_id: worldIdRef.current,
          title: title.trim(),
          content,
          visibility: 'draft',
          format: 'html',
        })
        storyIdRef.current = res.data.story_id
      } else {
        await storiesAPI.patch(storyIdRef.current, { title, content })
      }
      lastSavedRef.current = { title, content }
      setEditor(prev => ({ ...prev, saveStatus: 'saved' }))
    } catch {
      setEditor(prev => ({ ...prev, saveStatus: 'error' }))
    }
  }, [])

  const scheduleAutoSave = useCallback(() => {
    clearTimeout(saveTimerRef.current)
    saveTimerRef.current = setTimeout(doSave, 30_000)
  }, [doSave])

  const handleTitleChange = useCallback((value) => {
    editorDataRef.current = { ...editorDataRef.current, title: value }
    setEditor(prev => ({ ...prev, title: value, saveStatus: 'idle' }))
    scheduleAutoSave()
  }, [scheduleAutoSave])

  const handleContentUpdate = useCallback(({ html, editor: editorInstance, selectionLength }) => {
    editorRef.current = editorInstance
    editorDataRef.current = { ...editorDataRef.current, content: html }
    setEditor(prev => ({ ...prev, content: html, saveStatus: 'idle' }))
    setGpt(prev => ({ ...prev, selectionLength }))
    scheduleAutoSave()
  }, [scheduleAutoSave])

  const handleSave = useCallback(() => {
    clearTimeout(saveTimerRef.current)
    doSave()
  }, [doSave])

  const handlePublish = useCallback(async () => {
    if (!storyIdRef.current) await doSave()
    if (!storyIdRef.current) {
      showToast('Save the story first', 'warning')
      return
    }
    try {
      await storiesAPI.update(storyIdRef.current, { visibility: 'public' })
      setEditor(prev => ({ ...prev, isPublished: true }))
      showToast('Story published!', 'success')
    } catch {
      showToast('Failed to publish', 'error')
    }
  }, [doSave, showToast])

  const handleBack = useCallback(() => {
    navigate(storyIdRef.current
      ? `/stories/${storyIdRef.current}`
      : worldId ? `/worlds/${worldId}` : '/stories')
  }, [navigate, worldId])

  const callGpt = useCallback(async (mode) => {
    const editorInstance = editorRef.current
    if (!editorInstance) return
    const { from, to } = editorInstance.state.selection
    const selected = editorInstance.state.doc.textBetween(from, to, ' ')
    if (selected.length < 10) return

    gptSelectionRef.current = { from, to }
    setGpt(prev => ({ ...prev, isLoading: true, suggestions: [] }))
    try {
      const res = await gptAPI.paraphrase(selected, mode)
      const suggestions = Array.isArray(res.data)
        ? res.data
        : res.data?.suggestions ?? [res.data?.result ?? '']
      setGpt(prev => ({ ...prev, isLoading: false, suggestions: suggestions.filter(Boolean) }))
    } catch {
      showToast('GPT error', 'error')
      setGpt(prev => ({ ...prev, isLoading: false, suggestions: [] }))
    }
  }, [showToast])

  const handleParaphrase = useCallback(() => callGpt('paraphrase'), [callGpt])
  const handleExpand = useCallback(() => callGpt('expand'), [callGpt])

  const handleApply = useCallback((suggestion) => {
    const editorInstance = editorRef.current
    const sel = gptSelectionRef.current
    if (!editorInstance || !sel) return
    editorInstance.chain().focus().deleteRange(sel).insertContent(suggestion).run()
    setGpt(prev => ({ ...prev, suggestions: [] }))
    gptSelectionRef.current = null
  }, [])

  const handleClearSuggestions = useCallback(() => {
    setGpt(prev => ({ ...prev, suggestions: [] }))
  }, [])

  const handleInsertSignature = useCallback(() => {
    const editorInstance = editorRef.current
    if (!editorInstance || !userSignature) return
    if (editorInstance.getText().includes(`— ${userSignature}`)) {
      showToast('Signature already in document', 'info')
      return
    }
    editorInstance.chain().focus().insertContent(`<p>— ${userSignature}</p>`).run()
  }, [userSignature, showToast])

  const gptProps = {
    ...gpt,
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
