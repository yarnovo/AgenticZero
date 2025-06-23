'use client'

import React from 'react'
import { VirtuosoMessageListProps } from '@virtuoso.dev/message-list'
import { Message, MessageReaction } from '@/components/types'
import { cn } from '@/lib/utils'
import { GraduationCap, Users, ThumbsUp, ThumbsDown } from 'lucide-react'

export interface MessageBubbleConfig {
  showAvatars?: boolean
  userColor?: string
  aiColor?: string
  userAvatar?: React.ReactNode
  aiAvatar?: React.ReactNode
  messageAlignment?: 'left' | 'right' | 'both'
  maxWidth?: string
  borderStyle?: 'rounded' | 'square'
  showTimestamp?: boolean
  timestampFormat?: 'time' | 'datetime' | 'relative'
  showReactions?: boolean
  onReaction?: (messageKey: string, reactionType: 'like' | 'dislike') => void
}

interface MessageBubbleProps {
  data: Message
  config?: MessageBubbleConfig
  variant?: 'chat' | 'group'
}

const defaultConfig: MessageBubbleConfig = {
  showAvatars: true,
  userColor: 'bg-primary text-primary-foreground',
  aiColor: 'bg-muted text-foreground',
  userAvatar: <Users className="h-4 w-4 text-primary" />,
  aiAvatar: <GraduationCap className="h-4 w-4 text-primary" />,
  messageAlignment: 'both',
  maxWidth: 'max-w-[70%]',
  borderStyle: 'rounded',
  showTimestamp: true,
  timestampFormat: 'time',
  showReactions: false
}

export function MessageBubble({ data, config = {}, variant = 'chat' }: MessageBubbleProps) {
  const settings = { ...defaultConfig, ...config }
  const isUser = data.user === 'user'
  
  const formatTimestamp = (timestamp: Date) => {
    switch (settings.timestampFormat) {
      case 'datetime':
        return timestamp.toLocaleString()
      case 'relative':
        return new Intl.RelativeTimeFormat('zh-CN').format(
          Math.round((timestamp.getTime() - Date.now()) / 60000),
          'minute'
        )
      default:
        return timestamp.toLocaleTimeString()
    }
  }

  const getAlignment = () => {
    if (settings.messageAlignment === 'left') return 'justify-start'
    if (settings.messageAlignment === 'right') return 'justify-end'
    return isUser ? 'justify-end' : 'justify-start'
  }

  const getBorderRadius = () => {
    return settings.borderStyle === 'square' ? 'rounded-none' : 'rounded-lg'
  }

  return (
    <div className={cn("pb-4 flex", getAlignment())}>
      <div className={cn("flex gap-3", settings.maxWidth)}>
        {!isUser && settings.showAvatars && (
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
            {settings.aiAvatar}
          </div>
        )}
        <div
          className={cn(
            "px-4 py-2.5 shadow-sm",
            getBorderRadius(),
            isUser ? settings.userColor : settings.aiColor
          )}
        >
          <p className="text-sm whitespace-pre-wrap">{data.text}</p>
          {settings.showTimestamp && (
            <p className={cn(
              "text-xs mt-1",
              isUser ? "opacity-70" : "opacity-60"
            )}>
              {formatTimestamp(data.timestamp)}
            </p>
          )}
        </div>
        {isUser && settings.showAvatars && (
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
            {settings.userAvatar}
          </div>
        )}
      </div>
      {settings.showReactions && data.reactions && data.reactions.length > 0 && (
        <div className="flex gap-2 mt-2 ml-11">
          {data.reactions.map((reaction, index) => (
            <button
              key={index}
              onClick={() => settings.onReaction?.(data.key, reaction.type)}
              className={cn(
                "flex items-center gap-1 px-2 py-1 rounded-full text-xs transition-colors",
                reaction.userReacted
                  ? "bg-primary/20 text-primary"
                  : "bg-muted hover:bg-muted/80"
              )}
            >
              {reaction.type === 'like' ? (
                <ThumbsUp className="h-3 w-3" />
              ) : (
                <ThumbsDown className="h-3 w-3" />
              )}
              <span>{reaction.count}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

// 用于 VirtuosoMessageList 的 ItemContent 组件
export const createMessageItemContent = (config?: MessageBubbleConfig, variant?: 'chat' | 'group'): VirtuosoMessageListProps<Message, null>['ItemContent'] => {
  return ({ data }) => <MessageBubble data={data} config={config} variant={variant} />
}