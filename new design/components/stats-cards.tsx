import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Bot, Target, TrendingUp, Activity } from "lucide-react"
import { AnimatedCounter } from "./animated-counter"

interface StatsCardsProps {
  data: {
    total_triggers: number
    verdict_distribution: Record<string, number>
    recent_triggers: Array<any>
  }
}

export function StatsCards({ data }: StatsCardsProps) {
  const totalVerdicts = Object.values(data.verdict_distribution).reduce((a, b) => a + b, 0)
  const recentActivity = data.recent_triggers.length

  const getVerdictPercentage = (verdict: string) => {
    const count = data.verdict_distribution[verdict] || 0
    return totalVerdicts > 0 ? Math.round((count / totalVerdicts) * 100) : 0
  }

  const stats = [
    {
      title: "Total Triggers",
      value: data.total_triggers.toLocaleString(),
      icon: Bot,
      color: "text-blue-500",
      bgColor: "bg-blue-50 dark:bg-blue-950",
      description: "All-time detections",
    },
    {
      title: "AI Detected",
      value: `${getVerdictPercentage("🔴 Potentially AI-Generated")}%`,
      icon: Target,
      color: "text-red-500",
      bgColor: "bg-red-50 dark:bg-red-950",
      description: "Potentially AI-generated",
    },
    {
      title: "Human Content",
      value: `${getVerdictPercentage("🟢 Likely Human")}%`,
      icon: TrendingUp,
      color: "text-green-500",
      bgColor: "bg-green-50 dark:bg-green-950",
      description: "Likely human-written",
    },
    {
      title: "Recent Activity",
      value: recentActivity.toString(),
      icon: Activity,
      color: "text-orange-500",
      bgColor: "bg-orange-50 dark:bg-orange-950",
      description: "Latest detections",
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {stats.map((stat, index) => (
        <Card
          key={index}
          className="bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300"
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{stat.title}</CardTitle>
            <div className={`p-2 rounded-lg ${stat.bgColor}`}>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stat.title === "Total Triggers" ? (
                <AnimatedCounter value={data.total_triggers} />
              ) : stat.title.includes("%") ? (
                <AnimatedCounter value={Number.parseInt(stat.value)} suffix="%" />
              ) : (
                <AnimatedCounter value={Number.parseInt(stat.value)} />
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1">{stat.description}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
