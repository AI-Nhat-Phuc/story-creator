import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useTranslation } from 'react-i18next'
import { worldsAPI, gptAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import GptButton, { OpenAILogo } from '../components/GptButton'
import {
  GlobeAltIcon,
  LockClosedIcon,
  UserIcon,
  MapPinIcon,
  ArrowPathIcon,
  BookOpenIcon,
} from '@heroicons/react/24/outline'
import Tag from '../components/Tag'

function WorldsPage({ showToast }) {
  const { t } = useTranslation()
  const { isAuthenticated, user, loading: authLoading } = useAuth()
  const [worlds, setWorlds] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    world_type: 'fantasy',
  })
  const [gptAnalyzing, setGptAnalyzing] = useState(false)
  const [gptEntities, setGptEntities] = useState(null)
  const dialogRef = useRef(null)

  useEffect(() => {
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

  const analyzeWithGPT = async () => {
    if (!isAuthenticated) {
      showToast(t('pages.worlds.toast.loginRequired'), 'warning')
      return
    }
    if (!formData.description) {
      showToast(t('pages.worlds.toast.descRequired'), 'warning')
      return
    }
    if (!formData.name) {
      showToast(t('pages.worlds.toast.nameRequiredGpt'), 'warning')
      return
    }

    try {
      setGptAnalyzing(true)
      const response = await gptAPI.analyze({
        world_description: formData.description,
        world_type: formData.world_type
      })

      const taskId = response.data.task_id

      // Poll for results
      const checkResults = async () => {
        try {
          const result = await gptAPI.getResults(taskId)
          if (result.data.status === 'completed') {
            setGptEntities(result.data.result)
            showToast(t('pages.worlds.toast.gptAnalysisDone'), 'success')
            setGptAnalyzing(false)
          } else if (result.data.status === 'error') {
            showToast(result.data.result, 'error')
            setGptAnalyzing(false)
          } else {
            setTimeout(checkResults, 500)
          }
        } catch (err) {
          showToast(t('pages.worlds.toast.gptAnalysisError'), 'error')
          setGptAnalyzing(false)
        }
      }

      checkResults()
    } catch (error) {
      showToast(t('pages.worlds.toast.gptAnalysisError'), 'error')
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

      // Auto-analyze with GPT
      const gptResponse = await gptAPI.analyze({
        world_description: formData.description,
        world_type: formData.world_type
      })

      const taskId = gptResponse.data.task_id

      // Poll for GPT results
      const checkResults = async () => {
        try {
          const result = await gptAPI.getResults(taskId)
          if (result.data.status === 'completed') {
            const entities = result.data.result

            // Create world with GPT entities
            const payload = {
              ...formData,
              gpt_entities: entities
            }

            await worldsAPI.create(payload)
            showToast(t('pages.worlds.toast.createSuccess', { chars: entities.characters?.length || 0, locs: entities.locations?.length || 0 }), 'success')
            setShowCreateModal(false)
            setGptAnalyzing(false)
            loadWorlds()
          } else if (result.data.status === 'error') {
            showToast(t('pages.worlds.toast.createError'), 'error')
            setGptAnalyzing(false)
          } else {
            setTimeout(checkResults, 500)
          }
        } catch (err) {
          showToast(t('pages.worlds.toast.createError'), 'error')
          setGptAnalyzing(false)
        }
      }

      checkResults()
    } catch (error) {
      showToast(t('pages.worlds.toast.createError'), 'error')
      setGptAnalyzing(false)
    }
  }

  const resetForm = () => {
    setFormData({ name: '', description: '', world_type: 'fantasy' })
    setGptEntities(null)
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
      <Helmet>
        <title>{t('meta.worlds.title')}</title>
        <meta name="description" content={t('meta.worlds.description')} />
      </Helmet>
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
                  <span className="label-text-alt text-base-content/40">{t('pages.worlds.gptHint')}</span>
                </label>
              </div>

              {/* GPT Entities Preview */}
              {gptEntities && (
                <div className="bg-base-200/50 mb-4 p-4 border border-base-300 rounded-xl">
                  <div className="w-full">
                    <div className="flex justify-between items-center mb-3">
                      <span className="flex items-center gap-2 font-semibold">
                        <span className="flex justify-center items-center bg-gradient-to-br from-emerald-500/20 to-teal-500/20 rounded-full w-6 h-6 text-emerald-600">
                          <OpenAILogo className="w-3.5 h-3.5" />
                        </span>
                        {t('pages.worlds.analysisResult')}
                      </span>
                      <button
                        type="button"
                        onClick={() => setGptEntities(null)}
                        className="opacity-50 hover:opacity-100 btn btn-ghost btn-xs btn-circle"
                      >
                        ✕
                      </button>
                    </div>
                    {gptEntities.characters?.length > 0 && (
                      <div className="mb-3">
                        <span className="opacity-70 text-sm"><UserIcon className="inline w-3.5 h-3.5" /> Nhân vật ({gptEntities.characters.length}):</span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {gptEntities.characters.map((char, i) => (
                            <span key={i} className="bg-primary/10 px-2 py-1 border border-primary/30 rounded-lg font-medium text-primary text-sm">
                              {char.name} - {char.entity_type}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {gptEntities.locations?.length > 0 && (
                      <div>
                        <span className="opacity-70 text-sm"><MapPinIcon className="inline w-3.5 h-3.5" /> Địa điểm ({gptEntities.locations.length}):</span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {gptEntities.locations.map((loc, i) => (
                            <span key={i} className="bg-secondary/10 px-2 py-1 border border-secondary/30 rounded-lg font-medium text-secondary text-sm">
                              {loc.name} - {loc.location_type}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {(!gptEntities.characters?.length && !gptEntities.locations?.length) && (
                      <p className="opacity-70 text-sm">{t('pages.worlds.noEntities')}</p>
                    )}
                  </div>
                </div>
              )}

              <div className="modal-action">
                <GptButton
                  onClick={handleSubmit}
                  loading={gptAnalyzing}
                  loadingText={t('actions.processing')}
                  variant="primary"
                  size="md"
                >
                  {t('pages.worlds.createAndAnalyze')}
                </GptButton>
                <button type="button" onClick={() => dialogRef.current?.close()} className="btn" disabled={gptAnalyzing}>{t('common.cancel')}</button>
              </div>
            </form>
          </div>
      </dialog>
    </div>
  )
}

export default WorldsPage
