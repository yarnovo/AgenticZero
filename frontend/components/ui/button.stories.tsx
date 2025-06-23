import type { Meta, StoryObj } from '@storybook/react'
import { Button } from './button'

const meta: Meta<typeof Button> = {
  title: 'UI/Button',
  component: Button,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'],
    },
    size: {
      control: { type: 'select' },
      options: ['default', 'sm', 'lg', 'icon'],
    },
    asChild: {
      control: { type: 'boolean' },
    },
  },
}

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  name: '默认按钮',
  args: {
    children: 'Button',
  },
}

export const Destructive: Story = {
  name: '危险按钮',
  args: {
    variant: 'destructive',
    children: 'Delete',
  },
}

export const Outline: Story = {
  name: '轮廓按钮',
  args: {
    variant: 'outline',
    children: 'Outline',
  },
}

export const Secondary: Story = {
  name: '次要按钮',
  args: {
    variant: 'secondary',
    children: 'Secondary',
  },
}

export const Ghost: Story = {
  name: '幽灵按钮',
  args: {
    variant: 'ghost',
    children: 'Ghost',
  },
}

export const Link: Story = {
  name: '链接按钮',
  args: {
    variant: 'link',
    children: 'Link',
  },
}

export const Small: Story = {
  name: '小号按钮',
  args: {
    size: 'sm',
    children: 'Small',
  },
}

export const Large: Story = {
  name: '大号按钮',
  args: {
    size: 'lg',
    children: 'Large',
  },
}

export const Icon: Story = {
  name: '图标按钮',
  args: {
    size: 'icon',
    children: '🔥',
  },
}