import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import Header from '@/components/Header'

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <section className="pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            师承名师，学有所成
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto">
            用AI技术实现教育民主化，让每个人都能获得最好的教育
          </p>
        </div>
      </section>

      {/* 使命愿景 */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8">
            <Card className="p-8">
              <CardHeader className="p-0 mb-6">
                <CardTitle className="text-2xl">我们的使命</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <p className="text-lg leading-relaxed mb-4">
                  让每一位知识创作者都能通过AI技术实现智慧传承，让更多学习者受益于名师指导，推动教育资源的民主化。
                </p>
                <p className="text-muted-foreground">
                  我们相信，优质教育不应该是少数人的特权，而应该是每个人的基本权利。
                </p>
              </CardContent>
            </Card>
            <Card className="p-8">
              <CardHeader className="p-0 mb-6">
                <CardTitle className="text-2xl">我们的愿景</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <p className="text-lg leading-relaxed mb-4">
                  成为全球领先的AI知识传承平台，让每个知识创作者都能找到他们的"传承者"，每个学习者都能找到最适合的"名师"。
                </p>
                <p className="text-muted-foreground">
                  构建一个知识生生不息、智慧代代相传的学习生态系统。
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* 核心价值 */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-muted">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">核心价值观</h2>
          <div className="grid md:grid-cols-4 gap-6">
            <Card className="text-center p-6">
              <CardContent className="p-0">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">知识即财富</h3>
                <p className="text-sm text-muted-foreground">尊重知识产权，保护创作者价值</p>
              </CardContent>
            </Card>
            <Card className="text-center p-6">
              <CardContent className="p-0">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">教育公平</h3>
                <p className="text-sm text-muted-foreground">让优质教育触手可及</p>
              </CardContent>
            </Card>
            <Card className="text-center p-6">
              <CardContent className="p-0">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">技术赋能</h3>
                <p className="text-sm text-muted-foreground">用AI提升教育效率和质量</p>
              </CardContent>
            </Card>
            <Card className="text-center p-6">
              <CardContent className="p-0">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">以人为本</h3>
                <p className="text-sm text-muted-foreground">关注学习者和教育者需求</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* 产品特色 */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
            革命性的B→AI→C模式
          </h2>
          <p className="text-xl text-muted-foreground text-center mb-16 max-w-3xl mx-auto">
            知识创作者教会AI，AI服务千万学生，实现教育的指数级扩展
          </p>
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="p-6">
              <CardHeader className="p-0 mb-4">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-2xl font-bold text-primary">B</span>
                </div>
                <CardTitle className="text-xl">知识创作者</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <ul className="space-y-2 text-muted-foreground">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>通过自然对话训练AI</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>传授独特教学方法</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>获得70%收益分成</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
            <Card className="p-6">
              <CardHeader className="p-0 mb-4">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-xl font-bold text-primary">AI</span>
                </div>
                <CardTitle className="text-xl">智能教学助手</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <ul className="space-y-2 text-muted-foreground">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>继承老师教学风格</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>7×24小时在线服务</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>个性化学习方案</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
            <Card className="p-6">
              <CardHeader className="p-0 mb-4">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-2xl font-bold text-primary">C</span>
                </div>
                <CardTitle className="text-xl">学习者</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <ul className="space-y-2 text-muted-foreground">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>为学习目标付费</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>获得名师级指导</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>达成目标退押金</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* 核心数据 */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-muted">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            用数据说话
          </h2>
          <div className="grid md:grid-cols-4 gap-8">
            <Card className="text-center p-6">
              <CardContent className="p-0">
                <div className="text-4xl font-bold text-primary mb-2">73%</div>
                <h3 className="text-lg font-semibold mb-2">学习完成率</h3>
                <p className="text-sm text-muted-foreground">行业平均仅10%</p>
              </CardContent>
            </Card>
            <Card className="text-center p-6">
              <CardContent className="p-0">
                <div className="text-4xl font-bold text-primary mb-2">420%</div>
                <h3 className="text-lg font-semibold mb-2">教师收入增长</h3>
                <p className="text-sm text-muted-foreground">平均增长幅度</p>
              </CardContent>
            </Card>
            <Card className="text-center p-6">
              <CardContent className="p-0">
                <div className="text-4xl font-bold text-primary mb-2">92%</div>
                <h3 className="text-lg font-semibold mb-2">用户满意度</h3>
                <p className="text-sm text-muted-foreground">持续提升中</p>
              </CardContent>
            </Card>
            <Card className="text-center p-6">
              <CardContent className="p-0">
                <div className="text-4xl font-bold text-primary mb-2">24/7</div>
                <h3 className="text-lg font-semibold mb-2">全天候服务</h3>
                <p className="text-sm text-muted-foreground">随时随地学习</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* 竞争优势 */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            为什么选择我们
          </h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-2xl font-semibold mb-6">vs. 传统在线教育</h3>
              <ul className="space-y-4">
                <li className="flex items-start">
                  <svg className="w-6 h-6 text-primary mr-3 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <div>
                    <h4 className="font-semibold">卖结果，不卖课程</h4>
                    <p className="text-muted-foreground">学生为目标付费，达成即退还押金</p>
                  </div>
                </li>
                <li className="flex items-start">
                  <svg className="w-6 h-6 text-primary mr-3 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <div>
                    <h4 className="font-semibold">双向互动，不是单向灌输</h4>
                    <p className="text-muted-foreground">AI实时响应，个性化教学</p>
                  </div>
                </li>
                <li className="flex items-start">
                  <svg className="w-6 h-6 text-primary mr-3 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <div>
                    <h4 className="font-semibold">无限扩展，不受时间限制</h4>
                    <p className="text-muted-foreground">一个AI可服务千万学生</p>
                  </div>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-2xl font-semibold mb-6">vs. 通用AI工具</h3>
              <ul className="space-y-4">
                <li className="flex items-start">
                  <svg className="w-6 h-6 text-primary mr-3 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <div>
                    <h4 className="font-semibold">专业深度 vs 泛泛而谈</h4>
                    <p className="text-muted-foreground">垂直领域专家知识</p>
                  </div>
                </li>
                <li className="flex items-start">
                  <svg className="w-6 h-6 text-primary mr-3 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <div>
                    <h4 className="font-semibold">有温度的传承</h4>
                    <p className="text-muted-foreground">继承老师的教学风格和个性</p>
                  </div>
                </li>
                <li className="flex items-start">
                  <svg className="w-6 h-6 text-primary mr-3 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <div>
                    <h4 className="font-semibold">目标导向学习</h4>
                    <p className="text-muted-foreground">不是问答工具，是学习伙伴</p>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* 行动号召 */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-muted">
        <div className="max-w-6xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            开启您的AI教育之旅
          </h2>
          <p className="text-xl text-muted-foreground mb-12 max-w-2xl mx-auto">
            无论您是知识创作者还是学习者，AI Teacher Clone都能为您创造价值
          </p>
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <Card className="p-8">
              <CardHeader className="p-0 mb-6">
                <CardTitle className="text-2xl">成为AI教师</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <ul className="space-y-3 mb-6 text-left">
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>突破时间和空间限制</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>实现被动收入增长</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>帮助更多学生成功</span>
                  </li>
                </ul>
                <Button className="w-full" size="lg">
                  立即申请入驻
                </Button>
              </CardContent>
            </Card>
            <Card className="p-8">
              <CardHeader className="p-0 mb-6">
                <CardTitle className="text-2xl">开始学习</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <ul className="space-y-3 mb-6 text-left">
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>获得名师级个性化指导</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>7×24小时随时学习</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>达成目标退还押金</span>
                  </li>
                </ul>
                <Button className="w-full" size="lg" variant="outline">
                  免费体验
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* 联系方式 */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
            联系我们
          </h2>
          <p className="text-xl text-muted-foreground text-center mb-16">
            期待与您共创教育的美好未来
          </p>
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="text-center p-6">
              <CardContent className="p-0">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold mb-2">商务合作</h3>
                <p className="text-muted-foreground">business@aiteacherclone.com</p>
              </CardContent>
            </Card>
            <Card className="text-center p-6">
              <CardContent className="p-0">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold mb-2">教师入驻</h3>
                <p className="text-muted-foreground">teacher@aiteacherclone.com</p>
              </CardContent>
            </Card>
            <Card className="text-center p-6">
              <CardContent className="p-0">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold mb-2">客户支持</h3>
                <p className="text-muted-foreground">support@aiteacherclone.com</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
    </div>
  )
}