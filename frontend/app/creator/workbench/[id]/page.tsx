'use client'

import React, { useState, useRef, useEffect } from 'react'
import { MessageList, useMessageList, Message } from '@/components/MessageList'
import { MessageBubble } from '@/components/MessageBubble'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { Send, Save, Lightbulb, CheckCircle2, AlertCircle, GraduationCap, Users, Loader2, BarChart3, MessageSquare } from 'lucide-react'
import SidebarPanel from '@/components/SidebarPanel'


// 将 Message 类型转换为 MessageBubble 所需的格式
const convertMessageForBubble = (msg: Message) => ({
  ...msg,
  user: msg.user === 'me' ? 'user' : 'ai' as 'user' | 'ai',
  timestamp: msg.timestamp || new Date()
})

interface WorkbenchPageProps {
  params: {
    id: string
  }
}

export default function WorkbenchPage({ params }: WorkbenchPageProps) {
  const [aiName, setAiName] = useState('AI助教')
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { ref: messageListRef, sendMessage, receiveMessage } = useMessageList()
  
  // 模拟的AI助教数据（实际应该从数据库获取）
  const mockAiAssistants: Record<string, { name: string; subject: string }> = {
    'ai-1': { name: 'Python 编程导师', subject: 'Python编程' },
    'ai-2': { name: '数学小助手', subject: '高等数学' },
    'ai-3': { name: '英语口语教练', subject: '英语口语' },
  }
  
  useEffect(() => {
    // 从ID获取教师信息，或从ID中解析名称
    let teacherName = 'AI助教'
    
    if (params.id.startsWith('ai-')) {
      // 对于已存在的助教，从模拟数据获取
      const assistant = mockAiAssistants[params.id]
      if (assistant) {
        teacherName = assistant.name
      }
    } else {
      // 对于新创建的助教，从ID中解析名称（移除时间戳）
      const nameMatch = params.id.match(/(.+)-\d+$/)
      if (nameMatch) {
        teacherName = nameMatch[1].replace(/-/g, ' ')
        // 首字母大写
        teacherName = teacherName.split(' ')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ')
      }
    }
    
    setAiName(teacherName)
    
    // 使用 setTimeout 确保组件已经挂载
    setTimeout(() => {
      receiveMessage(`您好！我是${teacherName}，我将跟随您学习知识和教学方法。请开始教授我吧！`)
    }, 100)
  }, [params.id, receiveMessage])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim() || isLoading) return

    const messageText = inputValue.trim()
    setInputValue('')
    setIsLoading(true)

    // 使用 MessageList 的 sendMessage 方法
    sendMessage(messageText)

    // 模拟AI响应
    setTimeout(() => {
      // 初始消息内容
      const initialText = `我理解了，您刚才教授的是：${messageText}。`
      
      // 使用 MessageList 的 receiveMessage 方法
      receiveMessage(initialText)

      // 准备逐步添加的消息
      const additionalTexts = [
        '让我总结一下关键点...',
        '这个知识点很重要。',
        '我会认真学习并掌握它。',
        '您还有什么需要补充的吗？'
      ]
      
      // 逐个添加额外的消息
      additionalTexts.forEach((text, index) => {
        setTimeout(() => {
          receiveMessage(text)
          if (index === additionalTexts.length - 1) {
            setIsLoading(false)
          }
        }, (index + 1) * 500)
      })
    }, 1000)
  }

  return (
    <div className="h-screen bg-background flex flex-col">
      <header className="flex-shrink-0 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex h-14 items-center px-6">
          <div className="flex items-center gap-4 flex-1">
            <GraduationCap className="h-6 w-6 text-primary" />
            <div>
              <h1 className="text-lg font-semibold">AI 助教训练中心</h1>
              <p className="text-xs text-muted-foreground">正在培养: {aiName}</p>
            </div>
          </div>
          <Button variant="outline" size="sm">
            <Save className="h-4 w-4" />
            保存进度
          </Button>
        </div>
      </header>
      
      <div className="flex-1 flex min-h-0">
        <SidebarPanel side="left">
              <div>
                <h2 className="text-sm font-semibold mb-4">训练进度</h2>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">基础知识</span>
                      <span className="text-sm text-muted-foreground">30%</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div className="bg-primary h-2 rounded-full transition-all" style={{ width: '30%' }}></div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">教学方法</span>
                      <span className="text-sm text-muted-foreground">10%</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div className="bg-primary h-2 rounded-full transition-all" style={{ width: '10%' }}></div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">案例学习</span>
                      <span className="text-sm text-muted-foreground">0%</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div className="bg-primary h-2 rounded-full transition-all" style={{ width: '0%' }}></div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="h-px bg-border" />
              
              <div>
                <h2 className="text-sm font-semibold mb-4">培养提示</h2>
                <div className="space-y-3">
                  <Card className="border-blue-200 bg-blue-50/50 dark:bg-blue-950/20">
                    <CardContent className="p-3">
                      <div className="flex gap-3">
                        <Lightbulb className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                        <div className="space-y-1">
                          <p className="text-sm font-medium">建议</p>
                          <p className="text-xs text-muted-foreground">从简单概念开始，逐步深入复杂知识</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card className="border-green-200 bg-green-50/50 dark:bg-green-950/20">
                    <CardContent className="p-3">
                      <div className="flex gap-3">
                        <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400 mt-0.5 flex-shrink-0" />
                        <div className="space-y-1">
                          <p className="text-sm font-medium">技巧</p>
                          <p className="text-xs text-muted-foreground">使用具体例子帮助 AI 理解抽象概念</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card className="border-yellow-200 bg-yellow-50/50 dark:bg-yellow-950/20">
                    <CardContent className="p-3">
                      <div className="flex gap-3">
                        <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" />
                        <div className="space-y-1">
                          <p className="text-sm font-medium">注意</p>
                          <p className="text-xs text-muted-foreground">定期测试 AI 的理解程度</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
              
              <div className="h-px bg-border" />
              
              <div>
                <h2 className="text-sm font-semibold mb-4">快速操作</h2>
                <div className="space-y-2">
                  <Button variant="outline" size="sm" className="w-full justify-start">
                    <MessageSquare className="h-4 w-4" />
                    查看对话历史
                  </Button>
                  <Button variant="outline" size="sm" className="w-full justify-start">
                    <BarChart3 className="h-4 w-4" />
                    学习分析
                  </Button>
                </div>
              </div>
        </SidebarPanel>
        
        <main className="flex-1 flex flex-col">
          <div className="flex-shrink-0 border-b px-6 py-4">
            <h2 className="text-lg font-semibold">训练对话</h2>
            <p className="text-sm text-muted-foreground">通过自然对话向 {aiName} 传授您的知识</p>
          </div>
          
          <div className="flex-1 flex flex-col overflow-hidden bg-muted/20">
            <MessageList
              ref={messageListRef}
              initialMessages={[]}
              ItemContent={({ data }) => (
                <MessageBubble 
                  data={convertMessageForBubble(data)}
                  config={{
                    userColor: 'bg-primary text-primary-foreground',
                    aiColor: 'bg-muted border border-border',
                    showAvatars: true,
                    userAvatar: <Users className="h-4 w-4 text-primary" />,
                    aiAvatar: <GraduationCap className="h-4 w-4 text-primary" />,
                    showTimestamp: true
                  }}
                />
              )}
              licenseKey=""
            />
          </div>

          <div className="flex-shrink-0 border-t bg-background p-4">
            <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto">
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <Input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="输入您想教授的知识或教学方法..."
                    disabled={isLoading}
                    className="pr-12"
                  />
                  {isLoading && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                      <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                    </div>
                  )}
                </div>
                <Button
                  type="submit"
                  disabled={!inputValue.trim() || isLoading}
                  size="icon"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </form>
          </div>
        </main>
      </div>
    </div>
  )
}