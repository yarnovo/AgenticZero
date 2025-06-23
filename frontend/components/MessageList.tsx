'use client'

import * as React from 'react'
import {
  VirtuosoMessageList,
  VirtuosoMessageListLicense,
  VirtuosoMessageListMethods,
  VirtuosoMessageListProps,
  useVirtuosoMethods,
  ListScrollLocation
} from '@virtuoso.dev/message-list'

// 消息接口定义
export interface VirtuosoMessage {
  key: string
  text: string
  user: 'me' | 'other'
  timestamp?: Date
  avatar?: string
  delivered?: boolean
  localId?: number | null
  liked?: boolean
  replyTo?: string
  highlighted?: boolean
}


// 组件props
export interface VirtuosoMessageListWrapperProps {
  licenseKey?: string
  style?: React.CSSProperties
  initialMessages?: VirtuosoMessage[]
  onSendMessage?: (text: string) => void
  onReceiveMessage?: () => void
  onUpdateMessage?: (messageKey: string, updates: Partial<VirtuosoMessage>) => void
  ItemContent?: VirtuosoMessageListProps<VirtuosoMessage, null>['ItemContent']
}

// 默认消息内容组件
const DefaultItemContent: VirtuosoMessageListProps<VirtuosoMessage, null>['ItemContent'] = ({ data }) => {
  const ownMessage = data.user === 'me'
  return (
    <div style={{ paddingBottom: '2rem', display: 'flex' }}>
      <div
        style={{
          maxWidth: '80%',
          marginLeft: ownMessage ? 'auto' : undefined,
          backgroundColor: ownMessage ? 'var(--background)' : 'var(--alt-background)',
          color: 'var(--foreground)',
          border: '1px solid var(--border)',
          borderRadius: '1rem',
          padding: '1rem'
        }}
      >
        {data.text}
        {data.delivered === false && <div style={{ textAlign: 'right', fontSize: '0.8em', opacity: 0.7 }}>Delivering...</div>}
      </div>
    </div>
  )
}

// 主要的封装组件
export const VirtuosoMessageListWrapper = React.forwardRef<
  VirtuosoMessageListMethods<VirtuosoMessage>,
  VirtuosoMessageListWrapperProps
>(({
  licenseKey = '',
  style,
  initialMessages = [],
  onSendMessage,
  onReceiveMessage,
  onUpdateMessage,
  ItemContent
}, ref) => {
  const virtuoso = React.useRef<VirtuosoMessageListMethods<VirtuosoMessage>>(null)
  const [messages, setMessages] = React.useState<VirtuosoMessage[]>(initialMessages)

  // 暴露ref
  React.useImperativeHandle(ref, () => virtuoso.current!, [])


  // API方法
  const sendMessage = React.useCallback((text: string) => {
    const messageKey = `msg-${Date.now()}`
    const newMessage: VirtuosoMessage = {
      key: messageKey,
      text,
      user: 'me',
      timestamp: new Date(),
      delivered: true
    }

    virtuoso.current?.data.append([newMessage], ({ scrollInProgress, atBottom }) => {
      if (atBottom || scrollInProgress) {
        return 'smooth'
      } else {
        return 'auto'
      }
    })

    onSendMessage?.(text)
    return messageKey
  }, [onSendMessage])

  const receiveMessage = React.useCallback((text: string) => {
    const messageKey = `msg-${Date.now()}`
    const newMessage: VirtuosoMessage = {
      key: messageKey,
      text,
      user: 'other',
      timestamp: new Date(),
      delivered: true
    }

    virtuoso.current?.data.append([newMessage], ({ scrollInProgress, atBottom }) => {
      if (atBottom || scrollInProgress) {
        return 'smooth'
      } else {
        return false
      }
    })

    onReceiveMessage?.()
    return messageKey
  }, [onReceiveMessage])

  const updateMessage = React.useCallback((messageKey: string, updates: Partial<VirtuosoMessage>) => {
    virtuoso.current?.data.map((message) => {
      return message.key === messageKey ? { ...message, ...updates } : message
    }, 'smooth')

    onUpdateMessage?.(messageKey, updates)
  }, [onUpdateMessage])

  // 暴露API给父组件
  React.useImperativeHandle(ref, () => ({
    ...virtuoso.current!,
    sendMessage,
    receiveMessage,
    updateMessage
  }), [sendMessage, receiveMessage, updateMessage])


  return (
    <VirtuosoMessageListLicense licenseKey={licenseKey}>
      <VirtuosoMessageList<VirtuosoMessage, any>
        ref={virtuoso}
        initialData={messages}
        computeItemKey={({ data }) => data.key}
        initialLocation={{ index: 'LAST', align: 'end' }}
        shortSizeAlign="bottom-smooth"
        ItemContent={ItemContent || DefaultItemContent}
        style={{ 
          flex: 1,
          fontSize: '70%',
          ...style
        }}
      />
    </VirtuosoMessageListLicense>
  )
})

VirtuosoMessageListWrapper.displayName = 'VirtuosoMessageListWrapper'

// 便利的Hook用于创建消息列表
export function useVirtuosoMessageList(initialMessages: VirtuosoMessage[] = []) {
  const ref = React.useRef<VirtuosoMessageListMethods<VirtuosoMessage> & {
    sendMessage: (text: string) => string
    receiveMessage: (text: string) => string
    updateMessage: (messageKey: string, updates: Partial<VirtuosoMessage>) => void
  }>(null)

  return {
    ref,
    sendMessage: (text: string) => ref.current?.sendMessage(text),
    receiveMessage: (text: string) => ref.current?.receiveMessage(text),
    updateMessage: (messageKey: string, updates: Partial<VirtuosoMessage>) => ref.current?.updateMessage(messageKey, updates)
  }
}

// 重命名导出
export type Message = VirtuosoMessage
export const MessageList = VirtuosoMessageListWrapper
export const useMessageList = useVirtuosoMessageList