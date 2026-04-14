# SPEC — story preview truncation

> **Status**: DRAFT
> **Phase**: SPEC
> **Date**: 2026-04-14

---

## Behavior

The story detail page (`/stories/:storyId`) currently shows the entire story content inline. This is too long for a "preview" — the detail page should function as a summary/metadata card, while the novel reader UI (`/worlds/:worldId/novel`) is where the full story is read.

New behavior:

1. Show only the **first 10 lines** of `story.content` in the content block.
2. If the story has more than 10 lines, append a visual truncation indicator (fade/gradient overlay over the last visible lines) and a **"Xem thêm"** button below the content block.
3. Clicking **"Xem thêm"** navigates the user to `/worlds/{story.world_id}/novel`.
4. If the story has 10 lines or fewer, no truncation or button is shown — full content is rendered as before.

## API Contract

No backend changes. Purely frontend.

Existing props on `StoryDetailView` are sufficient:
- `story.content` (string)
- `story.world_id` (string, indirectly via `world` prop)
- `story.format` (`'html' | 'markdown' | 'plain'`)
- `highlightPosition` (number, -1 if none)

## Business Rules

1. **Line counting (plain text)**: split `story.content` by `\n`, trim trailing empty lines, count entries. Threshold = 10.
2. **Line counting (html/markdown)**: render into a container with CSS `line-clamp: 10` (≈ 10 visual lines). Detect overflow with `scrollHeight > clientHeight` after render.
3. **Highlight mode** (`highlightPosition >= 0`): skip truncation entirely — render full content so the target paragraph is visible. No "Xem thêm" button.
4. **Novel link target**: `/worlds/{world.world_id}/novel`. If `world` is null, do not truncate and do not show the button.
5. **Button placement**: below the content, inside the same card, DaisyUI `btn btn-primary` with an icon. Button label: `Xem thêm`.
6. **Fade overlay**: when truncated, apply a bottom gradient from transparent to `bg-base-100` over the last ~3 lines so the cut looks intentional.

## Edge Cases

- Empty content (`!story.content`): render nothing (existing behavior preserved).
- Content with trailing blank lines: trim trailing empties before counting.
- HTML/markdown content that's a single long paragraph wrapping many visual lines: CSS `line-clamp` handles it; button shown iff `scrollHeight > clientHeight`.
- `highlightPosition >= 0`: takes precedence — always full content, no button.
- Story without `world_id` (or `world` not loaded): full content, no button.

## Out of Scope

- Changing `NovelView` (no scroll-to-chapter / anchor behavior). Button navigates to novel index only.
- Configurable line count — hard-coded 10.
- Inline expand (the button navigates away, does not expand in place).
- i18n — hard-coded Vietnamese matching the rest of the page.
- Touching `StoryEditorPage`, `StoryPrintPage`, `StoriesPage`, or other pages.
