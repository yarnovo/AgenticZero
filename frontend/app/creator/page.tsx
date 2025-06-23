'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { Sparkles, GraduationCap, ChevronRight, Plus, Settings, Trash2 } from 'lucide-react'
import Header from '@/components/Header'

// Mock data for AI assistants
const mockAiAssistants = [
  {
    id: 1,
    name: 'Python 编程导师',
    subject: 'Python编程',
    status: '训练中',
    progress: 75,
    createdAt: '2024-01-15',
    studentsCount: 23
  },
  {
    id: 2,
    name: '数学小助手',
    subject: '高等数学',
    status: '已完成',
    progress: 100,
    createdAt: '2024-01-10',
    studentsCount: 45
  },
  {
    id: 3,
    name: '英语口语教练',
    subject: '英语口语',
    status: '草稿',
    progress: 15,
    createdAt: '2024-01-20',
    studentsCount: 0
  }
]

export default function CreatorPage() {
  const router = useRouter()
  const [showNameDialog, setShowNameDialog] = useState(false)
  const [tempAiName, setTempAiName] = useState('')
  const [aiAssistants, setAiAssistants] = useState(mockAiAssistants)

  const handleStartTraining = () => {
    setShowNameDialog(true)
  }

  const handleConfirmName = () => {
    if (tempAiName.trim()) {
      setShowNameDialog(false)
      // 生成一个基于名称的ID
      const aiId = tempAiName.trim().toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^\w\-一-龥]/g, '')
        + '-' + Date.now()
      // 跳转到工作台页面，使用路径参数
      router.push(`/creator/workbench/${aiId}`)
      setTempAiName('')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case '已完成':
        return 'text-green-600 bg-green-50 border-green-200'
      case '训练中':
        return 'text-blue-600 bg-blue-50 border-blue-200'
      case '草稿':
        return 'text-gray-600 bg-gray-50 border-gray-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const handleDeleteAssistant = (id: number) => {
    setAiAssistants(prev => prev.filter(assistant => assistant.id !== id))
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <Header />
      
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center p-2 bg-primary/10 rounded-full mb-4">
              <Sparkles className="h-6 w-6 text-primary" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
              培养您的 AI 教学助手
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              通过对话训练，将您的专业知识和教学风格传授给 AI，
              创造一个能够 24/7 帮助学生的智能助教
            </p>
          </div>
          

          {/* AI助教管理列表 */}
          {aiAssistants.length > 0 ? (
            <div className="mb-12">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold tracking-tight">我的 AI 助教</h2>
                  <p className="text-muted-foreground">管理您创建的所有 AI 教学助手</p>
                </div>
                <Button onClick={handleStartTraining} size="lg">
                  <Plus className="h-4 w-4" />
                  创建新助教
                </Button>
              </div>
              
              <div className="grid gap-4">
                {aiAssistants.map((assistant) => (
                  <Card key={assistant.id} className="border-muted hover:shadow-md transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                              <GraduationCap className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                              <h3 className="font-semibold text-lg">{assistant.name}</h3>
                              <p className="text-sm text-muted-foreground">{assistant.subject}</p>
                            </div>
                          </div>
                          
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                            <div>
                              <p className="text-xs text-muted-foreground">状态</p>
                              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(assistant.status)}`}>
                                {assistant.status}
                              </span>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">训练进度</p>
                              <div className="flex items-center gap-2">
                                <div className="flex-1 bg-secondary rounded-full h-2">
                                  <div 
                                    className="bg-primary h-2 rounded-full transition-all" 
                                    style={{ width: `${assistant.progress}%` }}
                                  ></div>
                                </div>
                                <span className="text-xs text-muted-foreground">{assistant.progress}%</span>
                              </div>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">学生数量</p>
                              <p className="font-medium">{assistant.studentsCount}</p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">创建时间</p>
                              <p className="font-medium">{assistant.createdAt}</p>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-2 ml-4">
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => {
                              // 生成基于ID的路径
                              const aiId = `ai-${assistant.id}`
                              router.push(`/creator/workbench/${aiId}`)
                            }}
                          >
                            <Settings className="h-4 w-4" />
                            编辑
                          </Button>
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button variant="outline" size="sm">
                                <Trash2 className="h-4 w-4" />
                                删除
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>确认删除</AlertDialogTitle>
                                <AlertDialogDescription>
                                  您确定要删除 "{assistant.name}" 吗？此操作不可撤销，所有相关的训练数据和对话记录将被永久删除。
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>取消</AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() => handleDeleteAssistant(assistant.id)}
                                  className="bg-destructive text-white hover:bg-destructive/90 dark:bg-destructive/60 dark:text-white"
                                >
                                  删除
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ) : (
            // 空状态时显示大的创建卡片
            <Card className="max-w-2xl mx-auto mb-12">
              <CardHeader className="text-center pb-4">
                <CardTitle className="text-2xl">开始创建您的 AI 助教</CardTitle>
                <CardDescription className="text-base">
                  只需几个简单步骤，即可开始培养您的专属 AI 教学助手
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <span className="text-sm font-medium text-primary">1</span>
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">定义教学领域</p>
                      <p className="text-sm text-muted-foreground">选择您擅长的学科或技能领域</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <span className="text-sm font-medium text-primary">2</span>
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">对话训练</p>
                      <p className="text-sm text-muted-foreground">通过自然对话传授知识和教学方法</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <span className="text-sm font-medium text-primary">3</span>
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">测试优化</p>
                      <p className="text-sm text-muted-foreground">验证教学效果并持续改进</p>
                    </div>
                  </div>
                </div>
                <Button 
                  onClick={handleStartTraining}
                  size="lg"
                  className="w-full"
                >
                  <Sparkles className="h-4 w-4" />
                  创建 AI 助教
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      <Dialog open={showNameDialog} onOpenChange={setShowNameDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>为您的 AI 助教命名</DialogTitle>
            <DialogDescription>
              一个好的名字能让学生更容易记住和信任您的 AI 助教
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <label htmlFor="name" className="text-sm font-medium">
                助教名称
              </label>
              <Input
                id="name"
                placeholder="例如：小明老师、Python 导师"
                value={tempAiName}
                onChange={(e) => setTempAiName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && tempAiName.trim()) {
                    handleConfirmName()
                  }
                }}
              />
              <p className="text-xs text-muted-foreground">
                建议使用亲切友好的名字，让学生感到更加亲近
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNameDialog(false)}>
              取消
            </Button>
            <Button onClick={handleConfirmName} disabled={!tempAiName.trim()}>
              <ChevronRight className="h-4 w-4" />
              开始训练
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}