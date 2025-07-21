"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { RefreshCw, Activity, TrendingUp, Users, Bot } from "lucide-react"
import { StatsCards } from "@/components/stats-cards"
import { VerdictChart } from "@/components/verdict-chart"
import { ActivityFeed } from "@/components/activity-feed"
import { SubredditList } from "@/components/subreddit-list"
import { TrendChart } from "@/components/trend-chart"

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

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null) // Reset error state on new fetch
      // Point to the running Flask API
      const response = await fetch("yhttp://127.0.0.1:5001/api/stats")
      if (!response.ok) {
        throw new Error(`Could not connect to backend. Is it running? (Status: ${response.status})`)
      }
      const newData = await response.json()
      setData(newData)
      setLastUpdated(new Date())
    } catch (error: any) {
      console.error("Could not fetch data:", error)
      setError(error.message || "An unknown error occurred.")
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
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="text-center">
              <Bot className="h-12 w-12 animate-pulse mx-auto mb-4 text-blue-500" />
              <p className="text-lg text-muted-foreground">Loading dashboard...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
        <div className="min-h-screen bg-red-50 dark:bg-red-900/20">
            <div className="container mx-auto px-4 py-8">
                <div className="flex items-center justify-center min-h-[60vh]">
                    <div className="text-center p-8 bg-white dark:bg-slate-800 rounded-lg shadow-xl max-w-lg">
                        <h2 className="text-2xl font-bold text-red-600 dark:text-red-400 mb-4">Connection Error</h2>
                        <p className="text-slate-600 dark:text-slate-300 mb-2">The dashboard could not load data from the backend.</p>
                        <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">Please make sure the Python backend server (`dashboard.py`) is running in a separate terminal.</p>
                        <code className="block bg-slate-100 dark:bg-slate-700 text-red-500 p-4 rounded-md text-left text-xs">
                            {error}
                        </code>
                        <Button onClick={fetchData} disabled={loading} variant="outline" size="sm" className="gap-2 mt-6">
                            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                            Retry Connection
                        </Button>
                    </div>
                </div>
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
