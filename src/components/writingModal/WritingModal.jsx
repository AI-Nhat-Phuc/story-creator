'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useTranslation } from 'react-i18next'
import { useWritingModal } from '../../contexts/WritingModalContext'
import NovelEditor from '../storyEditor/NovelEditor'
import FormattingToolbar from '../storyEditor/FormattingToolbar'
import {
  PencilSquareIcon,
  MinusIcon,
  XMarkIcon,
  ArrowsPointingOutIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'

// Pages where the modal should be hidden (user is already in an editor)
const EDITOR_PATH_PATTERNS = [
  /^\/stories\/[^/]+\/edit(\/|$)/,
  /^\/stories\/new(\/|$)/,
  /^\/worlds\/[^/]+\/novel(\/|$)/,
]

function isEditorPage(pathname) {
  return EDITOR_PATH_PATTERNS.some((re) => re.test(pathname))
}

const STATUS_CONFIG = {
  idle: { label: 'writingModal.statusIdle', cls: 'text-base-content/40' },
  saving: { label: 'writingModal.statusSaving', cls: 'text-primary/60', icon: ArrowPathIcon },
  saved: { label: 'writingModal.statusSaved', cls: 'text-primary', icon: CheckCircleIcon },
  error: { label: 'writingModal.statusError', cls: 'text-error', icon: ExclamationCircleIcon },
}

function SaveStatusBadge({ status }) {
  const { t } = useTranslation()
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.idle
  const Icon = cfg.icon
  return (
    <span className={`flex items-center gap-1 text-xs ${cfg.cls}`}>
      {Icon && <Icon className={`w-3 h-3 ${status === 'saving' ? 'animate-spin' : ''}`} />}
      {t(cfg.label)}
    </span>
  )
}

function MinimizedButton({ onClick }) {
  const { t } = useTranslation()
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 z-50 hidden md:flex items-center gap-2 btn btn-primary shadow-xl rounded-full pl-4 pr-5"
      title={t('writingModal.openDraft')}
    >
      <PencilSquareIcon className="w-5 h-5" />
      <span className="text-sm font-medium">{t('writingModal.continueDraft')}</span>
    </button>
  )
}

function WritingModal() {
  const { t } = useTranslation()
  const router = useRouter()
  const pathname = usePathname()
  const {
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
  } = useWritingModal()

  const [activeFormats, setActiveFormats] = useState({})
  const onEditor = isEditorPage(pathname)

  // Auto-minimize when user navigates into an editor page
  useEffect(() => {
    if (onEditor && modalState === 'open') {
      minimizeModal()
    }
  }, [onEditor, modalState, minimizeModal])

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

  const handleEditorUpdate = useCallback(({ html, editor }) => {
    handleContentUpdate({ html })
    setActiveFormats(getActiveFormats(editor))
  }, [handleContentUpdate, getActiveFormats])

  const handleSelectionChange = useCallback(({ editor }) => {
    setActiveFormats(getActiveFormats(editor))
  }, [getActiveFormats])

  const handleMaximize = useCallback(async () => {
    // Use ref to avoid stale closure — storyIdRef always has the current value
    const sid = storyIdRef.current
    if (!sid) {
      // No saved story yet — save first, then navigate
      await handleSave()
      const newSid = storyIdRef.current
      if (newSid) {
        minimizeModal()
        router.push(`/stories/${newSid}/edit`)
      }
      return
    }
    handleSave()
    minimizeModal()
    router.push(`/stories/${sid}/edit`)
  }, [storyIdRef, handleSave, minimizeModal, router])

  const canPublish = draft.saveStatus === 'saved' && !draft.isPublished && !!draft.storyId

  // Nothing to show when closed, or when on an editor page
  if (modalState === 'closed') return null

  // On editor pages: hide everything (user is already editing)
  if (onEditor) return null

  if (modalState === 'minimized') {
    return <MinimizedButton onClick={openModal} />
  }

  return (
    // Hidden on mobile — full editor page is used on small screens
    <div className="hidden md:flex fixed bottom-0 right-6 z-50 flex-col w-[38%] min-w-[340px] max-w-[560px] h-[60vh] min-h-[400px] bg-base-100 border border-base-300 rounded-t-xl shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 bg-base-200 border-b border-base-300 shrink-0">
        <div className="flex items-center gap-2 min-w-0">
          <PencilSquareIcon className="w-4 h-4 text-primary shrink-0" />
          <input
            type="text"
            value={draft.title}
            onChange={(e) => handleTitleChange(e.target.value)}
            placeholder={t('writingModal.titlePlaceholder')}
            className="input input-ghost input-xs text-sm font-medium w-full min-w-0 focus:outline-none px-0"
          />
        </div>
        <div className="flex items-center gap-1 shrink-0 ml-2">
          <SaveStatusBadge status={draft.saveStatus} />
          <div className="w-px h-4 bg-base-300 mx-1" />
          <button
            onClick={minimizeModal}
            className="btn btn-ghost btn-xs h-7 min-h-0 px-1.5"
            title={t('writingModal.minimize')}
          >
            <MinusIcon className="w-4 h-4" />
          </button>
          <button
            onClick={handleMaximize}
            className="btn btn-ghost btn-xs h-7 min-h-0 px-1.5"
            title={t('writingModal.maximize')}
          >
            <ArrowsPointingOutIcon className="w-4 h-4" />
          </button>
          <button
            onClick={closeModal}
            className="btn btn-ghost btn-xs h-7 min-h-0 px-1.5 text-error hover:bg-error/10"
            title={t('writingModal.close')}
          >
            <XMarkIcon className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Toolbar */}
      <FormattingToolbar editorRef={editorRef} activeFormats={activeFormats} />

      {/* Editor body */}
      <div className="flex-1 overflow-y-auto relative">
        {draft.isLoading ? (
          <div className="flex items-center justify-center h-full">
            <span className="loading loading-spinner loading-sm text-primary" />
          </div>
        ) : (
          <NovelEditor
            key={draft.storyId ?? 'new'}
            initialContent={draft.content}
            format="html"
            editorRef={editorRef}
            onUpdate={handleEditorUpdate}
            onSelectionChange={handleSelectionChange}
          />
        )}
      </div>

      {/* Footer actions */}
      <div className="flex items-center justify-end gap-2 px-3 py-2 border-t border-base-300 bg-base-100 shrink-0">
        <button
          onClick={handleSave}
          disabled={draft.saveStatus === 'saving'}
          className="btn btn-sm btn-ghost"
        >
          {t('writingModal.save')}
        </button>
        <button
          onClick={handlePublish}
          disabled={!canPublish || draft.saveStatus === 'saving'}
          className="btn btn-sm btn-primary"
        >
          {t('writingModal.publish')}
        </button>
      </div>
    </div>
  )
}

export default WritingModal
