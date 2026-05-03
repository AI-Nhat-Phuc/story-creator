# Writing Modal Feature Plan

## 1. Objective

Build a floating writing modal (chat-like) that allows users to continue drafting text across pages with auto-save and formatting capabilities.

---

## 2. Core Features

### 2.1 Writing Editor

* Reuse editor core (TipTap / Slate)
* Strip heavy plugins (image upload, embeds, etc.)
* Ensure smooth typing performance in modal
* Preserve cursor position

### 2.2 Auto Save

* Debounce: 2 seconds after user stops typing
* Cancel in-flight request when typing resumes
* Prevent race conditions (latest content wins)
* Save status indicator: saving / saved / error
* Optional: version check (updatedAt)

### 2.3 Manual Actions

* Save button
* Publish button

  * Enabled only when draft is saved
  * On publish: remove draft from modal state

### 2.4 Draft Management

* Load drafts from API
* Priority: most recently updated draft
* Allow switching drafts

  * Must confirm if unsaved changes exist
  * Auto-save before switching
* Exclude published drafts

---

## 3. Desktop UX

### 3.1 Modal Behavior

* Only show if `has_active_draft = true`
* Trigger after navigation away from editor (with slight delay)

### 3.2 Modal Size

* Default: 30–40% screen width
* Minimum size must support writing comfortably
* Consider resizable (optional)

### 3.3 Modal Controls

* Minimize: collapse into floating button
* Maximize: navigate to full editor page

### 3.4 Persistent State

* Modal state persists across navigation
* Draft content retained in memory

---

## 4. Mobile UX

* Modal editor feature is disabled on mobile
* Existing full editor page remains fully functional
* Users can continue writing/editing via the standard editor page
* Ensure no modal-related state or UI is triggered on mobile

---

## 5. State Management

### 5.1 Isolation Principle

* DO NOT reuse editor page global state directly
* Create isolated modal state

### 5.2 Modal State

* draftId
* content
* saveStatus
* modalState (open / minimized)

### 5.3 Architecture Suggestion

* modalDraftStore (Zustand or similar)
* State scoped per draftId

---

## 6. API Strategy

### 6.1 Reuse with Wrapping

* Reuse existing APIs but wrap them:

  * saveDraft()
  * publishDraft()

### 6.2 Requirements

* Handle high-frequency auto-save
* Prevent outdated overwrite
* Support partial updates if possible

### 6.3 Cross-Platform Sync (Option A - Fetch Latest on Init)

* Server is the single source of truth
* Each save must update `updatedAt`

#### Desktop Behavior

* On modal initialization:

  * If `has_active_draft = true`
  * Fetch latest draft from server:

    * GET /draft/:id
  * Always override local/modal state with server data

* Do NOT rely on cached draft when opening modal

#### Mobile Behavior

* Auto-save updates draft continuously
* No additional sync logic required

#### Caching Strategy

* Allow short-lived in-memory cache during session
* MUST refetch when:

  * opening modal
  * switching drafts

#### Conflict Handling (Minimal)

* Last write wins based on `updatedAt`
* No real-time sync required

---

## 7. Reuse Strategy

Reuse Strategy

### 7.0 Reuse Audit First (Mandatory Step)

Before implementation:

* List all existing editor components & APIs

* Evaluate each using criteria:

  * Performance
  * Dependency weight
  * UX compatibility
  * API behavior
  * Maintainability

* Decide:

  * Reuse as-is
  * Reuse with modification
  * Do not reuse

* Produce decision table with:

  * Item
  * Decision
  * Risk
  * Reason
  * Action

⚠️ Do NOT implement before completing this.

### 7.1 Expected Decisions

* Editor Core → Reuse with modification (strip plugins)
* Toolbar → Do NOT reuse (build lite version)
* Save API → Reuse + wrap (debounce-safe)
* Publish API → Reuse
* Draft List API → Reuse (sort by updatedAt)
* Global State → Do NOT reuse (isolate)
* Hooks → Reuse with refactor
* Validation → Reuse

---

## 8. Shared Logic Extraction

Refactor editor logic into reusable modules:

* useEditorInstance
* useDraftData
* useAutoSave

Ensure modal only uses required subset

---

## 9. Performance Considerations

* Debounce auto-save (2s)
* Cancel previous requests
* Reduce plugin load
* Avoid unnecessary re-renders

---

## 10. Edge Cases

* Network failure during auto-save
* User closes tab before save
* Switching drafts mid-save
* Multiple sessions editing same draft

---

## 11. Missing but Critical (Add)

### 11.1 Offline Support

* Cache draft locally (localStorage / IndexedDB)
* Sync when connection restores

### 11.2 Publish Behavior

* After publish:

  * Clear modal state
  * Do not reopen same draft

---

## 12. Next Steps

1. Complete reuse audit table
2. Refactor editor core
3. Extract shared hooks
4. Implement modal state store
5. Wrap APIs for auto-save
6. Build lite toolbar
7. Implement modal UX
8. Add E2E tests
