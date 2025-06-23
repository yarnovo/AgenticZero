import type { Meta, StoryObj } from '@storybook/react'
import SidebarPanel from './SidebarPanel'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { BookOpen, PenTool, BarChart3, Target, Calendar, Settings, User, Bell, Shield, HelpCircle } from 'lucide-react'

const meta = {
  title: 'Components/SidebarPanel',
  component: SidebarPanel,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: `
# SidebarPanel 组件文档

## 组件概述
SidebarPanel 是一个可复用的侧边栏容器组件，专门用于在页面左侧或右侧创建统一风格的信息面板。该组件基于项目的设计系统，提供了一致的布局、样式和交互体验。

## 一、功能特性

### 核心特性
- ✅ **可配置标题** - 支持自定义标题文本，也可以不显示标题
- ✅ **左右两侧支持** - 可以放置在页面的左侧或右侧，自动调整边框位置
- ✅ **多种宽度选项** - 提供 sm (256px)、md (320px)、lg (384px) 三种预设宽度
- ✅ **内置滚动** - 集成 ScrollArea 组件，内容过长时自动显示滚动条
- ✅ **统一布局** - 保持一致的内边距和间距设计，符合设计系统规范

### 样式特性
- 统一的背景色和边框样式
- 响应式设计，适配不同屏幕尺寸
- 支持自定义 CSS 类名扩展样式
- 与项目主题系统完美集成

### 布局特性
- Flexbox 布局，内容自动填充
- 标题区域固定，内容区域可滚动
- 合理的内边距和间距设计

## 二、使用说明

### 导入组件
\`\`\`tsx
import SidebarPanel from '@/components/SidebarPanel'
\`\`\`

### 重要提示
⚠️ **布局要求**
- 组件必须放置在 Flexbox 容器中
- 父容器需要有明确的高度设置
- 建议在全屏高度的布局中使用

### 基础使用
\`\`\`tsx
<div className="h-screen flex">
  <SidebarPanel title="侧边栏标题">
    <div>侧边栏内容</div>
  </SidebarPanel>
  <main className="flex-1">
    主内容区域
  </main>
</div>
\`\`\`

### 高级用法
\`\`\`tsx
// 右侧面板，大尺寸，自定义样式
<SidebarPanel 
  title="右侧工具栏"
  side="right"
  width="lg"
  className="bg-accent/5"
>
  <div className="space-y-4">
    <div>工具1</div>
    <div>工具2</div>
  </div>
</SidebarPanel>
\`\`\`

### API 参考

#### Props
| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| title | string | - | 侧边栏标题，可选 |
| children | ReactNode | - | 侧边栏内容 |
| className | string | - | 自定义 CSS 类名 |
| width | 'sm' \| 'md' \| 'lg' | 'md' | 侧边栏宽度 |
| side | 'left' \| 'right' | 'left' | 侧边栏位置 |

#### 宽度规格
| 尺寸 | 实际宽度 | 适用场景 |
|------|----------|----------|
| sm | 256px (w-64) | 简单导航栏 |
| md | 320px (w-80) | 标准信息面板 |
| lg | 384px (w-96) | 复杂内容面板 |

## 三、职责边界

### 核心职责
1. **布局容器管理**
   - 提供标准的侧边栏布局结构
   - 管理标题区域和内容区域的布局
   - 处理不同宽度和位置的样式变化

2. **滚动行为控制**
   - 集成 ScrollArea 组件提供平滑滚动
   - 自动处理内容溢出的滚动显示
   - 保持标题区域固定，内容区域可滚动

3. **样式规范统一**
   - 提供统一的视觉风格和间距
   - 确保与设计系统的一致性
   - 支持主题切换和自定义扩展

### 组件边界

#### 不负责的部分
1. **内容逻辑处理** - 不处理侧边栏内的具体业务逻辑
2. **数据获取** - 不负责内容数据的获取和管理
3. **路由导航** - 不包含路由跳转功能
4. **状态管理** - 不管理全局状态，仅负责布局展示

#### 使用约束
1. **布局约束** - 必须在 Flexbox 容器中使用
2. **高度约束** - 父容器需要有明确的高度设置
3. **内容约束** - 内容需要通过 children 属性传入

### 最佳实践
- 在全屏高度的页面布局中使用
- 标题简洁明了，不超过20个字符
- 内容区域使用合理的间距和分割线
- 与页面主题保持一致的视觉风格
- 考虑不同屏幕尺寸的适配

## 四、使用场景

### 典型应用场景
1. **工作台侧边栏** - 显示工具和操作按钮
2. **学习页面信息面板** - 展示学习进度和相关信息
3. **设置页面导航** - 提供设置选项的分类导航
4. **详情页面辅助信息** - 展示补充信息和快捷操作

### 与其他组件的配合
- 与 Header 组件配合使用形成完整的页面布局
- 与 Card 组件配合展示结构化信息
- 与 Button 组件配合提供操作入口
- 与 ScrollArea 组件深度集成提供滚动功能

## 总结
SidebarPanel 是一个设计精良的侧边栏容器组件，它为项目提供了统一的侧边栏布局解决方案。通过合理的 API 设计和灵活的配置选项，能够满足各种页面布局需求，同时保持良好的用户体验和视觉一致性。
        `
      }
    }
  },
  tags: ['autodocs'],
  argTypes: {
    title: {
      control: 'text',
      description: '侧边栏标题'
    },
    side: {
      control: 'radio',
      options: ['left', 'right'],
      description: '侧边栏位置'
    },
    width: {
      control: 'radio',
      options: ['sm', 'md', 'lg'],
      description: '侧边栏宽度'
    },
    className: {
      control: 'text',
      description: '自定义 CSS 类名'
    }
  }
} satisfies Meta<typeof SidebarPanel>

