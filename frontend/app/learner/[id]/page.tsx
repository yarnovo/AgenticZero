'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { MessageList, useMessageList, type Message } from '@/components/MessageList'
import { MessageBubble } from '@/components/MessageBubble'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Send, Star, BookOpen, PenTool, BarChart3, Target, Calendar, Loader2, GraduationCap, Trophy, Clock, MessageSquare } from 'lucide-react'
import SidebarPanel from '@/components/SidebarPanel'

interface AITeacher {
  id: string
  name: string
  avatar: string
  subject: string
  description: string
  rating: number
  students: number
  price: number
  mentor?: {
    name: string
    title: string
    experience: string
    achievements: string[]
  }
}

// 模拟数据（实际应该从API获取）
const aiTeachersData: Record<string, AITeacher> = {
  '1': {
    id: '1',
    name: '张老师AI',
    avatar: '👨‍🏫',
    subject: 'Python编程',
    description: '10年编程经验，擅长零基础教学',
    rating: 4.9,
    students: 1234,
    price: 199,
    mentor: {
      name: '张博文',
      title: '前谷歌高级工程师',
      experience: '15年软件开发经验，曾任职于谷歌、微软等顶尖科技公司',
      achievements: [
        'Python软件基金会贡献者',
        '出版《Python深度学习实战》',
        '累计培养学员超过5000人'
      ]
    }
  },
  '2': {
    id: '2',
    name: '李老师AI',
    avatar: '👩‍🏫',
    subject: '英语口语',
    description: '专注商务英语，帮你突破口语难关',
    rating: 4.8,
    students: 892,
    price: 299,
    mentor: {
      name: '李雅婷',
      title: '剑桥认证英语教师',
      experience: '12年英语教学经验，专注商务英语培训',
      achievements: [
        '剑桥大学CELTA认证',
        '前新东方金牌讲师',
        '帮助500+学员通过雅思考试'
      ]
    }
  },
  '3': {
    id: '3',
    name: '王老师AI',
    avatar: '👨‍🎓',
    subject: '数据分析',
    description: '数据科学专家，项目实战导向',
    rating: 4.9,
    students: 567,
    price: 399,
    mentor: {
      name: '王浩然',
      title: '数据科学家',
      experience: '阿里巴巴前数据科学家，10年大数据分析经验',
      achievements: [
        'Kaggle比赛Top 1%',
        '主导多个千万级数据项目',
        '《数据分析实战》作者'
      ]
    }
  }
}

interface LearnerDetailPageProps {
  params: {
    id: string
  }
}

// 将 Message 类型转换为 MessageBubble 所需的格式
const convertMessageForBubble = (msg: Message) => ({
  ...msg,
  user: msg.user === 'me' ? 'user' : 'ai' as 'user' | 'ai',
  timestamp: msg.timestamp || new Date()
})

