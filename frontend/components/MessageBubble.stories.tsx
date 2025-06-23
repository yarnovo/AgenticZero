import type { Meta, StoryObj } from '@storybook/react'
import { MessageBubble } from './MessageBubble'
import { Message } from './types'
import { Bot, User, Heart, Star } from 'lucide-react'

const meta: Meta<typeof MessageBubble> = {
  title: 'Components/MessageBubble',
  component: MessageBubble,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    config: {
      control: { type: 'object' },
    },
  },
}

export default meta
type Story = StoryObj<typeof meta>

const sampleUserMessage: Message = {
  key: '1',
  user: 'user',
  text: 'Hello! Can you help me understand JavaScript closures?',
  timestamp: new Date(),
}

const sampleAIMessage: Message = {
  key: '2',
  user: 'ai',
  text: 'Of course! A closure in JavaScript is a function that has access to variables in its outer (enclosing) scope even after the outer function has returned. Think of it like a backpack that a function carries around with all the variables it needs.',
  timestamp: new Date(),
}

const longMessage: Message = {
  key: '3',
  user: 'ai',
  text: `Here's a detailed explanation of closures:

1. **Definition**: A closure gives you access to an outer function's scope from an inner function

2. **Example**:
\`\`\`javascript
function outerFunction(x) {
  // This is the outer function's scope
  
  function innerFunction(y) {
    // This inner function has access to 'x'
    console.log(x + y);
  }
  
  return innerFunction;
}
\`\`\`

3. **Why are they useful?**
   - Data privacy
   - Function factories
   - Callbacks with state
   
Would you like me to show you more examples?`,
  timestamp: new Date(),
}

export const UserMessage: Story = {
  name: '用户消息',
  args: {
    data: sampleUserMessage,
  },
  render: (args) => (
    <div style={{ width: '400px', padding: '20px' }}>
      <MessageBubble {...args} />
    </div>
  ),
}

export const AIMessage: Story = {
  name: 'AI消息',
  args: {
    data: sampleAIMessage,
  },
  render: (args) => (
    <div style={{ width: '400px', padding: '20px' }}>
      <MessageBubble {...args} />
    </div>
  ),
}

export const LongMessage: Story = {
  name: '长消息',
  args: {
    data: longMessage,
  },
  render: (args) => (
    <div style={{ width: '600px', padding: '20px' }}>
      <MessageBubble {...args} />
    </div>
  ),
}

export const CustomColors: Story = {
  name: '自定义颜色',
  args: {
    data: sampleUserMessage,
    config: {
      userColor: 'bg-green-500 text-white',
      aiColor: 'bg-blue-100 text-blue-900',
    },
  },
  render: (args) => (
    <div style={{ width: '400px', padding: '20px' }}>
      <MessageBubble {...args} />
    </div>
  ),
}

export const CustomAvatars: Story = {
  name: '自定义头像',
  args: {
    data: sampleAIMessage,
    config: {
      userAvatar: <User className="h-4 w-4 text-green-600" />,
      aiAvatar: <Bot className="h-4 w-4 text-blue-600" />,
    },
  },
  render: (args) => (
    <div style={{ width: '400px', padding: '20px' }}>
      <MessageBubble {...args} />
    </div>
  ),
}

export const NoAvatars: Story = {
  name: '无头像',
  args: {
    data: sampleUserMessage,
    config: {
      showAvatars: false,
    },
  },
  render: (args) => (
    <div style={{ width: '400px', padding: '20px' }}>
      <MessageBubble {...args} />
    </div>
  ),
}

export const NoTimestamp: Story = {
  name: '无时间戳',
  args: {
    data: sampleAIMessage,
    config: {
      showTimestamp: false,
    },
  },
  render: (args) => (
    <div style={{ width: '400px', padding: '20px' }}>
      <MessageBubble {...args} />
    </div>
  ),
}

export const SquareBorders: Story = {
  name: '方形边框',
  args: {
    data: sampleUserMessage,
    config: {
      borderStyle: 'square',
    },
  },
  render: (args) => (
    <div style={{ width: '400px', padding: '20px' }}>
      <MessageBubble {...args} />
    </div>
  ),
}

export const LeftAligned: Story = {
  name: '左对齐',
  args: {
    data: sampleUserMessage,
    config: {
      messageAlignment: 'left',
    },
  },
  render: (args) => (
    <div style={{ width: '400px', padding: '20px' }}>
      <MessageBubble {...args} />
    </div>
  ),
}

export const TeachingStyle: Story = {
  name: '教学风格',
  args: {
    data: {
      key: '1',
      user: 'ai',
      text: '我理解了！您刚才教授的关于 React Hooks 的概念很清晰。让我总结一下要点：\n\n1. useState 用于状态管理\n2. useEffect 处理副作用\n3. 自定义 Hook 可以复用逻辑\n\n您还有什么需要补充的吗？',
      timestamp: new Date(),
    },
    config: {
      userColor: 'bg-blue-500 text-white',
      aiColor: 'bg-green-50 border border-green-200 text-green-900',
      userAvatar: <User className="h-4 w-4 text-blue-600" />,
      aiAvatar: <Star className="h-4 w-4 text-green-600" />,
    },
  },
  render: (args) => (
    <div style={{ width: '500px', padding: '20px' }}>
      <MessageBubble {...args} />
    </div>
  ),
}

export const Conversation: Story = {
  name: '对话示例',
  render: () => (
    <div style={{ width: '600px', padding: '20px' }}>
      <MessageBubble
        data={{
          key: '1',
          user: 'user',
          text: '什么是 JavaScript 闭包？',
          timestamp: new Date(Date.now() - 120000),
        }}
        config={{
          userColor: 'bg-blue-500 text-white',
          aiColor: 'bg-gray-100 text-gray-900',
        }}
      />
      <MessageBubble
        data={{
          key: '2',
          user: 'ai',
          text: '闭包是指函数能够访问其外部作用域中的变量，即使外部函数已经执行完毕。这是 JavaScript 中的一个重要概念。',
          timestamp: new Date(Date.now() - 60000),
        }}
        config={{
          userColor: 'bg-blue-500 text-white',
          aiColor: 'bg-gray-100 text-gray-900',
        }}
      />
      <MessageBubble
        data={{
          key: '3',
          user: 'user',
          text: '能给个例子吗？',
          timestamp: new Date(),
        }}
        config={{
          userColor: 'bg-blue-500 text-white',
          aiColor: 'bg-gray-100 text-gray-900',
        }}
      />
    </div>
  ),
}