export default meta
type Story = StoryObj<typeof meta>

// 基础示例
export const Basic: Story = {
  name: '基础示例',
  render: (args) => (
    <div style={{ height: '600px', display: 'flex', backgroundColor: 'var(--background)' }}>
      <SidebarPanel {...args}>
        <div>
          <p className="text-sm text-muted-foreground mb-3">基础内容示例</p>
          <Card>
            <CardHeader>
              <CardTitle>卡片标题</CardTitle>
              <CardDescription>这是一个示例卡片</CardDescription>
            </CardHeader>
            <CardContent>
              <p>卡片内容区域</p>
            </CardContent>
          </Card>
        </div>
        
        <div className="h-px bg-border" />
        
        <div>
          <p className="text-sm text-muted-foreground mb-3">操作按钮</p>
          <div className="space-y-2">
            <Button variant="outline" size="sm" className="w-full justify-start">
              <Settings className="h-4 w-4" />
              设置选项
            </Button>
            <Button variant="outline" size="sm" className="w-full justify-start">
              <User className="h-4 w-4" />
              用户信息
            </Button>
          </div>
        </div>
      </SidebarPanel>
      
      <div className="flex-1 p-6 flex items-center justify-center">
        <p className="text-muted-foreground">主内容区域</p>
      </div>
    </div>
  ),
  args: {
    title: '侧边栏标题',
    side: 'left',
    width: 'md'
  }
}

// 学习信息面板
export const LearningPanel: Story = {
  name: '学习信息面板',
  render: () => (
    <div style={{ height: '600px', display: 'flex', backgroundColor: 'var(--background)' }}>
      <SidebarPanel title="学习信息" side="left">
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
          </div>
        </div>
        
        <div className="h-px bg-border" />
        
        <div>
          <p className="text-sm text-muted-foreground mb-3">学习统计</p>
          <div className="grid grid-cols-2 gap-3">
            <Card className="bg-background">
              <CardContent className="p-3">
                <div className="text-2xl font-bold">12</div>
                <div className="text-xs text-muted-foreground">完成课程</div>
              </CardContent>
            </Card>
            <Card className="bg-background">
              <CardContent className="p-3">
                <div className="text-2xl font-bold">4.8</div>
                <div className="text-xs text-muted-foreground">平均评分</div>
              </CardContent>
            </Card>
          </div>
        </div>
        
        <div className="h-px bg-border" />
        
        <div>
          <p className="text-sm text-muted-foreground mb-3">快速操作</p>
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
        </div>
      </SidebarPanel>
      
      <div className="flex-1 p-6">
        <h2 className="text-2xl font-bold mb-4">主内容区域</h2>
        <p className="text-muted-foreground">这里是页面的主要内容</p>
      </div>
    </div>
  )
}

