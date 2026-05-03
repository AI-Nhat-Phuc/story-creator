'use client'

const ACTION_LABELS = {
  create_story: { label: 'Created story', className: 'badge-success' },
  update_story: { label: 'Updated story', className: 'badge-info' },
  delete_story: { label: 'Deleted story', className: 'badge-error' },
}

function formatTs(isoString) {
  if (!isoString) return '—'
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(isoString))
  } catch {
    return isoString
  }
}

/**
 * Renders a paginated activity log table for a single user.
 *
 * Props:
 *   logs    – array of log entry objects
 *   loading – show skeleton when true
 */
function ActivityLogTable({ logs, loading }) {
  if (loading) {
    return (
      <div className="space-y-2 animate-pulse p-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-base-300 rounded h-8 w-full" />
        ))}
      </div>
    )
  }

  if (!logs || logs.length === 0) {
    return (
      <p className="py-6 text-center opacity-50 text-sm" data-testid="no-logs-msg">
        No activity recorded yet.
      </p>
    )
  }

  return (
    <div className="overflow-x-auto" data-testid="activity-log-table">
      <table className="table table-xs w-full">
        <thead>
          <tr>
            <th>Action</th>
            <th>Resource</th>
            <th>Details</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => {
            const actionInfo = ACTION_LABELS[log.action] ?? { label: log.action, className: 'badge-ghost' }
            return (
              <tr key={log.log_id} data-testid="log-row">
                <td>
                  <span className={`badge badge-sm ${actionInfo.className}`}>
                    {actionInfo.label}
                  </span>
                </td>
                <td className="font-mono text-xs opacity-70">{log.resource_type}</td>
                <td className="text-xs opacity-80">
                  {log.metadata?.title && (
                    <span className="font-medium">"{log.metadata.title}"</span>
                  )}
                  {log.resource_id && (
                    <span className="ml-1 opacity-50">({log.resource_id.slice(0, 8)}…)</span>
                  )}
                </td>
                <td className="text-xs whitespace-nowrap">{formatTs(log.timestamp)}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default ActivityLogTable
