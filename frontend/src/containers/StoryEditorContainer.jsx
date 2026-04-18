import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useTranslation } from 'react-i18next'
import { usePageTitle } from '../hooks/usePageTitle'
import { storiesAPI, gptAPI, authAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import StoryEditorView from '../components/storyEditor/StoryEditorView'
import UnsavedChangesModal from '../components/storyEditor/UnsavedChangesModal'
import TitleSuggestionModal from '../components/storyEditor/TitleSuggestionModal'
import TurndownService from 'turndown'
import { marked } from 'marked'

const turndownSvc = new TurndownService({ headingStyle: 'atx', bulletListMarker: '-' })
const toMarkdown = (html) => turndownSvc.turndown(html || '')

const extractTitleSuggestion = (html) => {
  const text = (html || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
  return text.substring(0, 80).trim()
}

function StoryEditorContainer({ showToast }) {
  const { t } = useTranslation()
  const { storyId } = useParams()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { user, loading: authLoading } = useAuth()

  const worldId = searchParams.get('worldId')

  const [editor, setEditor] = useState({
    title: '',
    content: '',
    saveStatus: storyId ? 'idle' : 'new',
    isPublished: false,
    isLoading: true,
  })
  const [initialFormat, setInitialFormat] = useState('html')
  const [gpt, setGpt] = useState({ isLoading: false, suggestions: [], selectionLength: 0 })
  const [activeFormats, setActiveFormats] = useState({})
  const [signatures, setSignatures] = useState([])
  const [showUnsavedModal, setShowUnsavedModal] = useState(false)
  const [pendingNavigate, setPendingNavigate] = useState(null)
  const [showTitleModal, setShowTitleModal] = useState(false)
  const [titleSuggestion, setTitleSuggestion] = useState('')
  const [showSignatureModal, setShowSignatureModal] = useState(false)
  const editTitle = usePageTitle('storyEdit', editor.title || null)

  // Refs — mirror mutable values so doSave is always reading current data (no stale closures)
  const storyIdRef = useRef(storyId || null)
  const worldIdRef = useRef(worldId)
  const editorDataRef = useRef({ title: '', content: '' })
  const lastSavedRef = useRef({ title: '', content: '' })
  const saveTimerRef = useRef(null)
  const editorRef = useRef(null)
  const gptSelectionRef = useRef(null)

  useEffect(() => {
    if (!authLoading && user === null) {
      navigate('/login')
    }
  }, [user, authLoading, navigate])

  useEffect(() => {
    if (!user) return
    const storyLoad = storyId ? loadStory() : checkForDraft()
    Promise.all([storyLoad, loadUserSignatures()])
  }, [user, storyId])

  // Flush on unmount
  useEffect(() => {
    return () => {
      clearTimeout(saveTimerRef.current)
      doSave()
    }
  }, [])

  // Warn on browser close/refresh when dirty
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (isDirty()) {
        e.preventDefault()
        e.returnValue = ''
      }
    }
    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [])

  // Ctrl+S / Cmd+S keyboard shortcut — use ref so the handler is always current
  const handleSaveRef = useRef(null)
  useEffect(() => {
    const onKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
        handleSaveRef.current?.()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [])

  const loadStory = async () => {
    try {
      const res = await storiesAPI.getById(storyId)
      const data = res.data
      const title = data.title || ''
      const rawContent = data.content || ''
      const editorContent = data.format === 'markdown' ? marked.parse(rawContent) : rawContent
      const markdownBaseline = data.format === 'markdown' ? rawContent : toMarkdown(rawContent)
      storyIdRef.current = storyId
      setInitialFormat('html')
      editorDataRef.current = { title, content: editorContent }
      lastSavedRef.current = { title, content: markdownBaseline }
      setEditor({ title, content: editorContent, saveStatus: 'saved', isPublished: data.visibility === 'public', isLoading: false })
    } catch (err) {
      showToast(err.response?.status === 403 ? t('pages.storyEditor.accessDenied') : t('pages.storyEditor.storyNotFound'), 'error')
      navigate('/stories')
    }
  }

  const checkForDraft = async () => {
    if (!worldId) {
      showToast(t('pages.storyEditor.noWorld'), 'warning')
      navigate('/worlds')
      return
    }
    setEditor(prev => ({ ...prev, isLoading: false }))
  }

  const loadUserSignatures = async () => {
    try {
      const res = await authAPI.getCurrentUser()
      const meta = res.data?.metadata || {}
      // Support both new `signatures` array and legacy single `signature`
      const sigList = Array.isArray(meta.signatures) && meta.signatures.length > 0
        ? meta.signatures
        : (meta.signature ? [meta.signature] : [])
      setSignatures(sigList)
    } catch {
      // not critical
    }
  }

  const isDirty = useCallback(() => {
    const { title, content } = editorDataRef.current
    const markdownContent = toMarkdown(content)
    const last = lastSavedRef.current
    if (!storyIdRef.current) {
      return title.trim() !== '' || markdownContent.trim() !== ''
    }
    return title !== last.title || markdownContent !== last.content
  }, [])

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

  const doSave = useCallback(async () => {
    const { title, content } = editorDataRef.current
    const markdownContent = toMarkdown(content)
    const last = lastSavedRef.current
    if (title === last.title && markdownContent === last.content) return

    // Allow saving without title — fallback to "(no title)"
    const effectiveTitle = title.trim() || t('pages.storyEditor.titleNoTitle')

    setEditor(prev => ({ ...prev, saveStatus: 'saving' }))
    try {
      if (!storyIdRef.current) {
        const res = await storiesAPI.create({
          world_id: worldIdRef.current,
          title: effectiveTitle,
          content: markdownContent,
          visibility: 'draft',
          format: 'markdown',
        })
        storyIdRef.current = res.data.story_id
        lastSavedRef.current = { title: effectiveTitle, content: markdownContent }
        setEditor(prev => ({ ...prev, saveStatus: 'saved' }))
      } else {
        await storiesAPI.patch(storyIdRef.current, { title: effectiveTitle, content: markdownContent, format: 'markdown' })
        lastSavedRef.current = { title: effectiveTitle, content: markdownContent }
        setEditor(prev => ({ ...prev, saveStatus: 'saved' }))
      }
    } catch (err) {
      const msg = err.response?.data?.message || t('pages.storyEditor.saveError')
      showToast(msg, 'error')
      setEditor(prev => ({ ...prev, saveStatus: 'error' }))
    }
  }, [showToast, t])

  const scheduleAutoSave = useCallback(() => {
    clearTimeout(saveTimerRef.current)
    saveTimerRef.current = setTimeout(doSave, 30_000)
  }, [doSave])

  const handleTitleChange = useCallback((value) => {
    editorDataRef.current = { ...editorDataRef.current, title: value }
    setEditor(prev => ({ ...prev, title: value, saveStatus: 'idle' }))
    scheduleAutoSave()
  }, [scheduleAutoSave])

  const getActiveFormats = useCallback((ed) => ({
    bold: ed.isActive('bold'),
    italic: ed.isActive('italic'),
    underline: ed.isActive('underline'),
    strike: ed.isActive('strike'),
    highlight: ed.isActive('highlight'),
    h1: ed.isActive('heading', { level: 1 }),
    h2: ed.isActive('heading', { level: 2 }),
    h3: ed.isActive('heading', { level: 3 }),
    bulletList: ed.isActive('bulletList'),
    orderedList: ed.isActive('orderedList'),
    alignLeft: ed.isActive({ textAlign: 'left' }),
    alignCenter: ed.isActive({ textAlign: 'center' }),
    alignRight: ed.isActive({ textAlign: 'right' }),
  }), [])

  const handleContentUpdate = useCallback(({ html, editor: editorInstance, selectionLength }) => {
    editorRef.current = editorInstance
    editorDataRef.current = { ...editorDataRef.current, content: html }
    setEditor(prev => ({ ...prev, content: html, saveStatus: 'idle' }))
    setGpt(prev => ({ ...prev, selectionLength }))
    setActiveFormats(getActiveFormats(editorInstance))
    scheduleAutoSave()
  }, [scheduleAutoSave, getActiveFormats])

  const handleSelectionChange = useCallback(({ selectionLength, editor: editorInstance }) => {
    editorRef.current = editorInstance
    setGpt(prev => ({ ...prev, selectionLength }))
    setActiveFormats(getActiveFormats(editorInstance))
  }, [getActiveFormats])

  // Manual save — shows title modal if title is empty but content exists
  const handleSave = useCallback(() => {
    clearTimeout(saveTimerRef.current)
    const { title, content } = editorDataRef.current
    if (!title.trim() && (content || '').replace(/<[^>]+>/g, '').trim()) {
      setTitleSuggestion(extractTitleSuggestion(content))
      setShowTitleModal(true)
      return
    }
    doSave()
  }, [doSave])
  useEffect(() => { handleSaveRef.current = handleSave }, [handleSave])

  const handleTitleModalConfirm = useCallback((chosenTitle) => {
    setShowTitleModal(false)
    editorDataRef.current = { ...editorDataRef.current, title: chosenTitle }
    setEditor(prev => ({ ...prev, title: chosenTitle }))
    doSave()
  }, [doSave])

  const handleTitleModalSkip = useCallback(() => {
    setShowTitleModal(false)
    doSave()
  }, [doSave])

  const doNavigateBack = useCallback(() => {
    navigate(storyIdRef.current
      ? `/stories/${storyIdRef.current}`
      : worldId ? `/worlds/${worldId}` : '/stories')
  }, [navigate, worldId])

  const handleBack = useCallback(() => {
    if (isDirty()) {
      setPendingNavigate(() => doNavigateBack)
      setShowUnsavedModal(true)
      return
    }
    doNavigateBack()
  }, [isDirty, doNavigateBack])

  const handleUnsavedSave = useCallback(async () => {
    setShowUnsavedModal(false)
    await doSave()
    pendingNavigate?.()
    setPendingNavigate(null)
  }, [doSave, pendingNavigate])

  const handleUnsavedDiscard = useCallback(() => {
    setShowUnsavedModal(false)
    pendingNavigate?.()
    setPendingNavigate(null)
  }, [pendingNavigate])

  const handleUnsavedCancel = useCallback(() => {
    setShowUnsavedModal(false)
    setPendingNavigate(null)
  }, [])

  const handlePublish = useCallback(async () => {
    if (!storyIdRef.current) await doSave()
    if (!storyIdRef.current) {
      showToast(t('pages.storyEditor.saveFirst'), 'warning')
      return
    }
    try {
      await storiesAPI.update(storyIdRef.current, { visibility: 'public' })
      setEditor(prev => ({ ...prev, isPublished: true }))
      showToast(t('pages.storyEditor.published'), 'success')
    } catch {
      showToast(t('pages.storyEditor.publishError'), 'error')
    }
  }, [doSave, showToast, t])

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
      showToast(t('pages.storyEditor.gptError'), 'error')
      setGpt(prev => ({ ...prev, isLoading: false, suggestions: [] }))
    }
  }, [showToast, t])

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

  const handleInsertSignature = useCallback((sigText) => {
    const editorInstance = editorRef.current
    if (!editorInstance || !sigText) return
    if (editorInstance.getText().includes(`— ${sigText}`)) {
      showToast(t('pages.storyEditor.signatureExists'), 'info')
      return
    }
    editorInstance.chain().focus().insertContent(`<p>— ${sigText}</p>`).run()
  }, [showToast, t])

  const gptProps = {
    ...gpt,
    onParaphrase: handleParaphrase,
    onExpand: handleExpand,
    onApply: handleApply,
    onClear: handleClearSuggestions,
  }

  const pageTitle = storyId ? editTitle : t('meta.storyCreate.title')
  const pageDescription = storyId ? t('meta.storyEdit.description') : t('meta.storyCreate.description')

  return (
    <>
      <Helmet>
        <title>{pageTitle}</title>
        <meta name="description" content={pageDescription} />
      </Helmet>

      <StoryEditorView
        editor={editor}
        wordCount={wordCount}
        readTime={readTime}
        headings={headings}
        editorRef={editorRef}
        gpt={gptProps}
        activeFormats={activeFormats}
        signatures={signatures}
        showSignatureModal={showSignatureModal}
        onOpenSignatureModal={() => setShowSignatureModal(true)}
        onCloseSignatureModal={() => setShowSignatureModal(false)}
        onSignaturesChange={setSignatures}
        onInsertSignature={handleInsertSignature}
        onTitleChange={handleTitleChange}
        onContentUpdate={handleContentUpdate}
        onSelectionChange={handleSelectionChange}
        onSave={handleSave}
        onPublish={handlePublish}
        onBack={handleBack}
        initialFormat={initialFormat}
        showToast={showToast}
      />

      {showUnsavedModal && (
        <UnsavedChangesModal
          onSave={handleUnsavedSave}
          onDiscard={handleUnsavedDiscard}
          onCancel={handleUnsavedCancel}
        />
      )}

      {showTitleModal && (
        <TitleSuggestionModal
          suggestion={titleSuggestion}
          onConfirm={handleTitleModalConfirm}
          onSkip={handleTitleModalSkip}
          onCancel={() => setShowTitleModal(false)}
        />
      )}
    </>
  )
}

export default StoryEditorContainer
