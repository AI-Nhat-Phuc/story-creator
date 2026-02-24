import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { worldsAPI, gptAPI, statsAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import GptButton, { OpenAILogo } from '../components/GptButton'
import {
  GlobeAltIcon,
  LockClosedIcon,
  UserIcon,
  MapPinIcon,
} from '@heroicons/react/24/outline'

function WorldsPage({ showToast }) {
  const { isAuthenticated, user } = useAuth()
  const [worlds, setWorlds] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [quota, setQuota] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    world_type: 'fantasy',
    visibility: 'public'
  })
  const [gptAnalyzing, setGptAnalyzing] = useState(false)
  const [gptEntities, setGptEntities] = useState(null)

  useEffect(() => {
    loadWorlds()
    if (isAuthenticated) {
      loadQuota()
    }
  }, [isAuthenticated])

  const loadWorlds = async () => {
    try {
      setLoading(true)
      const response = await worldsAPI.getAll()
      setWorlds(response.data)
    } catch (error) {
      showToast('Không thể tải danh sách thế giới', 'error')
    } finally {
      setLoading(false)
    }
  }

  const loadQuota = async () => {
    try {
      const response = await statsAPI.get()
      setQuota(response.data?.user_quota)
    } catch (error) {
      console.error('Không thể tải quota:', error)
    }
  }

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const generateDescriptionWithGPT = async () => {
    if (!isAuthenticated) {
      showToast('Vui lòng đăng nhập để sử dụng tính năng GPT', 'warning')
      return
    }
    if (!formData.name) {
      showToast('Vui lòng nhập tên thế giới trước', 'warning')
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
        const result = await gptAPI.getResults(taskId)
        console.log('[DEBUG] GPT Result:', result.data)
        if (result.data.status === 'completed') {
          // Extract description from result object
          const resultData = result.data.result
          console.log('[DEBUG] Result data:', resultData)
          const generatedDesc = 'description' in resultData
            ? resultData.description
            : (typeof resultData === 'string' ? resultData : '')
          console.log('[DEBUG] Generated desc:', generatedDesc)
          setFormData({ ...formData, description: generatedDesc })
          showToast('Đã tạo mô tả bằng GPT!', 'success')
          setGptAnalyzing(false)
        } else if (result.data.status === 'error') {
          showToast(result.data.result, 'error')
          setGptAnalyzing(false)
        } else {
          setTimeout(checkResults, 500)
        }
      }

      checkResults()
    } catch (error) {
      showToast('Lỗi tạo mô tả GPT', 'error')
      setGptAnalyzing(false)
    }
  }

  const analyzeWithGPT = async () => {
    if (!isAuthenticated) {
      showToast('Vui lòng đăng nhập để sử dụng tính năng phân tích GPT', 'warning')
      return
    }
    if (!formData.description) {
      showToast('Vui lòng nhập mô tả thế giới', 'warning')
      return
    }
    if (!formData.name) {
      showToast('Vui lòng nhập tên thế giới khi sử dụng GPT', 'warning')
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
        const result = await gptAPI.getResults(taskId)
        if (result.data.status === 'completed') {
          setGptEntities(result.data.result)
          showToast('Phân tích GPT hoàn tất!', 'success')
          setGptAnalyzing(false)
        } else if (result.data.status === 'error') {
          showToast(result.data.result, 'error')
          setGptAnalyzing(false)
        } else {
          setTimeout(checkResults, 500)
        }
      }

      checkResults()
    } catch (error) {
      showToast('Lỗi phân tích GPT', 'error')
      setGptAnalyzing(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!formData.name || !formData.description) {
      showToast('Vui lòng điền đầy đủ thông tin', 'warning')
      return
    }

    if (!isAuthenticated) {
      showToast('Vui lòng đăng nhập để sử dụng tính năng GPT', 'warning')
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
        const result = await gptAPI.getResults(taskId)
        if (result.data.status === 'completed') {
          const entities = result.data.result

          // Create world with GPT entities
          const payload = {
            ...formData,
            gpt_entities: entities
          }

          await worldsAPI.create(payload)
          showToast(`Tạo thế giới thành công! Phát hiện ${entities.characters?.length || 0} nhân vật, ${entities.locations?.length || 0} địa điểm`, 'success')
          setShowCreateModal(false)
          resetForm()
          setGptAnalyzing(false)
          loadWorlds()
        } else if (result.data.status === 'error') {
          showToast('Lỗi phân tích GPT: ' + result.data.result, 'error')
          setGptAnalyzing(false)
        } else {
          setTimeout(checkResults, 500)
        }
      }

      checkResults()
    } catch (error) {
      showToast('Không thể tạo thế giới', 'error')
      setGptAnalyzing(false)
    }
  }

  const resetForm = () => {
    setFormData({ name: '', description: '', world_type: 'fantasy', visibility: 'public' })
    setGptEntities(null)
  }

  const deleteWorld = async (worldId) => {
    if (!confirm('Bạn có chắc muốn xóa thế giới này?')) return

    try {
      await worldsAPI.delete(worldId)
      showToast('Đã xóa thế giới', 'success')
      loadWorlds()
    } catch (error) {
      showToast('Không thể xóa thế giới', 'error')
    }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="font-bold text-3xl"><GlobeAltIcon className="inline w-8 h-8" /> Thế giới</h1>
        {isAuthenticated ? (
          user?.role === 'admin' ? (
            <div className="tooltip-left tooltip" data-tip="Admin chỉ quản lý hệ thống, không tạo nội dung">
              <button className="btn btn-primary btn-disabled">
                + Tạo thế giới mới
              </button>
            </div>
          ) : (
            <button onClick={() => setShowCreateModal(true)} className="btn btn-primary">
              + Tạo thế giới mới
            </button>
          )
        ) : (
          <div className="tooltip-left tooltip" data-tip="Vui lòng đăng nhập để tạo thế giới">
            <button className="btn btn-primary btn-disabled">
              + Tạo thế giới mới
            </button>
          </div>
        )}
      </div>

      <div className="gap-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {worlds.map(world => (
          <div key={world.world_id} className="bg-base-100 shadow-xl card">
            <div className="card-body">
              <h2 className="card-title">{world.name}</h2>
              <p className="opacity-70 text-sm">{world.world_type}</p>
              <p className="line-clamp-3">{world.description}</p>
              <div className="justify-end mt-4 card-actions">
                <Link to={`/worlds/${world.world_id}`} className="btn btn-primary btn-sm">
                  Xem chi tiết
                </Link>
                {isAuthenticated && user?.user_id === world.owner_id && (
                  <button onClick={() => deleteWorld(world.world_id)} className="btn btn-error btn-sm">
                    Xóa
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
            {isAuthenticated
              ? 'Chưa có thế giới nào. Hãy tạo thế giới đầu tiên!'
              : 'Chưa có thế giới công khai nào. Vui lòng đăng nhập để tạo thế giới.'}
          </p>
        </div>
      )}

      {/* Create World Modal */}
      {showCreateModal && (
        <div className="modal modal-open">
          <div className="max-w-2xl modal-box">
            <h3 className="mb-4 font-bold text-lg">Tạo thế giới mới</h3>

            {/* Quota Alert */}
            {isAuthenticated && formData.visibility === 'public' && quota?.worlds && quota.worlds.current >= quota.worlds.limit && (
              <div className="mb-4 alert alert-error">
                <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current w-6 h-6 shrink-0" fill="none" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h3 className="font-bold">Đã đạt giới hạn thế giới công khai!</h3>
                  <div className="text-sm">Bạn đã tạo {quota.worlds.current}/{quota.worlds.limit} thế giới công khai. Vui lòng chọn chế độ Riêng tư hoặc xóa bớt thế giới công khai.</div>
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit}>
              {/* Visibility Option - Always Enabled */}
              <div className="mb-4 form-control">
                <label className="label">
                  <span className="font-semibold label-text">Chế độ hiển thị *</span>
                </label>
                <select
                  name="visibility"
                  value={formData.visibility}
                  onChange={handleInputChange}
                  className="select-bordered select"
                >
                  <option value="draft">Bản nháp - Chỉ bạn thấy, đang viết</option>
                  <option value="private">Riêng tư - Chỉ bạn có thể xem</option>
                  <option value="public">Công khai - Mọi người có thể xem</option>
                </select>
                {isAuthenticated && quota?.worlds && (
                  <label className="label">
                    <span className="label-text-alt">
                      {formData.visibility === 'public'
                        ? `Thế giới công khai: ${quota.worlds.current}/${quota.worlds.limit}`
                        : 'Thế giới riêng tư không giới hạn'}
                    </span>
                  </label>
                )}
              </div>

              <div className="mb-4 form-control">
                <label className="label">
                  <span className="label-text">Tên thế giới *</span>
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className="input input-bordered"
                  disabled={isAuthenticated && formData.visibility === 'public' && quota?.worlds && quota.worlds.current >= quota.worlds.limit}
                  required
                />
              </div>

              <div className="mb-4 form-control">
                <label className="label">
                  <span className="label-text">Loại thế giới</span>
                </label>
                <select
                  name="world_type"
                  value={formData.world_type}
                  onChange={handleInputChange}
                  className="select-bordered select"
                  disabled={isAuthenticated && formData.visibility === 'public' && quota?.worlds && quota.worlds.current >= quota.worlds.limit}
                >
                  <option value="fantasy">Fantasy - Thế giới phép thuật</option>
                  <option value="sci-fi">Sci-Fi - Khoa học viễn tưởng</option>
                  <option value="modern">Modern - Hiện đại</option>
                  <option value="historical">Historical - Lịch sử</option>
                </select>
              </div>

              <div className="mb-4 form-control">
                <div className='flex justify-between'>
                  <label className="label">
                    <span className="label-text">Mô tả *</span>
                  </label>
                  <GptButton
                    onClick={generateDescriptionWithGPT}
                    loading={gptAnalyzing}
                    loadingText="Đang tạo..."
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
                  className="h-32 textarea textarea-bordered"
                  placeholder="Nhập mô tả thế giới hoặc dùng GPT để tự động tạo... Ví dụ: Một thế giới giả tưởng với ma thuật, rồng và các vương quốc cổ đại..."
                  disabled={isAuthenticated && formData.visibility === 'public' && quota?.worlds && quota.worlds.current >= quota.worlds.limit}
                  required
                />
                <label className="label">
                  <span className="label-text-alt">{formData.description.length} ký tự</span>
                  <span className="label-text-alt text-gray-400">Click nút bên trên để GPT tạo mô tả tự động</span>
                </label>
              </div>

              {gptAnalyzing && (
                <div className="mb-4 alert alert-info">
                  <div>
                    <span className="loading loading-spinner"></span>
                    <span>Đang phân tích với GPT...</span>
                  </div>
                </div>
              )}

              {/* Preview analyze button */}
              {formData.description && !gptEntities && (
                <div className="mb-4">
                  <GptButton
                    onClick={analyzeWithGPT}
                    loading={gptAnalyzing}
                    loadingText="Đang phân tích..."
                    variant="primary"
                    size="sm"
                  >
                    Xem trước phân tích
                  </GptButton>
                </div>
              )}

              {/* GPT Entities Preview */}
              {gptEntities && (
                <div className="bg-base-200/50 mb-4 p-4 border border-base-300 rounded-xl">
                  <div className="w-full">
                    <div className="flex justify-between items-center mb-3">
                      <span className="flex items-center gap-2 font-semibold">
                        <span className="flex justify-center items-center bg-gradient-to-br from-emerald-500/20 to-teal-500/20 rounded-full w-6 h-6 text-emerald-600">
                          <OpenAILogo className="w-3.5 h-3.5" />
                        </span>
                        Kết quả phân tích
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
                      <p className="opacity-70 text-sm">Không phát hiện nhân vật hoặc địa điểm nào.</p>
                    )}
                  </div>
                </div>
              )}

              <div className="modal-action">
                <GptButton
                  onClick={handleSubmit}
                  loading={gptAnalyzing}
                  loadingText="Đang xử lý..."
                  variant="primary"
                  size="md"
                  disabled={isAuthenticated && formData.visibility === 'public' && quota?.worlds && quota.worlds.current >= quota.worlds.limit}
                >
                  Tạo & Phân tích
                </GptButton>
                <button type="button" onClick={() => { setShowCreateModal(false); resetForm() }} className="btn" disabled={gptAnalyzing}>Hủy</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default WorldsPage
