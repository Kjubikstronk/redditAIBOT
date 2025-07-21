"use client"

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts"

interface VerdictChartProps {
  data: Record<string, number>
}

export function VerdictChart({ data }: VerdictChartProps) {
  const chartData = Object.entries(data).map(([verdict, count]) => ({
    name: verdict,
    value: count,
    percentage: Math.round((count / Object.values(data).reduce((a, b) => a + b, 0)) * 100),
  }))

  const COLORS = {
    "🔴 Potentially AI-Generated": "#ef4444",
    "🟡 Possibly AI-Generated": "#f59e0b",
    "🟢 Likely Human": "#22c55e",
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white dark:bg-slate-800 p-3 rounded-lg shadow-lg border">
          <p className="font-medium">{data.name}</p>
          <p className="text-sm text-muted-foreground">
            Count: {data.value} ({data.percentage}%)
          </p>
        </div>
      )
    }
    return null
  }

  if (chartData.length === 0) {
    return <div className="flex items-center justify-center h-64 text-muted-foreground">No data available</div>
  }

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={chartData} cx="50%" cy="50%" innerRadius={40} outerRadius={80} paddingAngle={5} dataKey="value">
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS] || "#8884d8"} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend verticalAlign="bottom" height={36} formatter={(value) => value.replace(/[🔴🟡🟢]\s/u, "")} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
