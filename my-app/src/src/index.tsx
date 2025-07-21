import { createRoot } from "react-dom/client"
import { Dashboard } from "./components/Dashboard"
import "./styles.css"

// Initialize the React app when the DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("react-dashboard")
  if (container) {
    const root = createRoot(container)
    root.render(<Dashboard />)
  }
})
