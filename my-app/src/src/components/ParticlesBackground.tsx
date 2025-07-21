"use client"

import type React from "react"
import { useEffect, useRef, useCallback } from "react"

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  opacity: number
  color: string
  life: number
  maxLife: number
}

interface ParticlesBackgroundProps {
  particleCount?: number
  colors?: string[]
  speed?: number
  connectionDistance?: number
}

export const ParticlesBackground: React.FC<ParticlesBackgroundProps> = ({
  particleCount = 50,
  colors = ["#3b82f6", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b"],
  speed = 0.5,
  connectionDistance = 120,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const particlesRef = useRef<Particle[]>([])
  const animationRef = useRef<number>()
  const mouseRef = useRef({ x: 0, y: 0 })

  const createParticle = useCallback(
    (x?: number, y?: number): Particle => ({
      x: x ?? Math.random() * window.innerWidth,
      y: y ?? Math.random() * window.innerHeight,
      vx: (Math.random() - 0.5) * speed,
      vy: (Math.random() - 0.5) * speed,
      size: Math.random() * 3 + 1,
      opacity: Math.random() * 0.8 + 0.2,
      color: colors[Math.floor(Math.random() * colors.length)],
      life: 0,
      maxLife: Math.random() * 200 + 100,
    }),
    [colors, speed],
  )

  const initParticles = useCallback(() => {
    particlesRef.current = Array.from({ length: particleCount }, () => createParticle())
  }, [particleCount, createParticle])

  const updateParticle = useCallback(
    (particle: Particle, canvas: HTMLCanvasElement) => {
      // Update position
      particle.x += particle.vx
      particle.y += particle.vy
      particle.life++

      // Mouse interaction
      const dx = mouseRef.current.x - particle.x
      const dy = mouseRef.current.y - particle.y
      const distance = Math.sqrt(dx * dx + dy * dy)

      if (distance < 100) {
        const force = (100 - distance) / 100
        particle.vx += (dx / distance) * force * 0.01
        particle.vy += (dy / distance) * force * 0.01
      }

      // Boundary collision
      if (particle.x < 0 || particle.x > canvas.width) {
        particle.vx *= -0.8
        particle.x = Math.max(0, Math.min(canvas.width, particle.x))
      }
      if (particle.y < 0 || particle.y > canvas.height) {
        particle.vy *= -0.8
        particle.y = Math.max(0, Math.min(canvas.height, particle.y))
      }

      // Fade effect based on life
      const lifeRatio = particle.life / particle.maxLife
      particle.opacity = Math.max(0, 0.8 - lifeRatio)

      // Reset particle if it's too old
      if (particle.life >= particle.maxLife) {
        Object.assign(particle, createParticle())
      }
    },
    [createParticle],
  )

  const drawParticle = useCallback((ctx: CanvasRenderingContext2D, particle: Particle) => {
    ctx.save()
    ctx.globalAlpha = particle.opacity
    ctx.fillStyle = particle.color
    ctx.beginPath()
    ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
    ctx.fill()
    ctx.restore()
  }, [])

  const drawConnection = useCallback(
    (ctx: CanvasRenderingContext2D, p1: Particle, p2: Particle, distance: number) => {
      const opacity = Math.max(0, (connectionDistance - distance) / connectionDistance) * 0.3
      ctx.save()
      ctx.globalAlpha = opacity
      ctx.strokeStyle = p1.color
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(p1.x, p1.y)
      ctx.lineTo(p2.x, p2.y)
      ctx.stroke()
      ctx.restore()
    },
    [connectionDistance],
  )

  const animate = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Clear canvas with fade effect
    ctx.fillStyle = "rgba(248, 250, 252, 0.1)"
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    // Update and draw particles
    particlesRef.current.forEach((particle) => {
      updateParticle(particle, canvas)
      drawParticle(ctx, particle)
    })

    // Draw connections
    for (let i = 0; i < particlesRef.current.length; i++) {
      for (let j = i + 1; j < particlesRef.current.length; j++) {
        const p1 = particlesRef.current[i]
        const p2 = particlesRef.current[j]
        const dx = p1.x - p2.x
        const dy = p1.y - p2.y
        const distance = Math.sqrt(dx * dx + dy * dy)

        if (distance < connectionDistance) {
          drawConnection(ctx, p1, p2, distance)
        }
      }
    }

    animationRef.current = requestAnimationFrame(animate)
  }, [updateParticle, drawParticle, drawConnection, connectionDistance])

  const handleResize = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
    initParticles()
  }, [initParticles])

  const handleMouseMove = useCallback((e: MouseEvent) => {
    mouseRef.current = { x: e.clientX, y: e.clientY }
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    handleResize()
    animate()

    window.addEventListener("resize", handleResize)
    window.addEventListener("mousemove", handleMouseMove)

    return () => {
      window.removeEventListener("resize", handleResize)
      window.removeEventListener("mousemove", handleMouseMove)
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [handleResize, animate, handleMouseMove])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{
        background: "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%)",
      }}
    />
  )
}
