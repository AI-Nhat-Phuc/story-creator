import React, { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  MagnifyingGlassIcon,
  PaperAirplaneIcon,
  ArrowPathIcon,
  ChatBubbleLeftEllipsisIcon,
  HandThumbUpIcon,
  ShareIcon,
  SparklesIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  KeyIcon,
  ClipboardDocumentIcon,
} from '@heroicons/react/24/outline'
import { facebookAPI, gptAPI } from '../services/api'

const ACCESS_KEY = 'story-creator-fb-2024'

export default function FacebookPage({ showToast }) {
  const [searchParams] = useSearchParams()
  const key = searchParams.get('key')

  // Auth / page selection state
  const [fbToken, setFbToken] = useState('')
  const [pages, setPages] = useState([])
  const [selectedPage, setSelectedPage] = useState(null)
  const [userInfo, setUserInfo] = useState(null)

  // Posts state
  const [posts, setPosts] = useState([])
  const [loadingPosts, setLoadingPosts] = useState(false)

  // Search
  const [searchKeyword, setSearchKeyword] = useState('')
  const [searchResults, setSearchResults] = useState(null)

  // Create post
  const [newMessage, setNewMessage] = useState('')
  const [newLink, setNewLink] = useState('')
  const [newImageUrl, setNewImageUrl] = useState('')
  const [publishing, setPublishing] = useState(false)

  // GPT generate
  const [gptTopic, setGptTopic] = useState('')
  const [gptRequirements, setGptRequirements] = useState('')
  const [gptTone, setGptTone] = useState('professional')
  const [generating, setGenerating] = useState(false)

  // Comments modal
  const [comments, setComments] = useState([])
  const [commentsPostId, setCommentsPostId] = useState(null)
  const [loadingComments, setLoadingComments] = useState(false)

  // --- Access gate ---
  if (key !== ACCESS_KEY) {
    return (
      <div className="flex flex-col justify-center items-center min-h-[60vh] text-center">
        <KeyIcon className="mx-auto mb-4 w-16 h-16 text-warning" />
        <h2 className="mb-2 font-bold text-2xl">Truy cập bị từ chối</h2>
        <p className="text-base-content/60">
          Bạn cần cung cấp đúng <code className="badge badge-outline">key</code> trong URL để truy cập trang này.
        </p>
        <p className="mt-2 text-sm text-base-content/40">
          Ví dụ: <code>/facebook?key=YOUR_KEY</code>
        </p>
      </div>
    )
  }

  // --- Handlers ---

  const handleConnect = async () => {
    if (!fbToken.trim()) {
      showToast('Vui lòng nhập Facebook Access Token', 'warning')
      return
    }
    try {
      const meRes = await facebookAPI.getMe(fbToken)
      setUserInfo(meRes.data)

      const pagesRes = await facebookAPI.getPages(fbToken)
      setPages(pagesRes.data?.data || [])
      showToast(`Đã kết nối với tài khoản: ${meRes.data.name}`, 'success')
    } catch (err) {
      showToast('Kết nối thất bại: ' + (err.response?.data?.error || err.message), 'error')
    }
  }

  const handleSelectPage = async (page) => {
    setSelectedPage(page)
    setSearchResults(null)
    await loadPosts(page.id, page.access_token)
  }

  const loadPosts = async (pageId, token) => {
    setLoadingPosts(true)
    try {
      const res = await facebookAPI.getPagePosts(pageId, token)
      setPosts(res.data?.data || [])
    } catch (err) {
      showToast('Lỗi tải bài viết: ' + (err.response?.data?.error || err.message), 'error')
    } finally {
      setLoadingPosts(false)
    }
  }

  const handleSearch = async () => {
    if (!searchKeyword.trim() || !selectedPage) return
    setLoadingPosts(true)
    try {
      const res = await facebookAPI.searchPosts(
        selectedPage.id, selectedPage.access_token, searchKeyword
      )
      setSearchResults(res.data?.data || [])
    } catch (err) {
      showToast('Lỗi tìm kiếm: ' + (err.response?.data?.error || err.message), 'error')
    } finally {
      setLoadingPosts(false)
    }
  }

  const handlePublish = async () => {
    if (!selectedPage) return
    if (!newMessage.trim() && !newLink.trim() && !newImageUrl.trim()) {
      showToast('Vui lòng nhập nội dung bài đăng', 'warning')
      return
    }
    setPublishing(true)
    try {
      await facebookAPI.createPost(selectedPage.id, {
        fb_token: selectedPage.access_token,
        message: newMessage,
        link: newLink,
        image_url: newImageUrl,
      })
      showToast('Đăng bài thành công!', 'success')
      setNewMessage('')
      setNewLink('')
      setNewImageUrl('')
      await loadPosts(selectedPage.id, selectedPage.access_token)
    } catch (err) {
      showToast('Đăng bài thất bại: ' + (err.response?.data?.error || err.message), 'error')
    } finally {
      setPublishing(false)
    }
  }

  const handleGenerate = async () => {
    if (!gptTopic.trim()) {
      showToast('Vui lòng nhập chủ đề', 'warning')
      return
    }
    setGenerating(true)
    try {
      const res = await facebookAPI.generateContent({
        topic: gptTopic,
        requirements: gptRequirements,
        tone: gptTone,
      })
      const taskId = res.data.task_id

      const poll = async () => {
        const result = await gptAPI.getResults(taskId)
        if (result.data.status === 'completed') {
          setNewMessage(result.data.result.content)
          setGenerating(false)
          showToast('Đã tạo nội dung!', 'success')
        } else if (result.data.status === 'error') {
          showToast(result.data.result, 'error')
          setGenerating(false)
        } else {
          setTimeout(poll, 1000)
        }
      }
      poll()
    } catch (err) {
      showToast('Lỗi tạo nội dung: ' + (err.response?.data?.error || err.message), 'error')
      setGenerating(false)
    }
  }

  const handleLoadComments = async (postId) => {
    if (!selectedPage) return
    setCommentsPostId(postId)
    setLoadingComments(true)
    try {
      const res = await facebookAPI.getPostComments(postId, selectedPage.access_token)
      setComments(res.data?.data || [])
    } catch (err) {
      showToast('Lỗi tải bình luận', 'error')
    } finally {
      setLoadingComments(false)
    }
  }

  const displayPosts = searchResults !== null ? searchResults : posts

  // --- Render ---
  return (
    <div className="space-y-6 mx-auto p-4 max-w-5xl">
      <h1 className="font-bold text-3xl">Facebook Page Manager</h1>

      {/* Step 1: Connect */}
      <div className="bg-base-100 shadow card">
        <div className="card-body">
          <h2 className="card-title">1. Kết nối Facebook</h2>
          <p className="text-sm text-base-content/60">
            Nhập Access Token từ{' '}
            <a href="/facebook-token" target="_blank" className="link link-primary">
              trang lấy token
            </a>{' '}
            hoặc từ Facebook Developer.
          </p>
          <div className="flex gap-2 mt-2">
            <input
              type="text"
              placeholder="Paste Facebook Access Token..."
              className="flex-1 input input-bordered"
              value={fbToken}
              onChange={(e) => setFbToken(e.target.value)}
            />
            <button className="btn btn-primary" onClick={handleConnect}>
              Kết nối
            </button>
          </div>
          {userInfo && (
            <div className="flex items-center gap-3 mt-3 p-3 rounded-lg bg-base-200">
              {userInfo.picture?.data?.url && (
                <img src={userInfo.picture.data.url} alt="" className="rounded-full w-10 h-10" />
              )}
              <div>
                <p className="font-semibold">{userInfo.name}</p>
                <p className="text-xs text-base-content/50">{userInfo.id}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Step 2: Select Page */}
      {pages.length > 0 && (
        <div className="bg-base-100 shadow card">
          <div className="card-body">
            <h2 className="card-title">2. Chọn Page</h2>
            <div className="flex flex-wrap gap-2">
              {pages.map((p) => (
                <button
                  key={p.id}
                  onClick={() => handleSelectPage(p)}
                  className={`btn btn-sm ${selectedPage?.id === p.id ? 'btn-primary' : 'btn-outline'}`}
                >
                  {p.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Active page sections */}
      {selectedPage && (
        <>
          {/* Search */}
          <div className="bg-base-100 shadow card">
            <div className="card-body">
              <h2 className="card-title">
                <MagnifyingGlassIcon className="inline w-5 h-5" /> Tìm kiếm bài viết
              </h2>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Từ khoá..."
                  className="flex-1 input input-bordered input-sm"
                  value={searchKeyword}
                  onChange={(e) => setSearchKeyword(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                />
                <button className="btn btn-sm btn-primary" onClick={handleSearch}>
                  <MagnifyingGlassIcon className="w-4 h-4" /> Tìm
                </button>
                {searchResults !== null && (
                  <button
                    className="btn btn-sm btn-ghost"
                    onClick={() => setSearchResults(null)}
                  >
                    Xoá bộ lọc
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Create Post + GPT */}
          <div className="gap-4 grid grid-cols-1 lg:grid-cols-2">
            {/* Create post */}
            <div className="bg-base-100 shadow card">
              <div className="card-body">
                <h2 className="card-title">
                  <PaperAirplaneIcon className="inline w-5 h-5" /> Đăng bài mới
                </h2>
                <textarea
                  className="w-full textarea textarea-bordered"
                  rows={4}
                  placeholder="Nội dung bài đăng..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                />
                <input
                  type="text"
                  placeholder="Link (tuỳ chọn)"
                  className="input input-bordered input-sm"
                  value={newLink}
                  onChange={(e) => setNewLink(e.target.value)}
                />
                <input
                  type="text"
                  placeholder="URL hình ảnh (tuỳ chọn)"
                  className="input input-bordered input-sm"
                  value={newImageUrl}
                  onChange={(e) => setNewImageUrl(e.target.value)}
                />
                <button
                  className={`btn btn-primary btn-sm mt-2 ${publishing ? 'loading' : ''}`}
                  onClick={handlePublish}
                  disabled={publishing}
                >
                  {!publishing && <PaperAirplaneIcon className="w-4 h-4" />}
                  {publishing ? 'Đang đăng...' : 'Đăng bài'}
                </button>
              </div>
            </div>

            {/* GPT content gen */}
            <div className="bg-base-100 shadow card">
              <div className="card-body">
                <h2 className="card-title">
                  <SparklesIcon className="inline w-5 h-5" /> Tạo nội dung bằng AI
                </h2>
                <input
                  type="text"
                  placeholder="Chủ đề bài đăng..."
                  className="input input-bordered input-sm"
                  value={gptTopic}
                  onChange={(e) => setGptTopic(e.target.value)}
                />
                <input
                  type="text"
                  placeholder="Yêu cầu thêm (tuỳ chọn)..."
                  className="input input-bordered input-sm"
                  value={gptRequirements}
                  onChange={(e) => setGptRequirements(e.target.value)}
                />
                <select
                  className="select select-bordered select-sm"
                  value={gptTone}
                  onChange={(e) => setGptTone(e.target.value)}
                >
                  <option value="professional">Chuyên nghiệp</option>
                  <option value="casual">Thân thiện</option>
                  <option value="creative">Sáng tạo</option>
                  <option value="humorous">Hài hước</option>
                </select>
                <button
                  className={`btn btn-secondary btn-sm mt-2 ${generating ? 'loading' : ''}`}
                  onClick={handleGenerate}
                  disabled={generating}
                >
                  {!generating && <SparklesIcon className="w-4 h-4" />}
                  {generating ? 'Đang tạo...' : 'Tạo nội dung'}
                </button>
              </div>
            </div>
          </div>

          {/* Posts list */}
          <div className="bg-base-100 shadow card">
            <div className="card-body">
              <div className="flex justify-between items-center">
                <h2 className="card-title">
                  <DocumentTextIcon className="inline w-5 h-5" /> Bài viết
                  {searchResults !== null && (
                    <span className="badge badge-info badge-sm ml-2">
                      Kết quả tìm kiếm: {searchResults.length}
                    </span>
                  )}
                </h2>
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => loadPosts(selectedPage.id, selectedPage.access_token)}
                >
                  <ArrowPathIcon className="w-4 h-4" />
                </button>
              </div>

              {loadingPosts ? (
                <div className="flex justify-center py-8">
                  <span className="loading loading-spinner loading-lg" />
                </div>
              ) : displayPosts.length === 0 ? (
                <p className="py-4 text-center text-base-content/50">Không có bài viết nào.</p>
              ) : (
                <div className="space-y-4 mt-2">
                  {displayPosts.map((post) => (
                    <div key={post.id} className="p-4 border rounded-lg border-base-300">
                      <p className="whitespace-pre-wrap">{post.message || '(Không có nội dung văn bản)'}</p>
                      {post.full_picture && (
                        <img
                          src={post.full_picture}
                          alt=""
                          className="mt-2 rounded max-h-60 object-cover"
                        />
                      )}
                      <div className="flex flex-wrap items-center gap-4 mt-3 text-sm text-base-content/60">
                        <span className="flex items-center gap-1">
                          <HandThumbUpIcon className="w-4 h-4" />
                          {post.likes?.summary?.total_count ?? 0}
                        </span>
                        <button
                          className="flex items-center gap-1 hover:text-primary cursor-pointer"
                          onClick={() => handleLoadComments(post.id)}
                        >
                          <ChatBubbleLeftEllipsisIcon className="w-4 h-4" />
                          {post.comments?.summary?.total_count ?? 0}
                        </button>
                        <span className="flex items-center gap-1">
                          <ShareIcon className="w-4 h-4" />
                          {post.shares?.count ?? 0}
                        </span>
                        <span className="text-xs">
                          {post.created_time && new Date(post.created_time).toLocaleString('vi-VN')}
                        </span>
                        {post.permalink_url && (
                          <a
                            href={post.permalink_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="link link-primary text-xs"
                          >
                            Xem trên Facebook
                          </a>
                        )}
                      </div>

                      {/* Inline comments */}
                      {commentsPostId === post.id && (
                        <div className="mt-3 pt-3 border-t border-base-300">
                          {loadingComments ? (
                            <span className="loading loading-spinner loading-sm" />
                          ) : comments.length === 0 ? (
                            <p className="text-sm text-base-content/50">Chưa có bình luận.</p>
                          ) : (
                            <div className="space-y-2">
                              {comments.map((c) => (
                                <div key={c.id} className="p-2 rounded bg-base-200 text-sm">
                                  <span className="font-semibold">{c.from?.name ?? 'Ẩn danh'}: </span>
                                  {c.message}
                                  <span className="ml-2 text-xs text-base-content/40">
                                    {c.like_count > 0 && `👍 ${c.like_count}`}
                                  </span>
                                </div>
                              ))}
                            </div>
                          )}
                          <button
                            className="btn btn-ghost btn-xs mt-2"
                            onClick={() => setCommentsPostId(null)}
                          >
                            Ẩn bình luận
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
