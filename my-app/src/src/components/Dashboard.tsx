"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { SpotlightCard } from "./SpotlightCard"
import { ParticlesBackground } from "./ParticlesBackground"
import { RefreshCw, Activity, TrendingUp, Users, Bot, Zap, Clock } from "lucide-react"

interface DashboardData {
  total_triggers: number
  verdict_distribution: Record<string, number>
  recent_triggers: Array<{
    id: string
    content: string
    author: string
    subreddit: string
    timestamp: string
    verdict: string
    confidence: number
    permalink: string
    upvotes?: number
    downvotes?: number
  }>
  subreddit_activity: Record<string, number>
}

interface StatCardProps {
  title: string
  value: string
  icon: React.ComponentType<any>
  color: string
  bgColor: string
  description: string
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon: Icon, color, bgColor, description }) => {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <div
      className={`${bgColor} rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 backdrop-blur-sm bg-opacity-80 border border-white/20 relative overflow-hidden`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Animated background gradient */}
      <div
        className={`absolute inset-0 opacity-0 transition-opacity duration-300 ${
          isHovered ? "opacity-20" : ""
        } bg-gradient-to-br from-white to-transparent`}
      />

      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-gray-600">{title}</h3>
          <div
            className={`p-2 rounded-lg bg-white/50 ${isHovered ? "scale-110" : ""} transition-transform duration-300`}
          >
            <Icon className={`h-6 w-6 ${color}`} />
          </div>
        </div>
        <div className="text-3xl font-bold text-gray-800 mb-1">{value}</div>
        <p className="text-xs text-gray-600">{description}</p>
      </div>
    </div>
  )
}

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchData = async () => {
    try {
      setLoading(true)
      const response = await fetch("/api/stats")
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const newData = await response.json()
      setData(newData)
      setLastUpdated(new Date())
    } catch (error) {
      console.error("Could not fetch data:", error)
      // Generate mock data for demo
      generateMockData()
    } finally {
      setLoading(false)
    }
  }

  const generateMockData = () => {
    const mockComments = [
      {
        id: "1",
        content:
          "This is a fascinating discussion about artificial intelligence and its impact on society. I believe we need to carefully consider the ethical implications of AI development while embracing its potential benefits. The rapid advancement in machine learning has opened up new possibilities that were unimaginable just a few years ago.",
        author: "tech_enthusiast_42",
        subreddit: "artificial",
        timestamp: "2 hours ago",
        verdict: "🟢 Likely Human",
        confidence: 85,
        permalink: "/r/artificial/comments/example1",
        upvotes: 23,
        downvotes: 2,
      },
      {
        id: "2",
        content:
          "Machine learning algorithms have revolutionized data analysis. The implementation of neural networks in various domains has shown remarkable results in pattern recognition and predictive modeling. These advancements continue to push the boundaries of what's possible in artificial intelligence.",
        author: "ai_researcher",
        subreddit: "MachineLearning",
        timestamp: "4 hours ago",
        verdict: "🔴 Potentially AI-Generated",
        confidence: 92,
        permalink: "/r/MachineLearning/comments/example2",
        upvotes: 15,
        downvotes: 8,
      },
      {
        id: "3",
        content:
          "Has anyone tried the new ChatGPT update? The responses seem more natural now, but I'm still not sure about its reliability for complex tasks. I've been experimenting with it for various projects and the results are quite impressive.",
        author: "curious_user",
        subreddit: "ChatGPT",
        timestamp: "6 hours ago",
        verdict: "🟡 Possibly AI-Generated",
        confidence: 67,
        permalink: "/r/ChatGPT/comments/example3",
        upvotes: 31,
        downvotes: 5,
      },
      {
        id: "4",
        content:
          "The ethical considerations surrounding AI development are becoming increasingly important. We need to ensure that these powerful tools are developed and deployed responsibly, with proper oversight and consideration for their societal impact.",
        author: "ethics_advocate",
        subreddit: "artificial",
        timestamp: "8 hours ago",
        verdict: "🟢 Likely Human",
        confidence: 78,
        permalink: "/r/artificial/comments/example4",
        upvotes: 42,
        downvotes: 3,
      },
      {
        id: "5",
        content:
          "Natural language processing has made significant strides in recent years. The ability of modern AI systems to understand and generate human-like text is remarkable, though it also raises important questions about authenticity and detection.",
        author: "nlp_specialist",
        subreddit: "MachineLearning",
        timestamp: "10 hours ago",
        verdict: "🔴 Potentially AI-Generated",
        confidence: 88,
        permalink: "/r/MachineLearning/comments/example5",
        upvotes: 19,
        downvotes: 6,
      },
    ]

    const mockData: DashboardData = {
      total_triggers: 1247,
      verdict_distribution: {
        "🔴 Potentially AI-Generated": 156,
        "🟡 Possibly AI-Generated": 89,
        "🟢 Likely Human": 234,
      },
      recent_triggers: mockComments,
      subreddit_activity: {
        artificial: 45,
        MachineLearning: 38,
        ChatGPT: 29,
        OpenAI: 22,
        technology: 18,
      },
    }

    setData(mockData)
    setLastUpdated(new Date())
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatCards = () => {
    if (!data) return []

    const totalVerdicts = Object.values(data.verdict_distribution).reduce((a, b) => a + b, 0)

    return [
      {
        title: "Total Triggers",
        value: data.total_triggers.toLocaleString(),
        icon: Bot,
        color: "text-blue-500",
        bgColor: "bg-gradient-to-br from-blue-50 to-blue-100",
        description: "All-time detections",
      },
      {
        title: "AI Detected",
        value: `${Math.round((data.verdict_distribution["🔴 Potentially AI-Generated"] / totalVerdicts) * 100)}%`,
        icon: Zap,
        color: "text-red-500",
        bgColor: "bg-gradient-to-br from-red-50 to-red-100",
        description: "Potentially AI-generated",
      },
      {
        title: "Human Content",
        value: `${Math.round((data.verdict_distribution["🟢 Likely Human"] / totalVerdicts) * 100)}%`,
        icon: Users,
        color: "text-green-500",
        bgColor: "bg-gradient-to-br from-green-50 to-green-100",
        description: "Likely human-written",
      },
      {
        title: "Active Subreddits",
        value: Object.keys(data.subreddit_activity).length.toString(),
        icon: TrendingUp,
        color: "text-purple-500",
        bgColor: "bg-gradient-to-br from-purple-50 to-purple-100",
        description: "Communities monitored",
      },
    ]
  }

  if (loading && !data) {
    return (
      <div className="min-h-screen relative">
        <ParticlesBackground />
        <div className="relative z-10 flex items-center justify-center min-h-screen">
          <div className="text-center bg-white/90 backdrop-blur-sm rounded-2xl p-8 shadow-2xl border border-white/20">
            <Bot className="h-16 w-16 animate-pulse mx-auto mb-6 text-blue-500" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Loading Dashboard</h2>
            <p className="text-gray-600">Initializing AI detection monitoring...</p>
            <div className="mt-4 w-48 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500 rounded-full animate-pulse" style={{ width: "60%" }} />
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen relative">
      <ParticlesBackground />

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-3 mb-6">
            <div className="p-3 bg-white/20 backdrop-blur-sm rounded-2xl border border-white/30">
              <Bot className="h-8 w-8 text-blue-600" />
            </div>
            <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent">
              Reddit AI Detection Bot
            </h1>
          </div>
          <p className="text-xl text-gray-700 mb-8 max-w-2xl mx-auto">
            Real-time monitoring and analytics dashboard with advanced AI detection capabilities
          </p>

          <div className="flex items-center justify-center gap-6 mb-8">
            {lastUpdated && (
              <div className="text-sm text-gray-600 bg-white/60 backdrop-blur-sm px-4 py-2 rounded-full border border-white/30">
                <Clock className="inline h-4 w-4 mr-2" />
                Last updated: {lastUpdated.toLocaleTimeString()}
              </div>
            )}
            <button
              onClick={fetchData}
              disabled={loading}
              className="flex items-center gap-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-6 py-2 rounded-full transition-all duration-300 disabled:opacity-50 shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
              Refresh Data
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        {data && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {getStatCards().map((stat, index) => (
              <StatCard key={index} {...stat} />
            ))}
          </div>
        )}

        {/* Recent Comments */}
        {data && (
          <div className="bg-white/40 backdrop-blur-sm rounded-3xl p-8 shadow-2xl border border-white/30">
            <div className="flex items-center gap-3 mb-8">
              <div className="p-2 bg-orange-100 rounded-xl">
                <Activity className="h-6 w-6 text-orange-600" />
              </div>
              <h2 className="text-3xl font-bold text-gray-800">Recent AI Detections</h2>
            </div>
            <div className="space-y-6">
              {data.recent_triggers.map((comment) => (
                <SpotlightCard key={comment.id} comment={comment} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
