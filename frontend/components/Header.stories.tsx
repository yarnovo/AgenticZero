import type { Meta, StoryObj } from '@storybook/react'
import Header from './Header'

const meta = {
  title: 'Components/Header',
  component: Header,
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof Header>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  name: '默认状态',
  parameters: {
    docs: {
      description: {
        story: '网站的主导航栏，包含品牌logo和主要导航链接。使用sticky定位，具有背景模糊效果。',
      },
    },
  },
}

export const WithBackground: Story = {
  name: '带背景显示',
  decorators: [
    (Story) => (
      <div style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        minHeight: '100vh',
        paddingTop: '0',
      }}>
        <Story />
        <div style={{ 
          padding: '2rem', 
          color: 'white',
          textAlign: 'center',
          marginTop: '2rem'
        }}>
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>页面内容示例</h1>
          <p>这里展示了Header组件在彩色背景下的模糊效果</p>
        </div>
      </div>
    ),
  ],
  parameters: {
    docs: {
      description: {
        story: '演示Header组件的背景模糊效果，在彩色背景上可以看到backdrop-blur-lg的效果。',
      },
    },
  },
}

export const NavigationDemo: Story = {
  name: '导航功能演示',
  decorators: [
    (Story) => (
      <div>
        <Story />
        <div style={{ 
          padding: '2rem',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          <h2 style={{ marginBottom: '1rem' }}>导航功能说明</h2>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '1rem',
            marginBottom: '2rem'
          }}>
            <div style={{ 
              padding: '1rem', 
              border: '1px solid #e5e7eb', 
              borderRadius: '8px',
              backgroundColor: '#f9fafb'
            }}>
              <h3 style={{ margin: '0 0 0.5rem 0', color: '#1f2937' }}>关于我们</h3>
              <p style={{ margin: 0, color: '#6b7280', fontSize: '0.875rem' }}>
                了解公司背景、团队介绍和发展历程
              </p>
            </div>
            <div style={{ 
              padding: '1rem', 
              border: '1px solid #e5e7eb', 
              borderRadius: '8px',
              backgroundColor: '#f9fafb'
            }}>
              <h3 style={{ margin: '0 0 0.5rem 0', color: '#1f2937' }}>我是创作者</h3>
              <p style={{ margin: 0, color: '#6b7280', fontSize: '0.875rem' }}>
                为知识创作者提供AI助教培训平台
              </p>
            </div>
            <div style={{ 
              padding: '1rem', 
              border: '1px solid #e5e7eb', 
              borderRadius: '8px',
              backgroundColor: '#f9fafb'
            }}>
              <h3 style={{ margin: '0 0 0.5rem 0', color: '#1f2937' }}>我是学习者</h3>
              <p style={{ margin: 0, color: '#6b7280', fontSize: '0.875rem' }}>
                为学习者提供AI教练和个性化学习体验
              </p>
            </div>
          </div>
          <div style={{ 
            padding: '1rem', 
            backgroundColor: '#dbeafe', 
            borderRadius: '8px',
            border: '1px solid #93c5fd'
          }}>
            <h4 style={{ margin: '0 0 0.5rem 0', color: '#1e40af' }}>设计特点</h4>
            <ul style={{ margin: 0, paddingLeft: '1.25rem', color: '#1e40af' }}>
              <li>响应式设计，适配各种屏幕尺寸</li>
              <li>sticky定位，在滚动时保持顶部固定</li>
              <li>backdrop-blur-lg实现背景模糊效果</li>
              <li>ghost按钮样式，保持界面简洁</li>
            </ul>
          </div>
        </div>
      </div>
    ),
  ],
  parameters: {
    docs: {
      description: {
        story: '展示Header组件的各个导航功能和设计特点，包括响应式布局和交互效果。',
      },
    },
  },
}