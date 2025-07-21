import { Badge } from "@/components/ui/badge"
import { ExternalLink, Clock } from "lucide-react"

interface ActivityFeedProps {
  data: Array<{
    timestamp: string
    verdict: string
    subreddit: string
  }>
}

export function ActivityFeed({ data }: ActivityFeedProps) {
  const getVerdictColor = (verdict: string) => {
    if (verdict.includes("🔴")) return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
    if (verdict.includes("🟡")) return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
    if (verdict.includes("🟢")) return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
    return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-muted-foreground">
        <div className="text-center">
          <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p>No recent activity found</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-3 max-h-96 overflow-y-auto">
      {data
        .slice()
        .reverse()
        .map((trigger, index) => (
          <div
            key={index}
            className="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-700/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="text-sm text-muted-foreground font-mono">{trigger.timestamp}</div>
              <Badge className={getVerdictColor(trigger.verdict)}>{trigger.verdict}</Badge>
            </div>
            <a
              href={`https://www.reddit.com/r/${trigger.subreddit}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 transition-colors"
            >
              r/{trigger.subreddit}
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        ))}
    </div>
  )
}
