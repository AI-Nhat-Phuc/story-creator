'use client'

import React from 'react'
import { Link } from '../../utils/router-compat'
import { useTranslation } from 'react-i18next'
import { marked } from 'marked'

/**
 * Stream of chapter content blocks.
 *
 * Blocks arrive from /api/worlds/:id/novel/content sorted by (order ASC,
 * created_at ASC). A block may represent:
 *   - a full chapter (is_complete === true, start_line === 0)
 *   - the start of a chapter that's split across batches (is_complete === false)
 *   - a continuation (start_line > 0)
 * We only render a heading on the FIRST chunk of a chapter (start_line === 0).
 */
function NovelContentStream({ blocks }) {
  const { t } = useTranslation()

  return (
    <div className="space-y-8">
      {blocks.map((block, idx) => {
        const key = `${block.story_id}-${block.start_line}`
        const isFirstChunk = block.start_line === 0
        return (
          <section key={key} className="bg-base-100 rounded-box shadow p-6 sm:p-8">
            {isFirstChunk && (
              <header className="mb-4">
                <Link
                  to={`/stories/${block.story_id}/read`}
                  className="hover:underline"
                >
                  <h2 className="font-bold text-2xl sm:text-3xl">
                    {block.title}
                  </h2>
                </Link>
              </header>
            )}
            <div
              className="prose prose-lg max-w-none leading-relaxed"
              dangerouslySetInnerHTML={{ __html: marked.parse(block.content || '') }}
            />
            {!block.is_complete && (
              <p className="opacity-60 italic mt-4">
                {t('pages.novel.continued')}
              </p>
            )}
          </section>
        )
      })}
    </div>
  )
}

export default NovelContentStream
