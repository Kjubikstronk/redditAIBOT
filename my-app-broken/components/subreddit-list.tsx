import { Badge } from "@/components/ui/badge"
import { ExternalLink } from "lucide-react"

interface SubredditListProps {
  data: Record<string, number>
}

export function SubredditList({ data }: SubredditListProps) {
  const sortedSubreddits = Object.entries(data)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10) // Show top 10

  if (sortedSubreddits.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-muted-foreground">
        <p>No subreddit data available</p>
      </div>
    )
  }

  return (
    <div className="space-y-2 max-h-96 overflow-y-auto">
      {sortedSubreddits.map(([subreddit, count], index) => (
        <div
          key={subreddit}
          className="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-700/50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="text-sm font-medium text-muted-foreground">#{index + 1}</div>
            <a
              href={`https://www.reddit.com/r/${subreddit}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 transition-colors"
            >
              r/{subreddit}
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
          <Badge variant="secondary" className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
            {count}
          </Badge>
        </div>
      ))}
    </div>
  )
}
