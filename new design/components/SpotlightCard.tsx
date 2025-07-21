"use client"

import type React from "react"
import { useRef, useState } from "react"
import { ExternalLink, ThumbsUp, ThumbsDown, Clock, User, MessageSquare } from "lucide-react"

interface Comment {
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
}

interface SpotlightCardProps {
  comment: Comment
  onVerdictChange?: (commentId: string, newVerdict: string) => void
}

export const SpotlightCard: React.FC<SpotlightCardProps> = ({ comment, onVerdictChange }) => {
  const divRef = useRef<HTMLDivElement>(null)
  const [isFocused, setIsFocused] = useState(false)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [opacity, setOpacity] = useState(0)
  const [isExpanded, setIsExpanded] = useState(false)

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!divRef.current || isFocused) return

    const div = divRef.current
    const rect = div.getBoundingClientRect()

    setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top })
  }

  const handleFocus = () => {
    setIsFocused(true)
    setOpacity(1)
  }

  const handleBlur = () => {
    setIsFocused(false)
    setOpacity(0)
  }

  const handleMouseEnter = () => {
    setOpacity(1)
  }

  const handleMouseLeave = () => {
    setOpacity(0)
  }

  const getVerdictColor = (verdict: string) => {
    if (verdict.includes("🔴")) return "border-red-200 bg-red-50/50"
    if (verdict.includes("🟡")) return "border-yellow-200 bg-yellow-50/50"
    if (verdict.includes("🟢")) return "border-green-200 bg-green-50/50"
    return "border-gray-200 bg-gray-50/50"
  }

  const getVerdictBadgeColor = (verdict: string) => {
    if (verdict.includes("🔴")) return "bg-red-100 text-red-800 border-red-300"
    if (verdict.includes("🟡")) return "bg-yellow-100 text-yellow-800 border-yellow-300"
    if (verdict.includes("🟢")) return "bg-green-100 text-green-800 border-green-300"
    return "bg-gray-100 text-gray-800 border-gray-300"
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence > 80) return "bg-red-500"
    if (confidence > 60) return "bg-yellow-500"
    return "bg-green-500"
  }

  const truncateContent = (content: string, maxLength = 200) => {
    if (content.length <= maxLength) return content
    return content.substring(0, maxLength) + "..."
  }

  return (
    <div
      ref={divRef}
      onMouseMove={handleMouseMove}
      onFocus={handleFocus}
      onBlur={handleBlur}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className={`relative overflow-hidden rounded-xl border-2 ${getVerdictColor(
        comment.verdict,
      )} p-6 shadow-lg transition-all duration-300 hover:shadow-xl backdrop-blur-sm bg-white/80`}
    >
      {/* Spotlight Effect */}
      <div
        className="pointer-events-none absolute -inset-px opacity-0 transition duration-300"
        style={{
          opacity,
          background: `radial-gradient(600px circle at ${position.x}px ${position.y}px, rgba(255,255,255,.4), transparent 40%)`,
        }}
      />

      {/* Header */}
      <div className="relative z-10 flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <User className="h-4 w-4 opacity-60" />
            <span className="font-medium text-sm text-gray-700">u/{comment.author}</span>
          </div>
          <div className="flex items-center space-x-2">
            <MessageSquare className="h-4 w-4 opacity-60" />
            <a
              href={`https://reddit.com/r/${comment.subreddit}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center space-x-1 transition-colors"
            >
              <span>r/{comment.subreddit}</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Clock className="h-4 w-4 opacity-60" />
          <span className="text-xs opacity-75 text-gray-600">{comment.timestamp}</span>
        </div>
      </div>

      {/* Content */}
      <div className="relative z-10 mb-4">
        <p className="text-gray-800 leading-relaxed">
          {isExpanded ? comment.content : truncateContent(comment.content)}
        </p>
        {comment.content.length > 200 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium mt-2 transition-colors"
          >
            {isExpanded ? "Show less" : "Show more"}
          </button>
        )}
      </div>

      {/* Verdict and Actions */}
      <div className="relative z-10 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span
            className={`px-3 py-1 rounded-full text-xs font-medium border ${getVerdictBadgeColor(comment.verdict)}`}
          >
            {comment.verdict}
          </span>
          <div className="flex items-center space-x-2">
            <div className="w-16 bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${getConfidenceColor(comment.confidence)}`}
                style={{ width: `${comment.confidence}%` }}
              />
            </div>
            <span className="text-xs opacity-75 text-gray-600">{comment.confidence}%</span>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {comment.upvotes !== undefined && (
            <div className="flex items-center space-x-1 text-green-600">
              <ThumbsUp className="h-4 w-4" />
              <span className="text-sm">{comment.upvotes}</span>
            </div>
          )}
          {comment.downvotes !== undefined && (
            <div className="flex items-center space-x-1 text-red-600">
              <ThumbsDown className="h-4 w-4" />
              <span className="text-sm">{comment.downvotes}</span>
            </div>
          )}
          <a
            href={`https://reddit.com${comment.permalink}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 transition-colors"
          >
            <ExternalLink className="h-4 w-4" />
          </a>
        </div>
      </div>
    </div>
  )
}
