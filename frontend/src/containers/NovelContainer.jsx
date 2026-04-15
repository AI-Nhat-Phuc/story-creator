import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useTranslation } from 'react-i18next'
import { usePageTitle } from '../hooks/usePageTitle'
import { novelAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import NovelView from '../components/novel/NovelView'

const LINE_BUDGET = 100

function NovelContainer({ showToast }) {
  const { t } = useTranslation()
  const { worldId } = useParams()
  const { user } = useAuth()

  const [novel, setNovel] = useState(null)
  const [chapters, setChapters] = useState([])
  const [contentBlocks, setContentBlocks] = useState([])
  const [nextCursor, setNextCursor] = useState(null)
  const [hasMore, setHasMore] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingMore, setIsLoadingMore] = useState(false)
  // Synchronous guard against observer double-fires (state updates lag).
  const loadingMoreRef = useRef(false)
  const [editingMeta, setEditingMeta] = useState(false)
  const [metaForm, setMetaForm] = useState({ title: '', description: '' })
  const [savingMeta, setSavingMeta] = useState(false)
  const novelTitle = usePageTitle('novel', novel?.title)
  const novelDescription = novel?.title
    ? t('meta.novel.descriptionTemplate', { name: novel.title })
    : t('meta.novel.descriptionFallback')

  useEffect(() => {
    load()
  }, [worldId])

  const load = async () => {
    try {
      setIsLoading(true)
      const [metaRes, contentRes] = await Promise.all([
        novelAPI.get(worldId),
        novelAPI.getContent(worldId, { lineBudget: LINE_BUDGET }),
      ])
      setNovel(metaRes.data)
      setChapters(metaRes.data.chapters || [])
      setMetaForm({ title: metaRes.data.title || '', description: metaRes.data.description || '' })

      setContentBlocks(contentRes.data.blocks || [])
      setNextCursor(contentRes.data.next_cursor)
      setHasMore(contentRes.data.has_more)
    } catch {
      showToast(t('pages.novel.loadError'), 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const loadMore = useCallback(async () => {
    if (!hasMore || loadingMoreRef.current || !nextCursor) return
    loadingMoreRef.current = true
    setIsLoadingMore(true)
    try {
      const res = await novelAPI.getContent(worldId, {
        cursor: nextCursor,
        lineBudget: LINE_BUDGET,
      })
      const newBlocks = res.data.blocks || []
      setContentBlocks(prev => [...prev, ...newBlocks])
      setNextCursor(res.data.next_cursor)
      setHasMore(res.data.has_more)
    } catch {
      showToast(t('pages.novel.loadMoreError'), 'error')
    } finally {
      loadingMoreRef.current = false
      setIsLoadingMore(false)
    }
  }, [worldId, nextCursor, hasMore, showToast, t])

  const totalWordCount = useMemo(
    () => chapters.reduce((sum, ch) => sum + (ch.word_count || 0), 0),
    [chapters]
  )

  const isOwner = !!(novel?.owner_id && user?.user_id === novel.owner_id)
  const isCoAuthor = !!(user && novel?.co_authors?.includes(user.user_id))
  const canEdit = isOwner
  const canReorder = isOwner || isCoAuthor

  const handleEditMeta = useCallback(() => setEditingMeta(true), [])
  const handleCancelMeta = useCallback(() => {
    setMetaForm({ title: novel?.title || '', description: novel?.description || '' })
    setEditingMeta(false)
  }, [novel])

  const handleSaveMeta = useCallback(async () => {
    setSavingMeta(true)
    try {
      const res = await novelAPI.update(worldId, metaForm)
      setNovel(prev => ({ ...prev, ...res.data }))
      setEditingMeta(false)
      showToast(t('pages.novel.updateSuccess'), 'success')
    } catch {
      showToast(t('pages.novel.updateError'), 'error')
    } finally {
      setSavingMeta(false)
    }
  }, [worldId, metaForm, showToast, t])

  const handleMetaFormChange = useCallback((field, value) => {
    setMetaForm(prev => ({ ...prev, [field]: value }))
  }, [])

  const chaptersRef = useRef(chapters)
  useEffect(() => { chaptersRef.current = chapters }, [chapters])

  const handleReorder = useCallback(async (reordered) => {
    const previous = chaptersRef.current
    setChapters(reordered)
    try {
      await novelAPI.reorderChapters(worldId, reordered.map(c => c.story_id))
    } catch {
      showToast(t('pages.novel.reorderError'), 'error')
      setChapters(previous)
    }
  }, [worldId, showToast, t])

  return (
    <>
      <Helmet>
        <title>{novelTitle}</title>
        <meta name="description" content={novelDescription} />
      </Helmet>
      <NovelView
        worldId={worldId}
        novel={novel}
        chapters={chapters}
        contentBlocks={contentBlocks}
        hasMore={hasMore}
        isLoadingMore={isLoadingMore}
        onLoadMore={loadMore}
        totalWordCount={totalWordCount}
        isLoading={isLoading}
        canEdit={canEdit}
        canReorder={canReorder}
        editingMeta={editingMeta}
        metaForm={metaForm}
        savingMeta={savingMeta}
        onEditMeta={handleEditMeta}
        onCancelMeta={handleCancelMeta}
        onSaveMeta={handleSaveMeta}
        onMetaFormChange={handleMetaFormChange}
        onReorder={handleReorder}
      />
    </>
  )
}

export default NovelContainer
