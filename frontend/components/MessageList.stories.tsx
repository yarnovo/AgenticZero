import type { Meta, StoryObj } from '@storybook/react'
import { 
  MessageList,
  useMessageList,
  type Message 
} from './MessageList'
import * as React from 'react'

// 简化的随机消息生成函数
function createRandomMessages(count: number): Message[] {
  return Array.from({ length: count }, (_, i) => ({
    key: `msg-${i}`,
    text: `这是第 ${i + 1} 条测试消息，内容随机生成用于演示。`,
    user: Math.random() > 0.5 ? 'me' : 'other',
    timestamp: new Date(),
    delivered: true,
    avatar: `https://i.pravatar.cc/30?u=${i}`
  }))
}

const meta = {
  title: 'Components/MessageList',
  component: MessageList,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: `
# MessageList 组件文档

## 组件概述
MessageList 是一个基于 @virtuoso.dev/message-list 封装的高性能虚拟化消息列表组件，专门用于处理大量消息的高效渲染和交互。

## 一、功能特性

### 核心特性
- ✅ **高性能虚拟化渲染** - 支持渲染数千条消息而不影响性能
- ✅ **自定义消息渲染** - 支持完全自定义的 ItemContent 组件
- ✅ **自动滚动控制** - 智能滚动到最新消息，支持平滑和即时滚动
- ✅ **完整的 TypeScript 支持** - 提供完善的类型定义
- ✅ **响应式布局** - 自动适应父容器尺寸变化
- ✅ **灵活的外部控制** - 通过 ref 和 Hook 提供完整的 API 控制

### 数据功能
- 支持消息的增加、删除、更新操作
- 消息状态管理（已发送、发送中、已读等）
- 批量消息操作支持
- 消息元数据扩展（时间戳、头像、点赞状态等）

### 性能特性
- 虚拟滚动技术，只渲染可视区域
- 自动内存回收，保持稳定的内存占用
- 批量更新优化，减少重渲染
- 支持大数据集（1000+ 消息）流畅渲染

## 二、使用说明

### 导入组件
\`\`\`tsx
import { MessageList, useMessageList } from '@/components/MessageList'
\`\`\`

### 重要提示：父容器要求
⚠️ **组件必须放置在 Flexbox 容器中才能正常工作**

组件内部使用 \`flex: 1\` 来自适应父容器高度，因此父容器必须满足以下条件：
1. 设置 \`display: flex\` 和 \`flex-direction: column\`
2. 具有明确的高度约束（如 \`height: 600px\` 或 \`height: 100vh\`）
3. 如果父容器也使用 flex: 1，需要添加 \`min-height: 0\`

#### 🔴 关键注意事项：高度约束
**在弹性盒子布局链中，必须有一个祖先元素具有固定高度**

如果 MessageList 的所有祖先元素都使用弹性盒子布局（flex），那么必须确保：
- 最外层容器有固定高度（如 \`height: 100vh\` 或 \`height: 600px\`）
- 中间的 flex 容器使用 \`flex: 1\` 和 \`min-height: 0\`
- 避免所有祖先都是 \`flex: 1\` 而没有固定高度的情况

**错误示例：**
\`\`\`tsx
// ❌ 错误：没有固定高度的祖先
<div className="flex flex-col flex-1">
  <div className="flex-1 flex flex-col">
    <MessageList /> {/* 高度会异常 */}
  </div>
</div>
\`\`\`

**正确示例：**
\`\`\`tsx
// ✅ 正确：最外层有固定高度
<div className="h-screen flex flex-col">
  <div className="flex-1 flex flex-col min-h-0">
    <MessageList /> {/* 正常工作 */}
  </div>
</div>
\`\`\`

### 基础使用
\`\`\`tsx
import { MessageList, useMessageList } from '@/components/MessageList'

function ChatComponent() {
  const { ref, sendMessage, receiveMessage } = useMessageList()
  
  return (
    {/* 父容器必须是 Flexbox 布局 */}
    <div style={{ 
      display: 'flex',
      flexDirection: 'column',
      height: '600px' 
    }}>
      <MessageList
        ref={ref}
        licenseKey="your-license-key"
        initialMessages={[]}
      />
      
      <button onClick={() => sendMessage('Hello!')}>
        发送消息
      </button>
    </div>
  )
}
\`\`\`

### 高级用法

#### 1. 自定义消息数据
\`\`\`tsx
const customMessages: Message[] = [
  {
    key: 'msg-1',
    text: '欢迎使用 MessageList！',
    user: 'other',
    timestamp: new Date(),
    avatar: 'https://example.com/avatar.jpg',
    delivered: true,
    liked: false
  }
]

<MessageListWrapper
  initialMessages={customMessages}
/>
\`\`\`

#### 2. 使用事件回调
\`\`\`tsx
<MessageListWrapper
  onSendMessage={(text) => {
    console.log('发送消息:', text)
    // 调用 API 发送消息
  }}
  onReceiveMessage={() => {
    console.log('接收到新消息')
  }}
  onUpdateMessage={(messageKey, updates) => {
    console.log('更新消息:', messageKey, updates)
  }}
/>
\`\`\`

#### 3. 外部控制消息列表
\`\`\`tsx
function ControlledChat() {
  const messageListRef = useRef<MessageListMethods<Message>>()
  
  // 添加消息
  const addMessage = () => {
    messageListRef.current?.data.append([{
      key: \`msg-\${Date.now()}\`,
      text: '新消息',
      user: 'me',
      timestamp: new Date()
    }])
  }
  
  // 更新消息
  const updateMessage = (key: string) => {
    messageListRef.current?.data.map(
      msg => msg.key === key ? { ...msg, liked: true } : msg
    )
  }
  
  // 滚动到底部
  const scrollToBottom = () => {
    messageListRef.current?.scrollToItem({
      index: 'LAST',
      align: 'end',
      behavior: 'smooth'
    })
  }
  
  return (
    <MessageListWrapper ref={messageListRef} />
  )
}
\`\`\`

#### 4. 自定义消息渲染
\`\`\`tsx
const CustomItemContent: MessageListProps<Message, null>['ItemContent'] = ({ data }) => {
  return (
    <div className="custom-message">
      <div className="message-header">
        <img src={data.avatar} alt="avatar" />
        <span>{data.user}</span>
      </div>
      <div className="message-body">{data.text}</div>
      <div className="message-actions">
        <button onClick={() => handleLike(data.key)}>Like</button>
      </div>
    </div>
  )
}

<MessageListWrapper
  initialMessages={messages}
  ItemContent={CustomItemContent}
/>
\`\`\`

#### 5. 在复杂布局中使用
\`\`\`tsx
<div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
  <header style={{ flexShrink: 0 }}>聊天标题</header>
  
  {/* 组件会自动 flex: 1 填充剩余空间 */}
  <MessageListWrapper
    initialMessages={messages}
  />
  
  <footer style={{ flexShrink: 0 }}>输入区域</footer>
</div>
\`\`\`

### API 参考

#### Props
| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| licenseKey | string | '' | Virtuoso 许可证密钥 |
| initialMessages | Message[] | [] | 初始消息数据 |
| style | React.CSSProperties | {} | 自定义样式 |
| ItemContent | MessageListProps['ItemContent'] | DefaultItemContent | 自定义消息渲染组件 |
| onSendMessage | (text: string) => void | - | 发送消息回调 |
| onReceiveMessage | () => void | - | 接收消息回调 |
| onUpdateMessage | (key: string, updates: Partial<Message>) => void | - | 更新消息回调 |

#### Ref Methods
- \`sendMessage(text: string)\` - 发送消息
- \`receiveMessage(text: string)\` - 接收消息
- \`updateMessage(key: string, updates: Partial<Message>)\` - 更新消息
- 继承所有 MessageListMethods 的方法

## 三、职责边界

### 核心职责
1. **渲染层职责**
   - 虚拟化渲染技术实现
   - 样式变体管理和切换
   - 响应式布局适配

2. **数据管理职责**
   - 消息数据结构定义
   - 消息状态管理
   - 数据流控制和更新

3. **交互控制职责**
   - 滚动行为控制
   - 外部控制接口
   - 事件回调机制

4. **性能优化职责**
   - 按需渲染实现
   - 内存管理优化
   - 批量更新处理

### 组件边界

#### 不负责的部分
1. **消息持久化** - 不处理消息的存储，由外部状态管理负责
2. **网络通信** - 不包含网络请求，消息收发由外部处理
3. **用户认证** - 不处理身份验证和权限控制
4. **输入控件** - 不提供输入框，专注于列表展示

#### 使用约束
1. **许可证要求** - 商业使用需要 Virtuoso 许可证
2. **容器要求** - 父容器必须是 Flexbox 布局，并有明确的高度约束
3. **数据要求** - 每条消息必须有唯一 key
4. **布局要求** - 组件使用 flex: 1 自适应高度，父容器需配合设置

### 最佳实践
- 配合状态管理库（Redux/Zustand）使用
- 与实时通信库（WebSocket/Socket.IO）集成
- 初始数据量控制在 100 条以内
- 使用批量操作减少渲染次数
- 保持样式一致性避免重排

## 总结
MessageList 提供了一个功能完整、性能优异、易于集成的消息列表解决方案。通过清晰的职责划分和灵活的 API 设计，能够满足各种消息展示场景的需求。
        `
      }
    }
  },
  tags: ['autodocs'],
  argTypes: {
    licenseKey: {
      control: { type: 'text' },
      description: 'Virtuoso 许可证密钥'
    },
    ItemContent: {
      control: false,
      description: '自定义消息渲染组件'
    }
  }
} satisfies Meta<typeof MessageList>

