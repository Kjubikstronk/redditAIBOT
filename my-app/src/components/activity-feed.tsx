import { Bot, User, MessageSquare } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { motion } from "framer-motion"
import { Notification } from "./notification"

interface ActivityFeedProps {
  data: {
    recent_triggers: Array<{
      id: string
      user: string
      content: string
      verdict: "Potentially AI-Generated" | "Likely Human"
      timestamp: string
    }>
  }
}

export function ActivityFeed({ data }: ActivityFeedProps) {
  const getVerdictClass = (verdict: string) => {
    switch (verdict) {
      case "Potentially AI-Generated":
        return "bg-red-500/10 text-red-500 border-red-500/20";
      case "Likely Human":
        return "bg-green-500/10 text-green-500 border-green-500/20";
      default:
        return "bg-gray-500/10 text-gray-500 border-gray-500/20";
    }
  };

  const recentTriggers = data?.recent_triggers;

  return (
    <div className="space-y-4">
        {Array.isArray(recentTriggers) && recentTriggers.length > 0 ? (
          recentTriggers.map((item, i) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <Notification>
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    {item.verdict === "Potentially AI-Generated" ? (
                      <Bot className="h-6 w-6 text-red-500" />
                    ) : (
                      <User className="h-6 w-6 text-green-500" />
                    )}
                  </div>
                  <div className="flex-grow">
                    <div className="flex items-center justify-between">
                      <p className="font-semibold text-sm text-gray-800 dark:text-gray-200">{item.user}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{new Date(item.timestamp).toLocaleTimeString()}</p>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-1 line-clamp-2">
                      <MessageSquare className="h-4 w-4 inline-block mr-2 text-gray-400" />
                      {item.content}
                    </p>
                    <div className="mt-2">
                      <Badge className={cn("text-xs font-semibold", getVerdictClass(item.verdict))}>
                        {item.verdict}
                      </Badge>
                    </div>
                  </div>
                </div>
              </Notification>
            </motion.div>
          ))
        ) : (
          <div className="flex items-center justify-center h-24 text-muted-foreground">
            <p>No recent activity found</p>
          </div>
        )}
    </div>
  )
}
