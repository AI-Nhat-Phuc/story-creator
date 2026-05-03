'use client'

import { useState, useEffect, useRef } from 'react'
import { Link } from '../utils/router-compat'
import { useTranslation } from 'react-i18next'
import { worldsAPI, gptAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import LoadingSpinner from '../components/LoadingSpinner'
import GptButton from '../components/GptButton'
import {
  GlobeAltIcon,
  LockClosedIcon,
  UserIcon,
  BookOpenIcon,
} from '@heroicons/react/24/outline'
import Tag from '../components/Tag'

function WorldsPage({ initialWorlds }) {
  const { showToast } = useToast()
  const { t } = useTranslation()
  const { isAuthenticated, user, loading: authLoading, canUseGpt } = useAuth()

  // Skip the initial client-side fetch when SSR pre-fetched public worlds.
  // Re-fetch still fires when the user authenticates (private worlds become visible).
  const hasSSRData = initialWorlds != null
  const skipFirstFetch = useRef(hasSSRData)
  const [worlds, setWorlds] = useState(initialWorlds ?? [])
  const [loading, setLoading] = useState(!hasSSRData)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    world_type: 'fantasy',
  })
  const [gptAnalyzing, setGptAnalyzing] = useState(false)
  const dialogRef = useRef(null)

  useEffect(() => {
    if (skipFirstFetch.current) {
      skipFirstFetch.current = false
      return
    }
    loadWorlds()
  }, [isAuthenticated])

  // Sync native <dialog> open/close state with React state
  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return
    if (showCreateModal) {
      if (!dialog.open) dialog.showModal()
    } else {
      if (dialog.open) dialog.close()
    }
  }, [showCreateModal])

  const handleClose = () => {
    setShowCreateModal(false)
    resetForm()
  }

  const loadWorlds = async () => {
    try {
      setLoading(true)
      const response = await worldsAPI.getAll()
      setWorlds(response.data)
    } catch (error) {
      showToast(t('pages.worlds.toast.loadError'), 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const generateDescriptionWithGPT = async () => {
    if (!isAuthenticated) {
      showToast(t('pages.worlds.toast.loginRequired'), 'warning')
      return
    }
    if (!formData.name) {
      showToast(t('pages.worlds.toast.nameRequired'), 'warning')
      return
    }

    try {
      setGptAnalyzing(true)
      const response = await gptAPI.generateDescription({
        type: 'world',
        world_name: formData.name,
        world_type: formData.world_type
      })

      const taskId = response.data.task_id

      // Poll for results
      const checkResults = async () => {
        try {
          const result = await gptAPI.getResults(taskId)
          if (result.data.status === 'completed') {
            // Extract description from result object
            const resultData = result.data.result
            const generatedDesc = 'description' in resultData
              ? resultData.description
              : (typeof resultData === 'string' ? resultData : '')
            setFormData(prev => ({ ...prev, description: generatedDesc }))
            showToast(t('pages.worlds.toast.gptDescDone'), 'success')
            setGptAnalyzing(false)
          } else if (result.data.status === 'error') {
            showToast(result.data.result, 'error')
            setGptAnalyzing(false)
          } else {
            setTimeout(checkResults, 500)
          }
        } catch (err) {
          showToast(t('pages.worlds.toast.gptDescError'), 'error')
          setGptAnalyzing(false)
        }
      }

      checkResults()
    } catch (error) {
      showToast(t('pages.worlds.toast.gptDescError'), 'error')
      setGptAnalyzing(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!formData.name || !formData.description) {
      showToast(t('pages.worlds.toast.fillRequired'), 'warning')
      return
    }

    if (!isAuthenticated) {
      showToast(t('pages.worlds.toast.loginToCreate'), 'warning')
      return
    }

    try {
      setGptAnalyzing(true)
      await worldsAPI.create(formData)
      showToast(t('pages.worlds.toast.createSuccess', { chars: 0, locs: 0 }), 'success')
      setShowCreateModal(false)
      loadWorlds()
    } catch (error) {
      showToast(t('pages.worlds.toast.createError'), 'error')
    } finally {
      setGptAnalyzing(false)
    }
  }

  const resetForm = () => {
    setFormData({ name: '', description: '', world_type: 'fantasy' })
  }

  const deleteWorld = async (worldId) => {
    if (!confirm(t('pages.worlds.deleteConfirm'))) return

    try {
      await worldsAPI.delete(worldId)
      showToast(t('pages.worlds.toast.deleteSuccess'), 'success')
      loadWorlds()
    } catch (error) {
      showToast(t('pages.worlds.toast.deleteError'), 'error')
    }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="font-bold text-3xl"><GlobeAltIcon className="inline w-8 h-8" /> {t('pages.worlds.title')}</h1>
        {authLoading ? (
          <button className="btn btn-primary" disabled>
            <span className="loading loading-spinner loading-xs"></span>
          </button>
        ) : isAuthenticated ? (
          user?.role === 'admin' ? (
            <div className="tooltip-left tooltip" data-tip={t('pages.worlds.adminTooltip')}>
              <button className="btn btn-primary btn-disabled">
                {t('pages.worlds.createBtn')}
              </button>
            </div>
          ) : (
            <button onClick={() => setShowCreateModal(true)} className="btn btn-primary">
              {t('pages.worlds.createBtn')}
            </button>
          )
        ) : (
          <div className="tooltip-left tooltip" data-tip={t('pages.worlds.loginTooltip')}>
            <button className="btn btn-primary btn-disabled">
              {t('pages.worlds.createBtn')}
            </button>
          </div>
        )}
      </div>

      <div className="gap-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {worlds.map(world => (
          <div key={world.world_id} className="bg-base-100 shadow-xl card">
            <div className="card-body">
              <h2 className="card-title">{world.name}</h2>
              <div className="flex flex-wrap items-center gap-2">
                <span className="opacity-70 text-sm">{world.world_type}</span>
                <Tag color={world.visibility === 'public' ? 'success' : world.visibility === 'draft' ? 'warning' : 'ghost'} size="sm">
                  {t(`common.${world.visibility || 'private'}`)}
                </Tag>
                <span className="flex items-center gap-1 opacity-60 text-xs">
                  <BookOpenIcon className="w-3.5 h-3.5" />
                  {t('common.storiesCount', { count: world.stories?.length ?? 0 })}
                </span>
                {world.owner_username && (
                  <span className="flex items-center gap-1 opacity-60 text-xs">
                    <UserIcon className="w-3.5 h-3.5" />
                    {world.owner_username}
                  </span>
                )}
              </div>
              <p className="line-clamp-3">{world.description}</p>
              <div className="justify-end mt-4 card-actions">
                <Link to={`/worlds/${world.world_id}`} className="btn btn-primary btn-sm">
                  {t('pages.worlds.viewDetail')}
                </Link>
                {isAuthenticated && user?.user_id === world.owner_id && (
                  <button onClick={() => deleteWorld(world.world_id)} className="btn btn-error btn-sm">
                    {t('actions.delete')}
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {worlds.length === 0 && (
        <div className="py-12 text-center">
          <p className="opacity-60 text-xl">
            {isAuthenticated ? t('pages.worlds.emptyAuth') : t('pages.worlds.emptyAnon')}
          </p>
        </div>
      )}

      {/* Create World Modal */}
      <dialog
        ref={dialogRef}
        className="modal modal-bottom-sheet"
        onClose={handleClose}
        onCancel={(e) => { if (gptAnalyzing) e.preventDefault() }}
        onClick={(e) => { if (e.target === dialogRef.current && !gptAnalyzing) dialogRef.current.close() }}
      >
          <div className="max-w-2xl modal-box">
            <h3 className="mb-4 font-bold text-lg">{t('pages.worlds.createModal')}</h3>

            <form onSubmit={handleSubmit}>
              <div className="mb-4 form-control">
                <label className="label">
                  <span className="label-text">{t('pages.worlds.worldName')}</span>
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className="input input-bordered"
                  required
                />
              </div>

              <div className="mb-4 form-control">
                <label className="label">
                  <span className="label-text">{t('pages.worlds.worldType')}</span>
                </label>
                <select
                  name="world_type"
                  value={formData.world_type}
                  onChange={handleInputChange}
                  className="select-bordered select"
                >
                  <option value="fantasy">{t('pages.worlds.worldTypes.fantasy')}</option>
                  <option value="sci-fi">{t('pages.worlds.worldTypes.sci-fi')}</option>
                  <option value="modern">{t('pages.worlds.worldTypes.modern')}</option>
                  <option value="historical">{t('pages.worlds.worldTypes.historical')}</option>
                </select>
              </div>

              <div className="mb-4 form-control">
                <div className='flex justify-between items-center mb-1'>
                  <label className="label py-0">
                    <span className="label-text">{t('pages.worlds.description')}</span>
                  </label>
                  {canUseGpt && (
                    <GptButton
                      onClick={generateDescriptionWithGPT}
                      loading={gptAnalyzing}
                      loadingText={t('pages.worlds.gptGenerating')}
                      disabled={!formData.name}
                      variant="secondary"
                      size="xs"
                    >
                      Tạo mô tả
                    </GptButton>
                  )}
                </div>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  className="h-48 sm:h-32 textarea textarea-bordered"
                  placeholder={t('pages.worlds.descPlaceholder')}
                  required
                />
                <label className="label">
                  <span className="label-text-alt">{t('pages.worlds.charCount', { count: formData.description.length })}</span>
                </label>
              </div>

              <div className="modal-action">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={gptAnalyzing}
                >
                  {gptAnalyzing ? (
                    <><span className="loading loading-spinner loading-xs" />{t('actions.processing')}</>
                  ) : t('pages.worlds.createBtn')}
                </button>
                <button type="button" onClick={() => dialogRef.current?.close()} className="btn" disabled={gptAnalyzing}>{t('common.cancel')}</button>
              </div>
            </form>
          </div>
      </dialog>
    </div>
  )
}

export default WorldsPage