// 右侧面板
export const RightPanel: Story = {
  name: '右侧面板',
  render: () => (
    <div style={{ height: '600px', display: 'flex', backgroundColor: 'var(--background)' }}>
      <div className="flex-1 p-6">
        <h2 className="text-2xl font-bold mb-4">主内容区域</h2>
        <p className="text-muted-foreground">这里是页面的主要内容</p>
      </div>
      
      <SidebarPanel title="快速操作" side="right">
        <div>
          <p className="text-sm text-muted-foreground mb-3">常用功能</p>
          <div className="space-y-2">
            <Button variant="outline" size="sm" className="w-full justify-start">
              <Bell className="h-4 w-4" />
              通知设置
            </Button>
            <Button variant="outline" size="sm" className="w-full justify-start">
              <Shield className="h-4 w-4" />
              隐私设置
            </Button>
            <Button variant="outline" size="sm" className="w-full justify-start">
              <HelpCircle className="h-4 w-4" />
              帮助中心
            </Button>
          </div>
        </div>
        
        <div className="h-px bg-border" />
        
        <div>
          <p className="text-sm text-muted-foreground mb-3">最近活动</p>
          <div className="space-y-3">
            <Card className="bg-muted/50">
              <CardContent className="p-3">
                <p className="text-sm font-medium">完成了 Python 基础课程</p>
                <p className="text-xs text-muted-foreground mt-1">2 小时前</p>
              </CardContent>
            </Card>
            <Card className="bg-muted/50">
              <CardContent className="p-3">
                <p className="text-sm font-medium">提交了作业</p>
                <p className="text-xs text-muted-foreground mt-1">5 小时前</p>
              </CardContent>
            </Card>
          </div>
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
                    明天14:00 - 数据结构复习
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </SidebarPanel>
    </div>
  )
}

// 无标题面板
export const NoTitle: Story = {
  name: '无标题面板',
  render: () => (
    <div style={{ height: '600px', display: 'flex', backgroundColor: 'var(--background)' }}>
      <SidebarPanel side="left">
        <div>
          <h2 className="text-sm font-semibold mb-4">自定义标题</h2>
          <p className="text-sm text-muted-foreground">
            当不提供 title 属性时，可以在内容中自定义标题样式
          </p>
        </div>
        
        <div className="h-px bg-border" />
        
        <div>
          <h2 className="text-sm font-semibold mb-4">内容区域</h2>
          <div className="space-y-2">
            <Card>
              <CardContent className="p-4">
                <p>这是一个没有默认标题的侧边栏</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </SidebarPanel>
      
      <div className="flex-1 p-6 flex items-center justify-center">
        <p className="text-muted-foreground">主内容区域</p>
      </div>
    </div>
  )
}

