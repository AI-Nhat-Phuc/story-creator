'use client'

import React, { useState } from 'react'
import { Link, useNavigate } from '../../utils/router-compat'
import { useTranslation } from 'react-i18next'
import {
  BookOpenIcon,
  GlobeAltIcon,
  ClockIcon,
  DocumentTextIcon,
  UserIcon,
} from '@heroicons/react/24/outline'
import { marked } from 'marked'

function toPlainText(content) {
  if (!content) return ''
  try {
    const html = marked.parse(content)
    return html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
  } catch {
    return content.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim()
  }
}

// 10 distinct colour slots — keyed by world name hash so every world
// consistently gets the same colour across cards.
const COLOR_PALETTES = [
  { border: 'border-l-amber-500',   dot: 'bg-amber-500',   worldText: 'text-amber-700'  },
  { border: 'border-l-sky-500',     dot: 'bg-sky-500',     worldText: 'text-sky-700'    },
  { border: 'border-l-emerald-500', dot: 'bg-emerald-500', worldText: 'text-emerald-700'},
  { border: 'border-l-violet-500',  dot: 'bg-violet-500',  worldText: 'text-violet-700' },
  { border: 'border-l-rose-500',    dot: 'bg-rose-500',    worldText: 'text-rose-700'   },
  { border: 'border-l-cyan-500',    dot: 'bg-cyan-500',    worldText: 'text-cyan-700'   },
  { border: 'border-l-orange-500',  dot: 'bg-orange-500',  worldText: 'text-orange-700' },
  { border: 'border-l-teal-500',    dot: 'bg-teal-500',    worldText: 'text-teal-700'   },
  { border: 'border-l-indigo-500',  dot: 'bg-indigo-500',  worldText: 'text-indigo-700' },
  { border: 'border-l-pink-500',    dot: 'bg-pink-500',    worldText: 'text-pink-700'   },
]

function paletteFor(worldName) {
  const hash = worldName.split('').reduce((acc, ch) => acc + ch.charCodeAt(0), 0)
  return COLOR_PALETTES[hash % COLOR_PALETTES.length]
}

function StoriesView({
  stories,
  worlds,
  user,
  authLoading,
  formatWorldTime,
  getWorldName,
}) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [selectedWorldId, setSelectedWorldId] = useState('')

  const effectiveWorldId = selectedWorldId || (worlds[0]?.world_id ?? '')

  const handleCreateStoryClick = () => {
    if (effectiveWorldId) navigate(`/stories/new?worldId=${effectiveWorldId}`)
  }

  return (
    <div>
      {/* ── Page header ─────────────────────────────────────────────── */}
      <div className="mb-6">
        <h1 className="font-bold text-3xl mb-4">
          <BookOpenIcon className="inline w-8 h-8" /> Câu chuyện
        </h1>

        {/* World selector + CTA — only shown for authenticated users with worlds */}
        {!authLoading && user && worlds.length > 0 && (
          <div className="flex flex-col sm:flex-row gap-3">
            <select
              className="select select-bordered flex-1 max-w-xs"
              value={effectiveWorldId}
              onChange={e => setSelectedWorldId(e.target.value)}
            >
              {worlds.map(world => (
                <option key={world.world_id} value={world.world_id}>
                  {world.name}
                </option>
              ))}
            </select>
            <button
              onClick={handleCreateStoryClick}
              disabled={!effectiveWorldId}
              className="btn btn-primary"
            >
              + Tạo câu chuyện mới
            </button>
          </div>
        )}
      </div>

      {/* ── Story grid ──────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {stories.map(story => {
          const worldName = getWorldName(story.world_id)
          const colors = paletteFor(worldName)

          return (
            <Link
              key={story.story_id}
              to={`/stories/${story.story_id}`}
              className="group block"
            >
              <div
                className={[
                  // Card shell
                  'flex flex-col h-full',
                  'bg-base-100 rounded-xl',
                  'shadow-md group-hover:shadow-xl',
                  'border border-base-200',
                  // Thick left accent border — colour-coded by world
                  'border-l-4', colors.border,
                  'transition-all duration-200',
                  'overflow-hidden',
                ].join(' ')}
              >
                {/* ── Card body ───────────────────────────────────── */}
                <div className="flex flex-col flex-1 p-4 gap-2">

                  {/* World name + time */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={`inline-flex items-center gap-1.5 text-xs font-semibold ${colors.worldText}`}
                      title={worldName}
                    >
                      {/* Coloured dot matching the left border */}
                      <span className={`w-2 h-2 rounded-full shrink-0 ${colors.dot}`} />
                      <GlobeAltIcon className="w-3.5 h-3.5 shrink-0" />
                      <span className="truncate max-w-[180px]">{worldName}</span>
                    </span>
                    <span className="text-base-content/40 text-xs flex items-center gap-0.5 ml-auto shrink-0">
                      <ClockIcon className="w-3.5 h-3.5" />
                      {formatWorldTime(story)}
                    </span>
                  </div>

                  {/* Title */}
                  <h2 className="font-bold text-base-content text-lg leading-snug line-clamp-2">
                    {story.title}
                  </h2>

                  {/* Content preview */}
                  <div className="flex-1">
                    {story.content ? (
                      <p className="text-base-content/70 text-sm leading-relaxed line-clamp-4">
                        {toPlainText(story.content)}
                      </p>
                    ) : (
                      <p className="text-base-content/30 text-sm italic">Chưa có nội dung…</p>
                    )}
                  </div>
                </div>

                {/* ── Card footer ─────────────────────────────────── */}
                <div className="px-4 py-2.5 border-t border-base-200 flex items-center gap-1.5 text-base-content/40 text-xs">
                  {story.author_signature?.display ? (
                    <>
                      <UserIcon className="w-3.5 h-3.5 shrink-0" />
                      <span className="truncate">{story.author_signature.display}</span>
                    </>
                  ) : (
                    <>
                      <DocumentTextIcon className="w-3.5 h-3.5 shrink-0" />
                      <span>Click để đọc thêm</span>
                    </>
                  )}
                  {story.visibility && (
                    <span className={`ml-auto badge badge-xs ${story.visibility === 'public' ? 'badge-success' : story.visibility === 'draft' ? 'badge-warning' : 'badge-ghost'}`}>
                      {t(`common.${story.visibility}`, story.visibility)}
                    </span>
                  )}
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      {/* ── Empty states ────────────────────────────────────────────── */}
      {stories.length === 0 && worlds.length > 0 && (
        <div className="py-16 text-center">
          <p className="opacity-60 text-xl">Chưa có câu chuyện nào. Hãy tạo câu chuyện đầu tiên!</p>
        </div>
      )}

      {worlds.length === 0 && (
        <div className="py-16 text-center">
          <div className="mx-auto max-w-md">
            <svg xmlns="http://www.w3.org/2000/svg" className="opacity-20 mx-auto w-24 h-24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="opacity-60 mt-4 text-xl">Chưa có thế giới nào!</p>
            <p className="opacity-50 mt-2 text-sm">Bạn cần tạo thế giới trước khi tạo câu chuyện.</p>
            <Link to="/worlds" className="mt-6 btn btn-primary">
              <GlobeAltIcon className="inline w-4 h-4" /> Tạo thế giới mới
            </Link>
          </div>
        </div>
      )}

    </div>
  )
}

export default StoriesView
