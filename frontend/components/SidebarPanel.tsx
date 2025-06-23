'use client'

import React from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'

interface SidebarPanelProps {
  title?: string
  children: React.ReactNode
  className?: string
  width?: 'sm' | 'md' | 'lg'
  side?: 'left' | 'right'
}

export default function SidebarPanel({ 
  title, 
  children, 
  className,
  width = 'md',
  side = 'left'
}: SidebarPanelProps) {
  const widthClasses = {
    sm: 'w-64',
    md: 'w-80',
    lg: 'w-96'
  }

  const borderClass = side === 'left' ? 'border-r' : 'border-l'

  return (
    <aside className={cn(
      widthClasses[width],
      borderClass,
      'bg-muted/10 flex flex-col',
      className
    )}>
      {title && (
        <div className="p-6 pb-0">
          <h2 className="text-sm font-semibold mb-4">{title}</h2>
        </div>
      )}
      <ScrollArea className="flex-1">
        <div className={cn(
          'space-y-6',
          title ? 'px-6 pb-6' : 'p-6'
        )}>
          {children}
        </div>
      </ScrollArea>
    </aside>
  )
}