// 不同宽度展示
export const DifferentWidths: Story = {
  name: '不同宽度',
  render: () => (
    <div style={{ height: '600px', backgroundColor: 'var(--background)' }}>
      <div className="mb-4 p-4 border-b">
        <h3 className="text-lg font-semibold">小尺寸 (sm - w-64)</h3>
      </div>
      <div style={{ height: '150px', display: 'flex', marginBottom: '2rem' }}>
        <SidebarPanel title="小尺寸" side="left" width="sm">
          <p className="text-sm">这是小尺寸的侧边栏，宽度为 16rem (256px)</p>
        </SidebarPanel>
        <div className="flex-1 p-4 bg-muted/20" />
      </div>
      
      <div className="mb-4 p-4 border-b">
        <h3 className="text-lg font-semibold">中尺寸 (md - w-80)</h3>
      </div>
      <div style={{ height: '150px', display: 'flex', marginBottom: '2rem' }}>
        <SidebarPanel title="中尺寸" side="left" width="md">
          <p className="text-sm">这是中尺寸的侧边栏，宽度为 20rem (320px)</p>
        </SidebarPanel>
        <div className="flex-1 p-4 bg-muted/20" />
      </div>
      
      <div className="mb-4 p-4 border-b">
        <h3 className="text-lg font-semibold">大尺寸 (lg - w-96)</h3>
      </div>
      <div style={{ height: '150px', display: 'flex' }}>
        <SidebarPanel title="大尺寸" side="left" width="lg">
          <p className="text-sm">这是大尺寸的侧边栏，宽度为 24rem (384px)</p>
        </SidebarPanel>
        <div className="flex-1 p-4 bg-muted/20" />
      </div>
    </div>
  )
}

// 长内容滚动
export const ScrollableContent: Story = {
  name: '长内容滚动',
  render: () => (
    <div style={{ height: '600px', display: 'flex', backgroundColor: 'var(--background)' }}>
      <SidebarPanel title="可滚动内容" side="left">
        <div>
          <p className="text-sm text-muted-foreground mb-3">长内容演示</p>
          <p className="text-sm mb-4">当内容超过容器高度时，会自动显示滚动条</p>
        </div>
        
        {Array.from({ length: 20 }, (_, i) => (
          <div key={i}>
            <div className="h-px bg-border" />
            <div className="py-4">
              <h3 className="text-sm font-medium mb-2">章节 {i + 1}</h3>
              <p className="text-sm text-muted-foreground">
                这是第 {i + 1} 个章节的内容。当内容较多时，侧边栏会自动启用滚动功能。
              </p>
            </div>
          </div>
        ))}
      </SidebarPanel>
      
      <div className="flex-1 p-6 flex items-center justify-center">
        <p className="text-muted-foreground">主内容区域</p>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: '演示当内容超过容器高度时的滚动效果'
      }
    }
  }
}

// 双侧边栏布局
export const BothSides: Story = {
  name: '双侧边栏布局',
  render: () => (
    <div style={{ height: '600px', display: 'flex', backgroundColor: 'var(--background)' }}>
      <SidebarPanel title="左侧信息" side="left">
        <div>
          <p className="text-sm text-muted-foreground mb-3">导航菜单</p>
          <div className="space-y-2">
            <Button variant="ghost" size="sm" className="w-full justify-start">
              首页
            </Button>
            <Button variant="ghost" size="sm" className="w-full justify-start">
              课程
            </Button>
            <Button variant="ghost" size="sm" className="w-full justify-start">
              作业
            </Button>
            <Button variant="ghost" size="sm" className="w-full justify-start">
              成绩
            </Button>
          </div>
        </div>
      </SidebarPanel>
      
      <div className="flex-1 p-6">
        <h2 className="text-2xl font-bold mb-4">主内容区域</h2>
        <p className="text-muted-foreground">
          这个布局展示了同时使用左右两个侧边栏的效果
        </p>
      </div>
      
      <SidebarPanel title="右侧工具" side="right">
        <div>
          <p className="text-sm text-muted-foreground mb-3">快捷工具</p>
          <div className="space-y-2">
            <Button variant="outline" size="sm" className="w-full justify-start">
              <Calendar className="h-4 w-4" />
              日历
            </Button>
            <Button variant="outline" size="sm" className="w-full justify-start">
              <Bell className="h-4 w-4" />
              通知
            </Button>
            <Button variant="outline" size="sm" className="w-full justify-start">
              <Settings className="h-4 w-4" />
              设置
            </Button>
          </div>
        </div>
      </SidebarPanel>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: '展示在页面两侧同时使用侧边栏的布局效果'
      }
    }
  }
}