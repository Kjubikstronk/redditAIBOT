"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { RefreshCw, Activity, TrendingUp, Users } from "lucide-react"
import { StatsCards } from "@/components/stats-cards"
import { VerdictChart } from "@/components/verdict-chart"
import { ActivityFeed } from "@/components/activity-feed"
import { SubredditList } from "@/components/subreddit-list"
import { TrendChart } from "@/components/trend-chart"
import { DemoBanner } from "@/components/demo-banner"
import { LoadingSkeleton } from "@/components/loading-skeleton"

interface DashboardData {
  total_triggers: number
  verdict_distribution: Record<string, number>
  recent_triggers: Array<{
    timestamp: string
    verdict: string
    subreddit: string
  }>
  subreddit_activity: Record<string, number>
  verdict_trends: {
    labels: string[]
    datasets: Record<string, number[]>
  }
}

// Add these helper functions before the main component:
const generateMockTriggers = () => {
  const verdicts = ["🔴 Potentially AI-Generated", "🟡 Possibly AI-Generated", "🟢 Likely Human"]
  const subreddits = [
    "technology",
    "AskReddit",
    "programming",
    "MachineLearning",
    "artificial",
    "ChatGPT",
    "OpenAI",
    "datascience",
    "Python",
    "javascript",
    "webdev",
    "startups",
  ]
  const triggers = []

  for (let i = 0; i < 20; i++) {
    const date = new Date()
    date.setMinutes(date.getMinutes() - Math.floor(Math.random() * 1440)) // Random time in last 24 hours

    triggers.push({
      timestamp: date.toLocaleString(),
      verdict: verdicts[Math.floor(Math.random() * verdicts.length)],
      subreddit: subreddits[Math.floor(Math.random() * subreddits.length)],
    })
  }

  return triggers.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
}

const generateMockSubredditActivity = () => {
  const subreddits = [
    "technology",
    "AskReddit",
    "programming",
    "MachineLearning",
    "artificial",
    "ChatGPT",
    "OpenAI",
    "datascience",
    "Python",
    "javascript",
  ]
  const activity: Record<string, number> = {}

  subreddits.forEach((subreddit) => {
    activity[subreddit] = Math.floor(Math.random() * 50) + 5
  })

  return activity
}

const generateMockTrends = () => {
  const labels = []
  const datasets: Record<string, number[]> = {
    "🔴 Potentially AI-Generated": [],
    "🟡 Possibly AI-Generated": [],
    "🟢 Likely Human": [],
  }

  // Generate last 7 days
  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    labels.push(date.toLocaleDateString())

    datasets["🔴 Potentially AI-Generated"].push(Math.floor(Math.random() * 30) + 10)
    datasets["🟡 Possibly AI-Generated"].push(Math.floor(Math.random() * 20) + 5)
    datasets["🟢 Likely Human"].push(Math.floor(Math.random() * 40) + 15)
  }

  return { labels, datasets }
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchData = async () => {
    try {
      setLoading(true)

      // Mock data generation
      await new Promise((resolve) => setTimeout(resolve, 500)) // Simulate API delay

      const mockData: DashboardData = {
        total_triggers: Math.floor(Math.random() * 10000) + 5000,
        verdict_distribution: {
          "🔴 Potentially AI-Generated": Math.floor(Math.random() * 200) + 50,
          "🟡 Possibly AI-Generated": Math.floor(Math.random() * 150) + 30,
          "🟢 Likely Human": Math.floor(Math.random() * 300) + 100,
        },
        recent_triggers: generateMockTriggers(),
        subreddit_activity: generateMockSubredditActivity(),
        verdict_trends: generateMockTrends(),
      }

      setData(mockData)
      setLastUpdated(new Date())
    } catch (error) {
      console.error("Could not fetch data:", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  if (loading && !data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Reddit AI Detection Bot
                </h1>
                <p className="text-lg text-muted-foreground mt-2">Real-time monitoring and analytics dashboard</p>
              </div>
            </div>
          </div>
          <LoadingSkeleton />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Reddit AI Detection Bot
              </h1>
              <p className="text-lg text-muted-foreground mt-2">Real-time monitoring and analytics dashboard</p>
            </div>
            <div className="flex items-center gap-4">
              {lastUpdated && (
                <div className="text-sm text-muted-foreground">Last updated: {lastUpdated.toLocaleTimeString()}</div>
              )}
              <Button onClick={fetchData} disabled={loading} variant="outline" size="sm" className="gap-2">
                <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                Refresh
              </Button>
            </div>
          </div>
        </div>

        {/* Demo Banner */}
        <DemoBanner />

        {data && (
          <>
            {/* Stats Cards */}
            <StatsCards data={data} />

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Verdict Distribution Chart */}
              <Card className="bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm border-0 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-blue-500" />
                    Verdict Distribution
                  </CardTitle>
                  <CardDescription>Distribution of AI detection results</CardDescription>
                </CardHeader>
                <CardContent>
                  <VerdictChart data={data.verdict_distribution} />
                </CardContent>
              </Card>

              {/* Top Subreddits */}
              <Card className="bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm border-0 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5 text-green-500" />
                    Top Subreddits
                  </CardTitle>
                  <CardDescription>Most active communities</CardDescription>
                </CardHeader>
                <CardContent>
                  <SubredditList data={data.subreddit_activity} />
                </CardContent>
              </Card>
            </div>

            {/* Activity Feed */}
            <Card className="bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm border-0 shadow-lg mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-orange-500" />
                  Live Activity Feed
                </CardTitle>
                <CardDescription>Recent bot detections and activity</CardDescription>
              </CardHeader>
              <CardContent>
                <ActivityFeed data={data.recent_triggers} />
              </CardContent>
            </Card>

            {/* Trend Chart */}
            <Card className="bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-purple-500" />
                  Daily Verdict Trends
                </CardTitle>
                <CardDescription>Historical trends of AI detection results</CardDescription>
              </CardHeader>
              <CardContent>
                <TrendChart data={data.verdict_trends} />
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  )
}
