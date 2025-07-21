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
    datasets: {
        "Potentially AI-Generated": number[],
        "Possibly AI-Generated": number[],
        "Likely Human": number[]
    }
  }
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [isLive, setIsLive] = useState(true)


  const fetchData = async () => {
    try {
      setLoading(true)
      const res = await fetch("http://127.0.0.1:5001/api/stats")
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`)
      }
      const jsonData = await res.json()
      
      // The backend sends snake_case, but the components expect camelCase.
      // We can handle this transformation here or update the components.
      // For now, let's assume the components will be updated or already handle it.
      setData(jsonData)
      setLastUpdated(new Date())
    } catch (error) {
      console.error("Could not fetch data:", error)
      setIsLive(false) // Switch to demo mode on error
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
        <div className="flex flex-col min-h-screen">
        <header className="flex items-center justify-between px-6 py-4 border-b">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold">Reddit AI Detection Bot</h1>
            <p className="text-muted-foreground">Real-time monitoring and analytics dashboard</p>
          </div>
          <div className="flex items-center gap-4">
            {lastUpdated && <span className="text-sm text-muted-foreground">Last updated: {lastUpdated.toLocaleTimeString()}</span>}
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </header>
        <main className="flex-1 p-6 bg-muted/40">
            <LoadingSkeleton/>
        </main>
      </div>
    )
  }

  return (
    <div className="flex flex-col min-h-screen">
       <header className="flex items-center justify-between px-6 py-4 border-b">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold">Reddit AI Detection Bot</h1>
            <p className="text-muted-foreground">Real-time monitoring and analytics dashboard</p>
          </div>
          <div className="flex items-center gap-4">
            {lastUpdated && <span className="text-sm text-muted-foreground">Last updated: {lastUpdated.toLocaleTimeString()}</span>}
            <Button variant="outline" size="sm" onClick={fetchData} disabled={loading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </header>

        <main className="flex-1 p-6 bg-muted/40">
        {!isLive && <DemoBanner />}
        
        {data && (
          <>
            <StatsCards data={data} />

            <div className="grid md:grid-cols-2 gap-6 mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Verdict Distribution</CardTitle>
                  <CardDescription>Distribution of AI detection results</CardDescription>
                </CardHeader>
                <CardContent>
                  <VerdictChart data={data.verdict_distribution} />
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Top Subreddits</CardTitle>
                  <CardDescription>Most active communities</CardDescription>
                </CardHeader>
                <CardContent>
                  <SubredditList data={data.subreddit_activity} />
                </CardContent>
              </Card>
            </div>
            
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Live Activity Feed</CardTitle>
                <CardDescription>Recent bot detections and activity</CardDescription>
              </CardHeader>
              <CardContent>
                <ActivityFeed data={data.recent_triggers} />
              </CardContent>
            </Card>
          </>
        )}
        </main>
    </div>
  )
} 