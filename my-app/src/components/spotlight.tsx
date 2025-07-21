"use client";
import { cn } from "@/lib/utils";
import React, { useRef, useEffect } from "react";

export const Spotlight = ({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const container = containerRef.current;
      if (!container) return;
      const rect = container.getBoundingClientRect();
      container.style.setProperty("--mouse-x", `${e.clientX - rect.left}`);
      container.style.setProperty("--mouse-y", `${e.clientY - rect.top}`);
    };

    const container = containerRef.current;
    if (!container) return;
    container.addEventListener("mousemove", handleMouseMove);

    return () => {
      container.removeEventListener("mousemove", handleMouseMove);
    };
  }, []);

  return (
    <div
      className={cn("group relative", className)}
      ref={containerRef}
    >
      <div
        className="pointer-events-none absolute -inset-px rounded-lg opacity-0 transition-all duration-300 group-hover:opacity-100"
        style={{
          background: `
            radial-gradient(
              400px at var(--mouse-x, 0)px var(--mouse-y, 0)px,
              rgba(255, 255, 255, 0.05),
              transparent 80%
            )
          `,
        }}
      />
      {children}
    </div>
  );
}; 