export default function LearnerDetailPage({ params }: LearnerDetailPageProps) {
  const router = useRouter()
  const [teacher, setTeacher] = useState<AITeacher | null>(null)
  const [learningGoal, setLearningGoal] = useState('')
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { ref: messageListRef, sendMessage, receiveMessage } = useMessageList()

  useEffect(() => {
    // 从模拟数据获取教师信息（实际应该从API获取）
    const teacherData = aiTeachersData[params.id]
    if (teacherData) {
      setTeacher(teacherData)
      // 延迟发送欢迎消息
      setTimeout(() => {
        receiveMessage(`你好！我是${teacherData.name}，很高兴成为你的学习伙伴。首先，让我了解一下你的学习目标吧！你希望通过学习${teacherData.subject}达成什么目标呢？`)
      }, 500)
    } else {
      // 如果找不到教师，返回列表页
      router.push('/learner')
    }
  }, [params.id, router, receiveMessage])

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
      let aiResponse = ''
      
      if (!learningGoal) {
        setLearningGoal(messageText)
        aiResponse = `很好！你的学习目标是"${messageText}"。`
      } else {
        aiResponse = `关于你刚才提到的"${messageText}"，`
      }

      // 使用 MessageList 的 receiveMessage 方法
      receiveMessage(aiResponse)

      // 模拟逐步添加更多消息
      const additionalTexts = !learningGoal ? [
        '让我为你制定一个个性化的学习计划。',
        '基于你的目标，我建议我们从以下几个方面入手：',
        '1. 基础概念理解',
        '2. 实践练习',
        '3. 项目应用',
        '你准备好开始了吗？'
      ] : [
        '让我详细解释一下...',
        '这是一个很好的问题。',
        '在实际应用中，你需要注意以下几点：',
        '你还有其他问题吗？'
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

  if (!teacher) {
    return (
      <div className="h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  return (
    <div className="h-screen bg-background flex flex-col">
      <header className="flex-shrink-0 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex h-14 items-center px-6">
          <div className="flex items-center gap-4 flex-1">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <span className="text-xl">{teacher.avatar}</span>
            </div>
            <div>
              <h1 className="text-lg font-semibold">学成AI学习系统</h1>
              <p className="text-xs text-muted-foreground">正在学习: {teacher.subject}</p>
            </div>
          </div>
          <Button variant="outline" size="sm">
            <MessageSquare className="h-4 w-4" />
            学习历史
          </Button>
        </div>
      </header>
      
      <div className="flex-1 flex min-h-0">
        <SidebarPanel title="学习信息" side="left">
          <div>
            <p className="text-sm text-muted-foreground mb-3">AI教练信息</p>
            <Card className="bg-background">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-2xl">{teacher.avatar}</span>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium">{teacher.name}</p>
                    <p className="text-sm text-muted-foreground">{teacher.subject}</p>
                  </div>
                </div>
                <div className="mt-4 flex items-center justify-between text-sm">
                  <div className="flex items-center gap-1">
                    <Star className="h-3 w-3 text-yellow-500" />
                    <span>{teacher.rating}</span>
                  </div>
                  <div className="flex items-center gap-1 text-muted-foreground">
                    <GraduationCap className="h-3 w-3" />
                    <span>{teacher.students} 学生</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          
          {learningGoal && (
            <div>
              <p className="text-sm text-muted-foreground mb-3">学习目标</p>
              <Card className="bg-blue-50/50 dark:bg-blue-950/20 border-blue-200">
                <CardContent className="p-4">
                  <div className="flex gap-3">
                    <Target className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                    <p className="text-sm">{learningGoal}</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
          
          <div className="h-px bg-border" />
          
          <div>
            <p className="text-sm text-muted-foreground mb-3">学习进度</p>
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm">今日学习</span>
                  <span className="text-sm text-muted-foreground">45%</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-primary h-2 rounded-full transition-all" style={{ width: '45%' }}></div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm">本周目标</span>
                  <span className="text-sm text-muted-foreground">60%</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-primary h-2 rounded-full transition-all" style={{ width: '60%' }}></div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm">总体掌握度</span>
                  <span className="text-sm text-muted-foreground">52%</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full transition-all" style={{ width: '52%' }}></div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="h-px bg-border" />
          
          <div>
            <p className="text-sm text-muted-foreground mb-3">学习统计</p>
            <div className="grid grid-cols-2 gap-3">
              <Card className="bg-background">
                <CardContent className="p-3">
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-xs text-muted-foreground">学习时长</p>
                      <p className="text-sm font-medium">2.5 小时</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-background">
                <CardContent className="p-3">
                  <div className="flex items-center gap-2">
                    <Trophy className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-xs text-muted-foreground">完成任务</p>
                      <p className="text-sm font-medium">12 个</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </SidebarPanel>
        
        <main className="flex-1 flex flex-col">
          <div className="flex-shrink-0 border-b px-6 py-4">
            <h2 className="text-lg font-semibold">学习对话</h2>
            <p className="text-sm text-muted-foreground">正在与 {teacher.name} 学习</p>
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
                    aiColor: 'bg-muted text-foreground',
                    showAvatars: false,
                    showTimestamp: true
                  }}
                />
              )}
              licenseKey=""
            />
          </div>

          <form onSubmit={handleSendMessage} className="flex-shrink-0 border-t bg-background p-4">
            <div className="flex gap-2 max-w-4xl mx-auto">
              <div className="flex-1 relative">
                <Input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="输入你的问题或回复..."
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
        </main>
        
        <SidebarPanel title="快速操作" side="right">
          <div className="space-y-2">
            <Button variant="outline" size="sm" className="w-full justify-start">
              <BookOpen className="h-4 w-4" />
              查看学习资料
            </Button>
            <Button variant="outline" size="sm" className="w-full justify-start">
              <PenTool className="h-4 w-4" />
              开始练习
            </Button>
            <Button variant="outline" size="sm" className="w-full justify-start">
              <BarChart3 className="h-4 w-4" />
              查看进度报告
            </Button>
            <Button variant="outline" size="sm" className="w-full justify-start">
              <Target className="h-4 w-4" />
              调整学习目标
            </Button>
          </div>
          
          <div className="h-px bg-border" />
          
          <div>
            <p className="text-sm text-muted-foreground mb-3">学习提醒</p>
            <Card className="bg-yellow-50/50 dark:bg-yellow-950/20 border-yellow-200">
              <CardContent className="p-4">
                <div className="flex gap-3">
                  <Calendar className="h-4 w-4 text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" />
                  <div className="space-y-1">
                    <p className="text-sm font-medium">下次学习</p>
                    <p className="text-xs text-muted-foreground">
                      明天14:00 - Python函数复习
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </SidebarPanel>
      </div>
    </div>
  )
}