'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Send, Plus, Menu, MessageSquare } from 'lucide-react'
import { MessageList, useMessageList, type VirtuosoMessage, type VirtuosoMessageListProps } from '@/components/MessageList'
import UserProfile from '@/components/UserProfile'

// 自定义消息内容组件
const CustomItemContent: VirtuosoMessageListProps<VirtuosoMessage, null>['ItemContent'] = ({ data }) => {
  const isOwnMessage = data.user === 'me'
  return (
    <div className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-2 ${
          isOwnMessage
            ? 'bg-primary text-primary-foreground'
            : 'bg-muted'
        }`}
      >
        <p className="text-sm">{data.text}</p>
        {data.timestamp && (
          <p className="text-xs opacity-70 mt-1">
            {new Date(data.timestamp).toLocaleTimeString()}
          </p>
        )}
      </div>
    </div>
  )
}

export default function Home() {
  const [inputValue, setInputValue] = useState('')
  const [conversations, setConversations] = useState([
    { id: '1', title: '新对话', active: true }
  ])
  const [activeConversationId, setActiveConversationId] = useState('1')
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const { ref: messageListRef, sendMessage, receiveMessage } = useMessageList()

  // 初始化欢迎消息
  useEffect(() => {
    setTimeout(() => {
      receiveMessage?.('你好！我是 AgenticZero AI 助手。有什么可以帮助你的吗？')
    }, 500)
  }, [])

  const handleSendMessage = () => {
    if (inputValue.trim()) {
      // 发送用户消息
      sendMessage?.(inputValue)
      setInputValue('')
      
      // 模拟AI回复
      setTimeout(() => {
        receiveMessage?.('这是AI的回复。我正在处理您的请求...')
      }, 1000)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const startNewConversation = () => {
    const newId = Date.now().toString()
    const newConversation = {
      id: newId,
      title: '新对话',
      active: true
    }
    setConversations([...conversations, newConversation])
    setActiveConversationId(newId)
    // 清空消息列表需要重新实现
    window.location.reload() // 临时解决方案
  }

  return (
    <div className="flex h-screen bg-background">
      {/* 侧边栏 */}
      <div className={`${isSidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 bg-muted border-r border-border overflow-hidden`}>
        <div className="flex flex-col h-full">
          <div className="p-4">
            <Button 
              onClick={startNewConversation} 
              className="w-full mb-4 justify-start"
              variant="outline"
            >
              <Plus className="mr-2 h-4 w-4" />
              新对话
            </Button>
          </div>
          
          <ScrollArea className="flex-1 px-4">
            <div className="space-y-2">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    conv.id === activeConversationId
                      ? 'bg-background border border-border'
                      : 'hover:bg-background/50'
                  }`}
                  onClick={() => {
                    setActiveConversationId(conv.id)
                    // 切换对话需要重新实现
                  }}
                >
                  <div className="flex items-center">
                    <MessageSquare className="mr-2 h-4 w-4" />
                    <span className="text-sm truncate">{conv.title}</span>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
          
          {/* 用户信息区域 */}
          <div className="p-4 border-t border-border">
            <UserProfile />
          </div>
        </div>
      </div>

      {/* 主聊天区域 */}
      <div className="flex-1 flex flex-col">
        {/* 顶部栏 */}
        <div className="h-14 border-b border-border flex items-center px-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          >
            <Menu className="h-5 w-5" />
          </Button>
          <h1 className="ml-4 text-lg font-semibold">AgenticZero Chat</h1>
        </div>

        {/* 消息区域 */}
        <div className="flex-1 overflow-hidden p-4">
          <div className="max-w-3xl mx-auto h-full">
            <MessageList
              ref={messageListRef}
              style={{ height: '100%' }}
              licenseKey="" // 如果需要许可证密钥，请在此处添加
              ItemContent={CustomItemContent}
            />
          </div>
        </div>

        {/* 输入区域 */}
        <div className="border-t border-border p-4">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-2">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="输入消息..."
                className="flex-1"
              />
              <Button onClick={handleSendMessage} disabled={!inputValue.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2 text-center">
              AgenticZero 可能会产生错误信息。请核实重要信息。
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}