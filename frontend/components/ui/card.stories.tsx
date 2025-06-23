import type { Meta, StoryObj } from '@storybook/react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter, CardAction } from './card'
import { Button } from './button'

const meta: Meta<typeof Card> = {
  title: 'UI/Card',
  component: Card,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  name: '默认卡片',
  render: () => (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Card Title</CardTitle>
        <CardDescription>Card description goes here</CardDescription>
      </CardHeader>
      <CardContent>
        <p>This is the card content area where you can put any content.</p>
      </CardContent>
      <CardFooter>
        <Button>Action</Button>
      </CardFooter>
    </Card>
  ),
}

export const WithAction: Story = {
  name: '带操作按钮的卡片',
  render: () => (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Notifications</CardTitle>
        <CardDescription>You have 3 unread messages</CardDescription>
        <CardAction>
          <Button variant="outline" size="sm">
            Mark all as read
          </Button>
        </CardAction>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <p className="text-sm">New message from John</p>
          <p className="text-sm">System update available</p>
          <p className="text-sm">Weekly report ready</p>
        </div>
      </CardContent>
    </Card>
  ),
}

export const Simple: Story = {
  name: '简单卡片',
  render: () => (
    <Card className="w-[350px]">
      <CardContent>
        <p>A simple card with just content, no header or footer.</p>
      </CardContent>
    </Card>
  ),
}

export const WithBorder: Story = {
  name: '带边框的卡片',
  render: () => (
    <Card className="w-[350px]">
      <CardHeader className="border-b">
        <CardTitle>Settings</CardTitle>
        <CardDescription>Manage your account settings</CardDescription>
      </CardHeader>
      <CardContent>
        <p>Your preferences and configurations.</p>
      </CardContent>
      <CardFooter className="border-t">
        <Button>Save Changes</Button>
      </CardFooter>
    </Card>
  ),
}