export default meta
type Story = StoryObj<typeof meta>

// 基础消息列表
export const Basic: Story = {
  name: '基础消息列表',
  render: (args) => {
    const { ref, sendMessage, receiveMessage } = useMessageList()
    
    return (
      <div style={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
        <MessageList
          ref={ref}
          {...args}
        />
        
        <div style={{ 
          padding: '1rem', 
          borderTop: '1px solid var(--border)', 
          display: 'flex', 
          gap: '1rem',
          backgroundColor: 'var(--background)'
        }}>
          <button 
            onClick={() => sendMessage?.('这是一条测试消息')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--primary)',
              color: 'var(--primary-foreground)',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            发送消息
          </button>
          <button 
            onClick={() => receiveMessage?.('这是一条接收到的测试消息')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--secondary)',
              color: 'var(--secondary-foreground)',
              border: '1px solid var(--border)',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            接收消息
          </button>
        </div>
      </div>
    )
  },
  args: {
    initialMessages: createRandomMessages(20),
    licenseKey: ''
  },
  parameters: {
    docs: {
      description: {
        story: '基础的消息列表，简洁的气泡样式。包含演示用的外部控制按钮。'
      }
    }
  }
}

// 自定义消息渲染组件示例 - 聊天风格
const CustomItemContent = ({ data }: { data: Message }) => {
  const ownMessage = data.user === 'me'
  return (
    <div style={{ paddingBottom: '1rem', display: 'flex', flexDirection: ownMessage ? 'row-reverse' : 'row', gap: '1rem' }}>
      <img 
        src={data.avatar || `https://i.pravatar.cc/40?u=${data.user}`}
        style={{ borderRadius: '100%', width: 40, height: 40 }}
        alt="avatar"
      />
      <div style={{ 
        maxWidth: '70%',
        backgroundColor: ownMessage ? '#007bff' : '#f1f3f5',
        color: ownMessage ? 'white' : 'black',
        borderRadius: '1rem',
        padding: '0.75rem 1rem',
        boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
      }}>
        <div>{data.text}</div>
        <div style={{ fontSize: '0.75rem', opacity: 0.7, marginTop: '0.25rem' }}>
          {data.timestamp?.toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}

// 自定义消息渲染组件示例 - 极简风格
const MinimalItemContent = ({ data }: { data: Message }) => {
  const ownMessage = data.user === 'me'
  return (
    <div style={{ 
      padding: '0.5rem 1rem',
      textAlign: ownMessage ? 'right' : 'left'
    }}>
      <div style={{
        display: 'inline-block',
        padding: '0.5rem 1rem',
        backgroundColor: ownMessage ? '#e3f2fd' : '#f5f5f5',
        borderRadius: '0.5rem',
        maxWidth: '80%'
      }}>
        <div style={{ fontSize: '0.9rem' }}>{data.text}</div>
        <div style={{ fontSize: '0.7rem', opacity: 0.6, marginTop: '0.25rem' }}>
          {data.user === 'me' ? '我' : '对方'} · {data.timestamp?.toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}

// 自定义消息渲染组件示例 - 卡片风格
const CardItemContent = ({ data }: { data: Message }) => {
  const ownMessage = data.user === 'me'
  return (
    <div style={{ 
      padding: '0.5rem',
      display: 'flex',
      justifyContent: ownMessage ? 'flex-end' : 'flex-start'
    }}>
      <div style={{
        backgroundColor: 'white',
        border: '1px solid #e0e0e0',
        borderRadius: '0.5rem',
        padding: '1rem',
        maxWidth: '75%',
        boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
      }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.5rem',
          marginBottom: '0.5rem'
        }}>
          <div style={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            backgroundColor: ownMessage ? '#4caf50' : '#ff9800'
          }} />
          <span style={{ 
            fontSize: '0.8rem', 
            fontWeight: 'bold',
            color: '#666'
          }}>
            {ownMessage ? '你' : '助手'}
          </span>
          <span style={{ fontSize: '0.75rem', color: '#999' }}>
            {data.timestamp?.toLocaleTimeString()}
          </span>
        </div>
        <div style={{ color: '#333' }}>{data.text}</div>
        {data.delivered === false && (
          <div style={{ fontSize: '0.7rem', color: '#999', marginTop: '0.5rem' }}>
            发送中...
          </div>
        )}
      </div>
    </div>
  )
}

export const CustomRendering: Story = {
  name: '自定义消息渲染',
  render: () => {
    const { ref, sendMessage, receiveMessage } = useMessageList()
    
    return (
      <div style={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
        <MessageList
          ref={ref}
          initialMessages={createRandomMessages(10)}
          ItemContent={CustomItemContent}
          licenseKey=""
        />
        
        <div style={{ 
          padding: '1rem', 
          borderTop: '1px solid var(--border)', 
          display: 'flex', 
          gap: '1rem',
          backgroundColor: 'var(--background)'
        }}>
          <button 
            onClick={() => sendMessage?.('这是自定义样式的消息！')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--primary)',
              color: 'var(--primary-foreground)',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            发送消息
          </button>
          <button 
            onClick={() => receiveMessage?.('这是自定义样式的接收消息！')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--secondary)',
              color: 'var(--secondary-foreground)',
              border: '1px solid var(--border)',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            接收消息
          </button>
        </div>
      </div>
    )
  },
  parameters: {
    docs: {
      description: {
        story: '使用自定义的 ItemContent 组件来完全控制消息的渲染方式。展示了带头像的聊天界面样式。'
      }
    }
  }
}

// 展示多种自定义渲染风格
export const CustomRenderingStyles: Story = {
  name: '多种渲染风格',
  render: () => {
    const [currentStyle, setCurrentStyle] = React.useState<'chat' | 'minimal' | 'card'>('chat')
    const { ref, sendMessage, receiveMessage } = useMessageList()
    
    const getItemContent = () => {
      switch (currentStyle) {
        case 'minimal':
          return MinimalItemContent
        case 'card':
          return CardItemContent
        default:
          return CustomItemContent
      }
    }
    
    return (
      <div style={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ 
          padding: '1rem', 
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          gap: '1rem',
          alignItems: 'center'
        }}>
          <span>选择样式：</span>
          <button 
            onClick={() => setCurrentStyle('chat')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: currentStyle === 'chat' ? 'var(--primary)' : 'var(--secondary)',
              color: currentStyle === 'chat' ? 'var(--primary-foreground)' : 'var(--secondary-foreground)',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            聊天风格
          </button>
          <button 
            onClick={() => setCurrentStyle('minimal')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: currentStyle === 'minimal' ? 'var(--primary)' : 'var(--secondary)',
              color: currentStyle === 'minimal' ? 'var(--primary-foreground)' : 'var(--secondary-foreground)',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            极简风格
          </button>
          <button 
            onClick={() => setCurrentStyle('card')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: currentStyle === 'card' ? 'var(--primary)' : 'var(--secondary)',
              color: currentStyle === 'card' ? 'var(--primary-foreground)' : 'var(--secondary-foreground)',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            卡片风格
          </button>
        </div>
        
        <MessageList
          ref={ref}
          initialMessages={createRandomMessages(8)}
          ItemContent={getItemContent()}
          licenseKey=""
        />
        
        <div style={{ 
          padding: '1rem', 
          borderTop: '1px solid var(--border)', 
          display: 'flex', 
          gap: '1rem',
          backgroundColor: 'var(--background)'
        }}>
          <button 
            onClick={() => sendMessage?.('测试不同风格的消息渲染')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--primary)',
              color: 'var(--primary-foreground)',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            发送消息
          </button>
          <button 
            onClick={() => receiveMessage?.('这是对方发送的消息示例')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--secondary)',
              color: 'var(--secondary-foreground)',
              border: '1px solid var(--border)',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            接收消息
          </button>
        </div>
      </div>
    )
  },
  parameters: {
    docs: {
      description: {
        story: '展示三种不同的自定义消息渲染风格：聊天风格、极简风格和卡片风格。可以动态切换查看效果。'
      }
    }
  }
}



// 自定义控制演示
export const CustomControls: Story = {
  name: '自定义控制面板',
  render: (args) => {
    const { ref, sendMessage, receiveMessage, updateMessage } = useMessageList()
    const [inputText, setInputText] = React.useState('')
    const [lastSentMessageKey, setLastSentMessageKey] = React.useState<string | null>(null)
    const [messages, setMessages] = React.useState<Message[]>(createRandomMessages(10))
    
    const handleSend = () => {
      if (inputText.trim()) {
        const messageKey = `msg-${Date.now()}`
        const newMessage: Message = {
          key: messageKey,
          text: inputText.trim(),
          user: 'me',
          timestamp: new Date(),
          delivered: true,
          liked: false
        }
        
        // 添加消息到列表，并自动滚动
        ref.current?.data.append([newMessage], ({ scrollInProgress, atBottom }) => {
          if (atBottom || scrollInProgress) {
            return 'smooth'
          } else {
            return 'auto'
          }
        })
        setMessages(prev => [...prev, newMessage])
        setLastSentMessageKey(messageKey)
        setInputText('')
      }
    }
    
    const handleReceive = () => {
      const newMessage: Message = {
        key: `msg-${Date.now()}`,
        text: '这是一条模拟接收的消息，展示了接收消息的功能！',
        user: 'other',
        timestamp: new Date(),
        delivered: true
      }
      ref.current?.data.append([newMessage], ({ scrollInProgress, atBottom }) => {
        if (atBottom || scrollInProgress) {
          return 'smooth'
        } else {
          return false
        }
      })
      setMessages(prev => [...prev, newMessage])
    }
    
    const handleLikeLastMessage = () => {
      if (lastSentMessageKey) {
        // 获取当前消息的点赞状态
        const currentMessage = messages.find(msg => msg.key === lastSentMessageKey)
        const isLiked = currentMessage?.liked || false
        
        // 切换点赞状态
        updateMessage?.(lastSentMessageKey, { liked: !isLiked })
        setMessages(prev => prev.map(msg => 
          msg.key === lastSentMessageKey ? { ...msg, liked: !isLiked } : msg
        ))
      }
    }
    
    // 自定义消息渲染组件，支持点赞显示
    const CustomItemContentWithLike = ({ data }: { data: Message }) => {
      const ownMessage = data.user === 'me'
      return (
        <div style={{ paddingBottom: '1rem', display: 'flex', flexDirection: ownMessage ? 'row-reverse' : 'row', gap: '0.5rem' }}>
          <div
            style={{
              maxWidth: '70%',
              backgroundColor: ownMessage ? '#007bff' : '#f1f3f5',
              color: ownMessage ? 'white' : 'black',
              borderRadius: '1rem',
              padding: '0.75rem 1rem',
              boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
              position: 'relative'
            }}
          >
            <div>{data.text}</div>
            {data.timestamp && (
              <div style={{ fontSize: '0.75rem', opacity: 0.7, marginTop: '0.25rem' }}>
                {data.timestamp.toLocaleTimeString()}
              </div>
            )}
            {data.liked && (
              <div style={{
                position: 'absolute',
                bottom: '-10px',
                right: ownMessage ? undefined : '-10px',
                left: ownMessage ? '-10px' : undefined,
                backgroundColor: '#ff4458',
                borderRadius: '50%',
                width: '24px',
                height: '24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '12px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
              }}>
                ❤️
              </div>
            )}
          </div>
        </div>
      )
    }
    
    return (
      <div style={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
        <MessageList
          ref={ref}
          initialMessages={messages}
          ItemContent={CustomItemContentWithLike}
          licenseKey=""
        />
        
        {/* 自定义控制面板 */}
        <div style={{ 
          padding: '1rem', 
          borderTop: '1px solid var(--border)', 
          display: 'flex', 
          gap: '1rem', 
          alignItems: 'center',
          backgroundColor: 'var(--background)'
        }}>
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="输入消息..."
            style={{
              flex: 1,
              padding: '0.5rem',
              border: '1px solid var(--border)',
              borderRadius: '0.25rem',
              backgroundColor: 'var(--background)',
              color: 'var(--foreground)'
            }}
          />
          <button 
            onClick={handleSend}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--primary)',
              color: 'var(--primary-foreground)',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            发送
          </button>
          <button 
            onClick={handleReceive}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--secondary)',
              color: 'var(--secondary-foreground)',
              border: '1px solid var(--border)',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            模拟接收
          </button>
          <button 
            onClick={handleLikeLastMessage}
            disabled={!lastSentMessageKey}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: lastSentMessageKey ? '#ff4458' : 'var(--muted)',
              color: 'white',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: lastSentMessageKey ? 'pointer' : 'not-allowed',
              opacity: lastSentMessageKey ? 1 : 0.5
            }}
          >
            ❤️ {messages.find(msg => msg.key === lastSentMessageKey)?.liked ? '取消点赞' : '给最后一条发送的消息点赞'}
          </button>
        </div>
      </div>
    )
  },
  parameters: {
    docs: {
      description: {
        story: '外部自定义控制面板演示，展示如何在组件外部使用API控制消息列表。组件本身不包含任何控制按钮，完全由外部控制。'
      }
    }
  }
}

// 空状态
export const EmptyState: Story = {
  name: '空状态',
  render: (args) => {
    const { ref, sendMessage, receiveMessage } = useMessageList()
    
    return (
      <div style={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
        <MessageList
          ref={ref}
          {...args}
        />
        
        <div style={{ 
          padding: '1rem', 
          borderTop: '1px solid var(--border)', 
          display: 'flex', 
          gap: '1rem',
          backgroundColor: 'var(--background)'
        }}>
          <button 
            onClick={() => sendMessage?.('第一条消息！')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--primary)',
              color: 'var(--primary-foreground)',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            发送第一条消息
          </button>
          <button 
            onClick={() => receiveMessage?.('欢迎使用消息列表！')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--secondary)',
              color: 'var(--secondary-foreground)',
              border: '1px solid var(--border)',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            接收欢迎消息
          </button>
        </div>
      </div>
    )
  },
  args: {
    initialMessages: [],
    licenseKey: ''
  },
  parameters: {
    docs: {
      description: {
        story: '空状态的消息列表'
      }
    }
  }
}

// 性能测试（大量消息）
export const Performance: Story = {
  name: '性能测试',
  render: (args) => {
    const { ref, sendMessage, receiveMessage } = useMessageList()
    
    return (
      <div style={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
        <MessageList
          ref={ref}
          {...args}
        />
        
        <div style={{ 
          padding: '1rem', 
          borderTop: '1px solid var(--border)', 
          display: 'flex', 
          gap: '1rem',
          alignItems: 'center',
          backgroundColor: 'var(--background)'
        }}>
          <span style={{ fontSize: '0.875rem', color: 'var(--muted-foreground)' }}>
            显示 1000 条消息的虚拟化列表
          </span>
          <button 
            onClick={() => sendMessage?.('新消息')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--primary)',
              color: 'var(--primary-foreground)',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            添加消息
          </button>
          <button 
            onClick={() => {
              // 滚动到底部
              ref.current?.scrollToItem({
                index: 'LAST',
                align: 'end',
                behavior: 'smooth'
              })
            }}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--secondary)',
              color: 'var(--secondary-foreground)',
              border: '1px solid var(--border)',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            滚动到底部
          </button>
        </div>
      </div>
    )
  },
  args: {
    initialMessages: createRandomMessages(1000),
    licenseKey: ''
  },
  parameters: {
    docs: {
      description: {
        story: '性能测试 - 1000条消息的虚拟化列表'
      }
    }
  }
}


// API 使用演示
export const APIDemo: Story = {
  name: 'API使用演示',
  render: () => {
    const { ref, sendMessage, receiveMessage, updateMessage } = useMessageList()
    const [messageCount, setMessageCount] = React.useState(5)
    
    React.useEffect(() => {
      // 初始化一些消息
      for (let i = 0; i < messageCount; i++) {
        receiveMessage?.(`初始化消息 ${i + 1}`)
      }
    }, [])
    
    const handleBatchSend = () => {
      for (let i = 0; i < 3; i++) {
        setTimeout(() => {
          sendMessage?.(`批量消息 ${i + 1}`)
        }, i * 500)
      }
    }
    
    const handleAnimatedReceive = () => {
      const fullText = '这是一条模拟打字效果的长消息，展示了消息实时更新的功能！'
      
      // 使用 receiveMessage 添加初始消息，它会返回消息的 key
      const messageKey = receiveMessage?.('正在输入...')
      
      if (!messageKey) return
      
      // 模拟打字效果
      setTimeout(() => {
        let text = ''
        
        const typeInterval = setInterval(() => {
          if (text.length >= fullText.length) {
            clearInterval(typeInterval)
            return
          }
          
          text = fullText.slice(0, text.length + 1)
          updateMessage?.(messageKey, { text })
        }, 50)
      }, 500)
    }
    
    return (
      <div style={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
        <MessageList
          ref={ref}
          initialMessages={[]}
          licenseKey=""
        />
        
        <div style={{ 
          padding: '1rem', 
          borderTop: '1px solid var(--border)', 
          display: 'flex', 
          flexWrap: 'wrap',
          gap: '1rem',
          backgroundColor: 'var(--background)'
        }}>
          <button onClick={() => sendMessage?.('Hello World!')}>发送简单消息</button>
          <button onClick={() => receiveMessage?.('这是一条随机接收的消息')}>接收随机消息</button>
          <button onClick={handleBatchSend}>批量发送</button>
          <button onClick={handleAnimatedReceive}>打字效果</button>
        </div>
      </div>
    )
  },
  parameters: {
    docs: {
      description: {
        story: 'API 使用演示，展示各种消息操作功能'
      }
    }
  }
}

// Flexbox 容器演示
export const FlexboxContainer: Story = {
  name: 'Flexbox容器演示',
  render: () => {
    const { ref, sendMessage, receiveMessage } = useMessageList()
    
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        height: '600px',
        backgroundColor: 'var(--background)',
        border: '2px solid var(--border)',
        borderRadius: '8px'
      }}>
        <div style={{ 
          padding: '1rem', 
          backgroundColor: 'var(--muted)',
          borderBottom: '1px solid var(--border)',
          flexShrink: 0
        }}>
          <h3 style={{ margin: 0, marginBottom: '0.5rem' }}>Flexbox 容器演示</h3>
          <p style={{ margin: 0, fontSize: '0.9em', opacity: 0.8 }}>组件自动填充父容器的高度和宽度</p>
        </div>
        
        {/* 组件会自动 flex: 1 填充剩余空间 */}
        <MessageList
          ref={ref}
          initialMessages={createRandomMessages(15)}
          licenseKey=""
        />
        
        <div style={{ 
          padding: '1rem', 
          borderTop: '1px solid var(--border)', 
          display: 'flex', 
          gap: '1rem',
          backgroundColor: 'var(--muted)',
          flexShrink: 0
        }}>
          <button 
            onClick={() => sendMessage?.('Flexbox 演示消息')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--primary)',
              color: 'var(--primary-foreground)',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            发送消息
          </button>
          <button 
            onClick={() => receiveMessage?.('这是通过 Flexbox 容器接收的消息')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--secondary)',
              color: 'var(--secondary-foreground)',
              border: '1px solid var(--border)',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            接收消息
          </button>
        </div>
      </div>
    )
  },
  parameters: {
    docs: {
      description: {
        story: 'Flexbox 容器演示：组件内部使用 flex: 1 自动填充父容器的剩余空间。父容器必须是 display: flex 和 flex-direction: column。'
      }
    }
  }
}

