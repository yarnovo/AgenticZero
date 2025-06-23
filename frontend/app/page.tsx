import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { GraduationCap, Users } from 'lucide-react'
import Header from '@/components/Header'

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <div className="container mx-auto px-4 py-16 flex items-center justify-center min-h-screen">
        <div className="max-w-4xl w-full text-center">
          <h1 className="text-6xl md:text-7xl font-bold mb-8 text-foreground">
            师承×学成
          </h1>
          
          <p className="text-3xl md:text-4xl mb-12 text-muted-foreground">
            和AI一起，学有所成
          </p>
          
          <p className="text-xl mb-16 text-muted-foreground max-w-2xl mx-auto">
            创新的B→AI→C教育模式，让知识创作者培养AI助教，让学习者获得个性化指导
          </p>
          
          <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto">
            <Card className="hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border">
              <CardContent className="p-8">
                <div className="mb-6">
                  <div className="w-20 h-20 bg-muted rounded-full flex items-center justify-center mx-auto">
                    <GraduationCap className="w-10 h-10 text-foreground" />
                  </div>
                </div>
                <h2 className="text-2xl font-bold mb-4 text-foreground">我是知识创作者</h2>
                <p className="text-muted-foreground mb-6">
                  培养您的AI助教，让知识传承规模化，服务更多学生
                </p>
                <Link href="/creator">
                  <Button size="lg" className="w-full">
                    进入师承系统
                  </Button>
                </Link>
              </CardContent>
            </Card>
            
            <Card className="hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border">
              <CardContent className="p-8">
                <div className="mb-6">
                  <div className="w-20 h-20 bg-muted rounded-full flex items-center justify-center mx-auto">
                    <Users className="w-10 h-10 text-foreground" />
                  </div>
                </div>
                <h2 className="text-2xl font-bold mb-4 text-foreground">我是知识学习者</h2>
                <p className="text-muted-foreground mb-6">
                  选择AI教练，获得个性化指导，实现学习目标
                </p>
                <Link href="/learner">
                  <Button size="lg" className="w-full">
                    进入学成系统
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
          
          <div className="mt-16 text-sm text-muted-foreground">
            <p>已有 <span className="font-bold text-foreground">1,000+</span> 知识创作者和 <span className="font-bold text-foreground">10,000+</span> 学习者加入我们</p>
          </div>
        </div>
      </div>
    </div>
  )
}