'use client'

import React from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Star, Users, Award, Info } from 'lucide-react'
import Header from '@/components/Header'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

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

const aiTeachers: AITeacher[] = [
  {
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
  {
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
  {
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
]

export default function LearnerPage() {
  const router = useRouter()

  const handleSelectTeacher = (teacherId: string) => {
    router.push(`/learner/${teacherId}`)
  }

  return (
    <div className="h-screen bg-background flex flex-col">
      <Header />
      
      <main className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-shrink-0 container mx-auto px-4 pt-16 pb-8">
          <div className="max-w-6xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-6 text-foreground">
              学成 - AI教练市场
            </h1>
            <p className="text-2xl text-muted-foreground">
              不是随便聊天的AI助手，而是能兑现学习承诺的AI教练
            </p>
          </div>
        </div>
        
        <div className="flex-1 overflow-auto pb-16">
          <div className="container mx-auto px-4">
            <div className="max-w-6xl mx-auto">
              <div className="grid md:grid-cols-3 gap-6">
                {aiTeachers.map((teacher) => (
                  <Card key={teacher.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader className="text-center relative">
                      {teacher.mentor && (
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="absolute top-2 right-2 h-8 w-8"
                              onClick={(e) => e.stopPropagation()}
                            >
                              <Info className="h-4 w-4" />
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-80" align="end">
                            <div className="space-y-4">
                              <div>
                                <h4 className="font-semibold text-sm mb-1">师承信息</h4>
                                <div className="space-y-3">
                                  <div>
                                    <p className="font-medium">{teacher.mentor.name}</p>
                                    <p className="text-sm text-muted-foreground">{teacher.mentor.title}</p>
                                  </div>
                                  <p className="text-sm">{teacher.mentor.experience}</p>
                                  <div>
                                    <p className="text-sm font-medium mb-2 flex items-center">
                                      <Award className="h-3 w-3 mr-1" />
                                      主要成就
                                    </p>
                                    <ul className="space-y-1">
                                      {teacher.mentor.achievements.map((achievement, index) => (
                                        <li key={index} className="text-sm text-muted-foreground flex items-start">
                                          <span className="mr-2">•</span>
                                          <span>{achievement}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </PopoverContent>
                        </Popover>
                      )}
                      <div className="text-6xl mb-2">{teacher.avatar}</div>
                      <CardTitle>{teacher.name}</CardTitle>
                      <CardDescription>{teacher.subject}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-muted-foreground mb-4">{teacher.description}</p>
                      <div className="flex justify-between items-center mb-4">
                        <div className="flex items-center">
                          <Star className="h-4 w-4 text-foreground mr-1" />
                          <span className="text-sm">{teacher.rating}</span>
                        </div>
                        <div className="flex items-center text-sm text-muted-foreground">
                          <Users className="h-4 w-4 mr-1" />
                          {teacher.students} 学生
                        </div>
                      </div>
                      <div className="text-center mb-4">
                        <span className="text-2xl font-bold text-foreground">¥{teacher.price}</span>
                        <span className="text-muted-foreground">/月</span>
                      </div>
                      <Button 
                        className="w-full" 
                        onClick={() => handleSelectTeacher(teacher.id)}
                      >
                        选择此教练
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}