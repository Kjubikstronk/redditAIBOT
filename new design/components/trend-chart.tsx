"use client"

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

interface TrendChartProps {
  data: {
    labels: string[]
    datasets: Record<string, number[]>
  }
}

export function TrendChart({ data }: TrendChartProps) {
  if (!data || !data.labels || data.labels.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-muted-foreground">
        <p>Not enough data for trend analysis</p>
      </div>
    )
  }

  const chartData = data.labels.map((label, index) => {
    const point: any = { date: label }
    Object.entries(data.datasets).forEach(([verdict, values]) => {
      point[verdict] = values[index] || 0
    })
    return point
  })

  const colors = {
    "🔴 Potentially AI-Generated": "#ef4444",
    "🟡 Possibly AI-Generated": "#f59e0b",
    "🟢 Likely Human": "#22c55e",
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-slate-800 p-3 rounded-lg shadow-lg border">
          <p className="font-medium mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.dataKey.replace(/[🔴🟡🟢]\s/u, "")}: {entry.value}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis dataKey="date" className="text-xs" tick={{ fontSize: 12 }} />
          <YAxis className="text-xs" tick={{ fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend formatter={(value) => value.replace(/[🔴🟡🟢]\s/u, "")} />
          {Object.keys(data.datasets).map((verdict) => (
            <Line
              key={verdict}
              type="monotone"
              dataKey={verdict}
              stroke={colors[verdict as keyof typeof colors] || "#8884d8"}
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
