import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AnalyzedEntitiesEditor from '../AnalyzedEntitiesEditor'
import { STORY_TEMPLATES } from '../storyTemplates'
import {
  BookOpenIcon,
  GlobeAltIcon,
  ClockIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline'

function StoriesView({
  stories,
  worlds,
  user,
  authLoading,
  showCreateModal,
  formData,
  detectedCharacters,
  analyzedEntities,
  gptGenerating,
  gptAnalyzing,
  onOpenModal,
  onCloseModal,
  onInputChange,
  onSubmit,
  onGenerateDescription,
  onAnalyzeStory,
  onClearAnalyzedEntities,
  onUpdateAnalyzedEntities,
  showAnalyzedModal,
  onCloseAnalyzedModal,
  onOpenAnalyzedModal,
  formatWorldTime,
  getWorldName,
  availableCharacters = [],
  selectedCharacters = [],
  setSelectedCharacters = () => {},
}) {
    const navigate = useNavigate()

    const handleCreateStoryClick = () => {
      if (worlds.length === 1) {
        navigate(`/stories/new?worldId=${worlds[0].world_id}`)
      } else {
        onOpenModal()
      }
    }

    // Checkbox state for character selection
    const [createNewCharacter, setCreateNewCharacter] = useState(false);

    // Handle checkbox change
    const handleCharacterCheckbox = (e) => {
      const { value, checked } = e.target;
      if (value === '__new__') {
        setCreateNewCharacter(checked);
        if (checked) {
          setSelectedCharacters((prev) => prev.filter((id) => id !== '__new__').concat(['__new__']));
        } else {
          setSelectedCharacters((prev) => prev.filter((id) => id !== '__new__'));
        }
        return;
      }
      if (checked) {
        setSelectedCharacters((prev) => prev.concat([value]));
      } else {
        setSelectedCharacters((prev) => prev.filter((id) => id !== value));
      }
    };
  // Popup state for template selection
  const [selectedTemplate, setSelectedTemplate] = useState('')
  const [selectedGenre, setSelectedGenre] = useState('adventure')

  // Open template modal
  // const handleOpenTemplateModal = () => {
  //   setSelectedGenre(formData.genre || 'adventure')
  //   setShowTemplateModal(true)
  // }

  // Handle template select and trigger GPT
  const handleSelectTemplate = (template) => {
    setSelectedTemplate(template)
    // Pass template to GPT handler
    onGenerateDescription(template)
  }

  // Change genre in modal
  const handleChangeGenre = (e) => {
    setSelectedGenre(e.target.value)
  }

  // Get templates for selected genre
  const genreTemplates = STORY_TEMPLATES.find(t => t.genre === selectedGenre)
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="font-bold text-3xl"><BookOpenIcon className="inline w-8 h-8" /> Câu chuyện</h1>
        {worlds.length > 0 ? (
          authLoading ? (
            <button className="btn btn-primary" disabled>
              <span className="loading loading-spinner loading-xs"></span>
            </button>
          ) : user ? (
            <button onClick={handleCreateStoryClick} className="btn btn-primary">
              + Tạo câu chuyện mới
            </button>
          ) : (
            <div className="tooltip-left tooltip" data-tip="Vui lòng đăng nhập để tạo câu chuyện">
              <button className="btn btn-disabled" disabled>
                + Tạo câu chuyện mới
              </button>
            </div>
          )
        ) : (
          <div className="tooltip-left tooltip" data-tip="Tạo thế giới trước để bắt đầu">
            <button className="btn btn-disabled" disabled>
              + Tạo câu chuyện mới
            </button>
          </div>
        )}
      </div>

      <div className="gap-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {stories.map(story => {
          // Get world name for scroll color
          const worldName = getWorldName(story.world_id)

          // Generate color based on world name hash
          const colorPalettes = [
            { rod: 'from-amber-600 via-amber-500 to-amber-600', rodEdge: 'from-amber-700 to-amber-800', text: 'text-amber-100' },
            { rod: 'from-cyan-600 via-cyan-500 to-cyan-600', rodEdge: 'from-cyan-700 to-cyan-800', text: 'text-cyan-100' },
            { rod: 'from-emerald-600 via-emerald-500 to-emerald-600', rodEdge: 'from-emerald-700 to-emerald-800', text: 'text-emerald-100' },
            { rod: 'from-violet-600 via-violet-500 to-violet-600', rodEdge: 'from-violet-700 to-violet-800', text: 'text-violet-100' },
            { rod: 'from-rose-600 via-rose-500 to-rose-600', rodEdge: 'from-rose-700 to-rose-800', text: 'text-rose-100' },
            { rod: 'from-sky-600 via-sky-500 to-sky-600', rodEdge: 'from-sky-700 to-sky-800', text: 'text-sky-100' },
            { rod: 'from-orange-600 via-orange-500 to-orange-600', rodEdge: 'from-orange-700 to-orange-800', text: 'text-orange-100' },
            { rod: 'from-teal-600 via-teal-500 to-teal-600', rodEdge: 'from-teal-700 to-teal-800', text: 'text-teal-100' },
            { rod: 'from-indigo-600 via-indigo-500 to-indigo-600', rodEdge: 'from-indigo-700 to-indigo-800', text: 'text-indigo-100' },
            { rod: 'from-pink-600 via-pink-500 to-pink-600', rodEdge: 'from-pink-700 to-pink-800', text: 'text-pink-100' },
          ]

          // Simple hash from world name
          const hash = worldName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
          const colors = colorPalettes[hash % colorPalettes.length]

          return (
            <Link key={story.story_id} to={`/stories/${story.story_id}`} className="group block">
              {/* Scroll Container */}
              <div className="flex h-[220px]">
                {/* Left Scroll Rod */}
                <div className={`relative bg-gradient-to-r ${colors.rod} shadow-md rounded-l-sm w-7`}>
                  {/* World name vertical text */}
                  <div className="absolute inset-0 flex justify-center items-center">
                    <span
                      className={`font-bold text-[16px] ${colors.text} whitespace-nowrap origin-center drop-shadow-sm`}
                      style={{ writingMode: 'vertical-rl', textOrientation: 'mixed', transform: 'rotate(180deg)' }}
                    >
                      {worldName}
                    </span>
                  </div>
                </div>

                {/* Scroll Paper */}
                <div className="relative flex-1 bg-white shadow-xl group-hover:shadow-2xl border border-gray-200 border-l-0 rounded-r-sm overflow-hidden transition-all">
                  <div className="z-10 relative flex flex-col p-4 h-full">
                    <h2 className="mb-2 font-bold text-gray-900 text-lg line-clamp-2 leading-tight">
                      {story.title}
                    </h2>
                    <div className="flex flex-wrap gap-1 mb-2">
                      <span className="bg-gray-100 px-2 py-0.5 rounded text-gray-700 text-xs">
                                                <ClockIcon className="inline w-3.5 h-3.5" /> {formatWorldTime(story)}
                      </span>
                    </div>
                    <div className="flex-1 overflow-hidden">
                      {story.content ? (
                        <p className="text-gray-800 text-sm line-clamp-4 leading-relaxed">
                          {story.content}
                        </p>
                      ) : (
                        <p className="text-gray-400 text-sm italic">
                          Chưa có mô tả...
                        </p>
                      )}
                    </div>
                    <div className="mt-2 pt-2 border-gray-300 border-t border-dashed">
                      <span className="text-gray-400 text-xs"><DocumentTextIcon className="inline w-3.5 h-3.5" /> Click để đọc thêm</span>
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      {stories.length === 0 && worlds.length > 0 && (
        <div className="py-12 text-center">
          <p className="opacity-60 text-xl">Chưa có câu chuyện nào. Hãy tạo câu chuyện đầu tiên!</p>
        </div>
      )}

      {worlds.length === 0 && (
        <div className="py-12 text-center">
          <div className="mx-auto max-w-md">
            <svg xmlns="http://www.w3.org/2000/svg" className="opacity-30 mx-auto w-24 h-24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="opacity-60 mt-4 text-xl">Chưa có thế giới nào!</p>
            <p className="opacity-50 mt-2">Bạn cần tạo thế giới trước khi tạo câu chuyện.</p>
            <Link to="/worlds" className="mt-4 btn btn-primary">
                            <GlobeAltIcon className="inline w-4 h-4" /> Tạo thế giới mới
            </Link>
          </div>
        </div>
      )}

      {showCreateModal && (
        <div className="modal modal-open">
          <div className="modal-box max-w-sm">
            <h3 className="mb-4 font-bold text-lg">Chọn thế giới</h3>
            <p className="mb-4 text-sm text-base-content/70">Câu chuyện sẽ được tạo trong thế giới nào?</p>
            <div className="flex flex-col gap-2">
              {worlds.map(world => (
                <Link
                  key={world.world_id}
                  to={`/stories/new?worldId=${world.world_id}`}
                  className="btn btn-outline justify-start"
                  onClick={onCloseModal}
                >
                  <GlobeAltIcon className="w-4 h-4 shrink-0" />
                  <span className="truncate">{world.name}</span>
                  <span className="ml-auto text-xs opacity-50">{world.world_type}</span>
                </Link>
              ))}
            </div>
            <div className="modal-action mt-6">
              <button type="button" onClick={onCloseModal} className="btn btn-ghost">Hủy</button>
            </div>
          </div>
          <div className="modal-backdrop" onClick={onCloseModal}></div>
        </div>
      )}




      {/* GPT Analyzed Entities Modal */}
      <AnalyzedEntitiesEditor
        open={showAnalyzedModal}
        analyzedEntities={analyzedEntities}
        onUpdate={onUpdateAnalyzedEntities}
        onClose={onCloseAnalyzedModal}
        onClear={onClearAnalyzedEntities}
        linkLabel="Xác nhận"
      />
    </div>
  )
}

export default StoriesView
