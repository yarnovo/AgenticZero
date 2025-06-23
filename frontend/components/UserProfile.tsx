'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { 
  Popover, 
  PopoverContent, 
  PopoverTrigger 
} from '@/components/ui/popover'
import { 
  User, 
  Settings, 
  LogOut, 
  Crown, 
  ChevronUp 
} from 'lucide-react'
import { useUserStore } from '@/stores/useUserStore'
import SettingsDialog from '@/components/SettingsDialog'

export default function UserProfile() {
  const { user, logout } = useUserStore()
  const [isOpen, setIsOpen] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)

  if (!user) {
    return null
  }

  const getPlanBadgeStyle = (plan: string) => {
    switch (plan) {
      case 'pro':
        return 'bg-amber-100 text-amber-800 border-amber-200'
      case 'enterprise':
        return 'bg-purple-100 text-purple-800 border-purple-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getPlanDisplayName = (plan: string) => {
    switch (plan) {
      case 'pro':
        return 'Pro'
      case 'enterprise':
        return 'Enterprise'
      default:
        return 'Free'
    }
  }

  return (
    <>
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          className="w-full h-auto p-3 justify-between hover:bg-muted/50"
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
              {user.avatar ? (
                <img 
                  src={user.avatar} 
                  alt={user.name}
                  className="w-full h-full rounded-full object-cover"
                />
              ) : (
                <User className="w-4 h-4" />
              )}
            </div>
            <div className="flex flex-col items-start text-left">
              <div className="text-sm font-medium truncate max-w-32">
                {user.name}
              </div>
              <div className="text-xs text-muted-foreground">
                {getPlanDisplayName(user.plan)}
              </div>
            </div>
          </div>
          <ChevronUp className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </Button>
      </PopoverTrigger>
      
      <PopoverContent className="w-80 p-0" align="start" side="top">
        <div className="p-4 border-b">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              {user.avatar ? (
                <img 
                  src={user.avatar} 
                  alt={user.name}
                  className="w-full h-full rounded-full object-cover"
                />
              ) : (
                <User className="w-6 h-6" />
              )}
            </div>
            <div className="flex-1">
              <h3 className="font-medium">{user.name}</h3>
              <p className="text-sm text-muted-foreground">{user.email}</p>
            </div>
            <div className={`px-2 py-1 rounded-full text-xs font-medium border ${getPlanBadgeStyle(user.plan)}`}>
              {user.plan === 'pro' && <Crown className="w-3 h-3 inline mr-1" />}
              {getPlanDisplayName(user.plan)}
            </div>
          </div>
          
          <div className="text-xs text-muted-foreground">
            加入时间: {new Date(user.createdAt).toLocaleDateString('zh-CN')}
          </div>
        </div>
        
        <div className="p-2">
          <Button
            variant="ghost"
            className="w-full justify-start"
            onClick={() => {
              setIsOpen(false)
              setSettingsOpen(true)
            }}
          >
            <Settings className="w-4 h-4 mr-2" />
            设置
          </Button>
          
          <Button
            variant="ghost"
            className="w-full justify-start text-destructive hover:text-destructive"
            onClick={() => {
              setIsOpen(false)
              logout()
              // TODO: 重定向到登录页面或清空会话
              console.log('用户退出登录')
            }}
          >
            <LogOut className="w-4 h-4 mr-2" />
            退出登录
          </Button>
        </div>
      </PopoverContent>
    </Popover>
    
    {/* 设置弹窗 */}
    <SettingsDialog 
      open={settingsOpen} 
      onOpenChange={setSettingsOpen} 
    />
  </>
  )
}