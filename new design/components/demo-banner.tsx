import { Badge } from "@/components/ui/badge"
import { Info } from "lucide-react"

export function DemoBanner() {
  return (
    <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/50 dark:to-purple-950/50 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
          <Info className="h-4 w-4 text-blue-600 dark:text-blue-400" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-blue-900 dark:text-blue-100">Demo Mode</h3>
            <Badge variant="secondary" className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
              Live Preview
            </Badge>
          </div>
          <p className="text-sm text-blue-700 dark:text-blue-300">
            You're viewing the dashboard with simulated data. Connect to your Flask backend to see real Reddit bot
            activity.
          </p>
        </div>
      </div>
    </div>
  )
}
