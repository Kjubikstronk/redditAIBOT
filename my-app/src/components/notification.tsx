"use client";
import { cn } from "@/lib/utils";
import React, { ReactNode } from "react";

export const Notification = ({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) => {
  return (
    <div
      className={cn(
        "group relative flex items-center p-4 rounded-lg shadow-lg bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm",
        className
      )}
    >
      <div className="flex-1">{children}</div>
    </div>
  );
}; 