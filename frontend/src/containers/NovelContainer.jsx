import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { novelAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import NovelView from '../components/novel/NovelView'

function NovelContainer({ showToast }) {
  const { worldId } = useParams()
  const { user } = useAuth()

  const [novel, setNovel] = useState(null)
  const [chapters, setChapters] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [editingMeta, setEditingMeta] = useState(false)
  const [metaForm, setMetaForm] = useState({ title: '', description: '' })
  const [savingMeta, setSavingMeta] = useState(false)

  useEffect(() => {
    load()
  }, [worldId])

  const load = async () => {
    try {
      setIsLoading(true)
      const res = await novelAPI.get(worldId)
      const data = res.data
      setNovel(data)
      setChapters(data.chapters || [])
      setMetaForm({ title: data.title || '', description: data.description || '' })
    } catch {
      showToast('Failed to load novel', 'error')
    } finally {
      setIsLoading(false)
    }
  }

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
      showToast('Novel updated', 'success')
    } catch {
      showToast('Failed to update novel', 'error')
    } finally {
      setSavingMeta(false)
    }
  }, [worldId, metaForm, showToast])

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
      showToast('Failed to save chapter order', 'error')
      setChapters(previous)
    }
  }, [worldId, showToast])

  return (
    <NovelView
      worldId={worldId}
      novel={novel}
      chapters={chapters}
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
  )
}

export default NovelContainer
