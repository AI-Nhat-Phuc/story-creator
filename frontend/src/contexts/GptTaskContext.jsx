import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react'
import { gptAPI } from '../services/api'

const STORAGE_KEY = 'gpt_pending_tasks'
const POLL_INTERVAL = 2000

const GptTaskContext = createContext(null)

/**
 * Manages GPT background tasks with persistence across page refreshes.
 *
 * Features:
 * - Saves pending task IDs to localStorage
 * - Resumes polling on page load for any unfinished tasks
 * - Shows toast notification when a task completes or fails
 * - Provides `registerTask` for containers to submit new tasks
 * - Provides `onTaskComplete` callback registration per task
 */
export function GptTaskProvider({ children, showToast }) {
  // { taskId: { label, task_type, status, result?, callback? } }
  const [tasks, setTasks] = useState({})
  const callbacksRef = useRef({})
  const pollTimerRef = useRef(null)
  const mountedRef = useRef(true)
  const tasksRef = useRef(tasks)
  const pollRef = useRef(null)

  // Keep tasksRef in sync
  useEffect(() => { tasksRef.current = tasks }, [tasks])

  // ---- localStorage helpers ----
  const loadStoredTasks = useCallback(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      return raw ? JSON.parse(raw) : {}
    } catch {
      return {}
    }
  }, [])

  const saveStoredTasks = useCallback((taskMap) => {
    try {
      // Only store non-completed tasks
      const pending = {}
      for (const [id, t] of Object.entries(taskMap)) {
        if (t.status !== 'completed' && t.status !== 'error') {
          pending[id] = { label: t.label, task_type: t.task_type, status: t.status }
        }
      }
      if (Object.keys(pending).length > 0) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(pending))
      } else {
        localStorage.removeItem(STORAGE_KEY)
      }
    } catch { /* ignore */ }
  }, [])

  // ---- Register a new task for tracking ----
  const registerTask = useCallback((taskId, { label, task_type, onComplete }) => {
    if (onComplete) {
      callbacksRef.current[taskId] = onComplete
    }
    setTasks(prev => {
      const next = {
        ...prev,
        [taskId]: { label, task_type, status: 'pending' }
      }
      saveStoredTasks(next)
      return next
    })
  }, [saveStoredTasks])

  // ---- Handle a completed/errored task ----
  const handleTaskDone = useCallback((taskId, taskData) => {
    const status = taskData.status
    // Read label from ref to avoid stale closure
    const label = taskData.label || tasksRef.current[taskId]?.label || 'GPT Task'

    if (status === 'completed') {
      showToast?.(`✅ ${label} — hoàn tất!`, 'success')
    } else if (status === 'error') {
      const errMsg = typeof taskData.result === 'string' ? taskData.result : 'Có lỗi xảy ra'
      showToast?.(`❌ ${label} — ${errMsg}`, 'error')
    }

    // Call callback if registered
    const cb = callbacksRef.current[taskId]
    if (cb) {
      cb(taskData)
      delete callbacksRef.current[taskId]
    }

    // Update state & clean from localStorage
    setTasks(prev => {
      const next = { ...prev, [taskId]: { ...prev[taskId], ...taskData } }
      saveStoredTasks(next)
      return next
    })
  }, [showToast, saveStoredTasks])

  // ---- Polling loop ----
  const pollPendingTasks = useCallback(async () => {
    if (!mountedRef.current) return

    // Collect all IDs that need polling — use ref for fresh state
    const pending = {}
    // From state (via ref to avoid stale closure)
    for (const [id, t] of Object.entries(tasksRef.current)) {
      if (t.status === 'pending' || t.status === 'processing') {
        pending[id] = t
      }
    }
    // From localStorage (for tasks registered before refresh)
    const stored = loadStoredTasks()
    for (const [id, t] of Object.entries(stored)) {
      if (!pending[id]) {
        pending[id] = t
      }
    }

    const ids = Object.keys(pending)
    if (ids.length === 0) return

    try {
      const response = await gptAPI.getTasks(ids)
      const serverTasks = response.data?.tasks || []

      for (const serverTask of serverTasks) {
        const tid = serverTask.task_id
        if (!tid) continue

        if (serverTask.status === 'completed' || serverTask.status === 'error') {
          handleTaskDone(tid, serverTask)
        } else if (serverTask.status === 'processing') {
          // Update progress in state
          setTasks(prev => ({
            ...prev,
            [tid]: { ...prev[tid], ...serverTask, status: 'processing' }
          }))
        }
      }

      // Check for tasks not found on server (orphaned)
      const serverTaskIds = new Set(serverTasks.map(t => t.task_id))
      for (const id of ids) {
        if (!serverTaskIds.has(id)) {
          // Task no longer on server — clean up
          handleTaskDone(id, {
            status: 'error',
            label: pending[id]?.label,
            result: 'Task đã hết hạn hoặc server đã khởi động lại'
          })
        }
      }
    } catch (err) {
      console.error('[GptTaskContext] Poll error:', err)
    }
  }, [loadStoredTasks, handleTaskDone])

  // Keep pollRef in sync so interval always calls the latest version
  useEffect(() => { pollRef.current = pollPendingTasks }, [pollPendingTasks])

  // ---- Start/stop polling based on pending tasks ----
  useEffect(() => {
    const hasPending = Object.values(tasks).some(
      t => t.status === 'pending' || t.status === 'processing'
    )
    const storedHasPending = Object.keys(loadStoredTasks()).length > 0

    if (hasPending || storedHasPending) {
      // Always restart interval to pick up the latest pollRef
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current)
      }
      pollTimerRef.current = setInterval(() => {
        pollRef.current?.()
      }, POLL_INTERVAL)
      // Also poll immediately
      pollRef.current?.()
    } else {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current)
        pollTimerRef.current = null
      }
    }

    return () => {
      // Don't clear on re-render, only on unmount
    }
  }, [tasks, loadStoredTasks])

  // ---- On mount: recover tasks from localStorage ----
  useEffect(() => {
    mountedRef.current = true
    const stored = loadStoredTasks()
    if (Object.keys(stored).length > 0) {
      setTasks(prev => ({ ...stored, ...prev }))
    }
    return () => {
      mountedRef.current = false
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current)
        pollTimerRef.current = null
      }
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // ---- Get active (non-finished) tasks ----
  const activeTasks = Object.entries(tasks)
    .filter(([, t]) => t.status === 'pending' || t.status === 'processing')
    .map(([id, t]) => ({ taskId: id, ...t }))

  return (
    <GptTaskContext.Provider value={{ registerTask, activeTasks, tasks }}>
      {children}
    </GptTaskContext.Provider>
  )
}

export function useGptTasks() {
  const ctx = useContext(GptTaskContext)
  if (!ctx) throw new Error('useGptTasks must be used within GptTaskProvider')
  return ctx
}

export default GptTaskContext
