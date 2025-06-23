'use client'

export interface MessageReaction {
  type: 'like' | 'dislike'
  count: number
  userReacted?: boolean
}

export interface Message {
  key: string
  text: string
  user: 'user' | 'ai'
  timestamp: Date
  reactions?: MessageReaction[]
  avatar?: string
  delivered?: boolean
}