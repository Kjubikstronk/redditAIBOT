"use client"

import type React from "react"
import { useState } from "react"
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

interface CommentCardProps {
  comment: Comment
  onVerdictChange?: (commentId: string, newVerdict: string) => void
}

export const CommentCard: React.FC<CommentCardProps> = ({ comment, onVerdictChange }) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isHovered, setIsHovered] = useState(false)

  const getVerdictColor = (verdict: string) => {
    if (verdict.includes("🔴")) return "bg-red-50 border-red-200 text-red-800"
    if (verdict.includes("🟡")) return "bg-yellow-50 border-yellow-200 text-yellow-800"
    if (verdict.includes("🟢")) return "bg-green-50 border-green-200 text-green-800"
    return "bg-gray-50 border-gray-200 text-gray-800"
  }

  const getVerdictBadgeColor = (verdict: string) => {
    if (verdict.includes("🔴")) return "bg-red-100 text-red-800 border-red-300"
    if (verdict.includes("🟡")) return "bg-yellow-100 text-yellow-800 border-yellow-300"
    if (verdict.includes("🟢")) return "bg-green-100 text-green-800 border-green-300"
    return "bg-gray-100 text-gray-800 border-gray-300"
  }

  const truncateContent = (content: string, maxLength = 200) => {
    if (content.length <= maxLength) return content
    return content.substring(0, maxLength) + "..."
  }

  return (
    <div
      className={`comment-card ${getVerdictColor(comment.verdict)} rounded-xl border-2 p-6 mb-4 transition-all duration-300 transform hover:scale-[1.02] hover:shadow-lg ${
        isHovered ? "shadow-xl" : "shadow-md"
      }`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <User className="h-4 w-4 opacity-60" />
            <span className="font-medium text-sm">u/{comment.author}</span>
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
          <span className="text-xs opacity-75">{comment.timestamp}</span>
        </div>
      </div>

      {/* Content */}
      <div className="mb-4">
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
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span
            className={`px-3 py-1 rounded-full text-xs font-medium border ${getVerdictBadgeColor(comment.verdict)}`}
          >
            {comment.verdict}
          </span>
          <div className="flex items-center space-x-1">
            <div className="w-16 bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${
                  comment.confidence > 80 ? "bg-red-500" : comment.confidence > 60 ? "bg-yellow-500" : "bg-green-500"
                }`}
                style={{ width: `${comment.confidence}%` }}
              ></div>
            </div>
            <span className="text-xs opacity-75">{comment.confidence}%</span>
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
