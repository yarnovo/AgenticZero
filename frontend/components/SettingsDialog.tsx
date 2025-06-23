'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card'
import { 
  Settings, 
  Check, 
  AlertTriangle,
  Eye,
  EyeOff
} from 'lucide-react'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { useSettingsStore, type ApiProvider } from '@/stores/useSettingsStore'

interface SettingsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export default function SettingsDialog({ open, onOpenChange }: SettingsDialogProps) {
  const { 
    apiConfig, 
    activeProvider, 
    updateApiConfig, 
    setActiveProvider, 
    resetApiConfig,
    validateApiConfig 
  } = useSettingsStore()
  
  const [showApiKeys, setShowApiKeys] = useState({
    openai: false,
    anthropic: false
  })
  
  const [tempConfig, setTempConfig] = useState(apiConfig)

  const handleSave = () => {
    // 保存所有配置
    Object.keys(tempConfig).forEach((provider) => {
      updateApiConfig(provider as ApiProvider, tempConfig[provider as ApiProvider])
    })
    onOpenChange(false)
  }

  const handleReset = (provider: ApiProvider) => {
    resetApiConfig(provider)
    setTempConfig({ ...apiConfig })
  }

  const updateTempConfig = (provider: ApiProvider, updates: any) => {
    setTempConfig(prev => ({
      ...prev,
      [provider]: {
        ...prev[provider],
        ...updates
      }
    }))
  }

  const toggleApiKeyVisibility = (provider: 'openai' | 'anthropic') => {
    setShowApiKeys(prev => ({
      ...prev,
      [provider]: !prev[provider]
    }))
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            设置
          </DialogTitle>
          <DialogDescription>
            配置你的 AI 服务提供商设置
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* 当前活跃提供商 */}
          <div>
            <h3 className="text-lg font-medium mb-3">当前使用的提供商</h3>
            <RadioGroup
              value={activeProvider}
              onValueChange={(value) => setActiveProvider(value as ApiProvider)}
              className="flex gap-6"
            >
              {(['openai', 'anthropic', 'ollama'] as ApiProvider[]).map((provider) => (
                <div key={provider} className="flex items-center space-x-2">
                  <RadioGroupItem value={provider} id={provider} />
                  <label 
                    htmlFor={provider} 
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer flex items-center gap-2"
                  >
                    {provider === 'openai' && 'OpenAI'}
                    {provider === 'anthropic' && 'Anthropic'}
                    {provider === 'ollama' && 'Ollama'}
                    {validateApiConfig(provider) && (
                      <Check className="w-4 h-4 text-green-500" />
                    )}
                  </label>
                </div>
              ))}
            </RadioGroup>
          </div>

          {/* OpenAI 配置 */}
          <Card>
            <CardHeader>
              <CardTitle>
                OpenAI 配置
              </CardTitle>
              <CardDescription>
                配置 OpenAI API 密钥和设置
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label htmlFor="openai-key" className="text-sm font-medium">
                  API 密钥
                </label>
                <div className="flex gap-2 mt-1">
                  <Input
                    id="openai-key"
                    type={showApiKeys.openai ? "text" : "password"}
                    placeholder="sk-..."
                    value={tempConfig.openai.apiKey}
                    onChange={(e) => updateTempConfig('openai', { apiKey: e.target.value })}
                  />
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => toggleApiKeyVisibility('openai')}
                  >
                    {showApiKeys.openai ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </Button>
                </div>
              </div>
              <div>
                <label htmlFor="openai-base-url" className="text-sm font-medium">
                  API 基础 URL
                </label>
                <Input
                  id="openai-base-url"
                  className="mt-1"
                  placeholder="https://api.openai.com/v1"
                  value={tempConfig.openai.baseUrl}
                  onChange={(e) => updateTempConfig('openai', { baseUrl: e.target.value })}
                />
              </div>
              <div>
                <label htmlFor="openai-model" className="text-sm font-medium">
                  模型
                </label>
                <Input
                  id="openai-model"
                  className="mt-1"
                  placeholder="gpt-4o-mini"
                  value={tempConfig.openai.model}
                  onChange={(e) => updateTempConfig('openai', { model: e.target.value })}
                />
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => handleReset('openai')}
              >
                重置为默认值
              </Button>
            </CardContent>
          </Card>

          {/* Anthropic 配置 */}
          <Card>
            <CardHeader>
              <CardTitle>
                Anthropic 配置
              </CardTitle>
              <CardDescription>
                配置 Anthropic Claude API 密钥和设置
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label htmlFor="anthropic-key" className="text-sm font-medium">
                  API 密钥
                </label>
                <div className="flex gap-2 mt-1">
                  <Input
                    id="anthropic-key"
                    type={showApiKeys.anthropic ? "text" : "password"}
                    placeholder="sk-ant-..."
                    value={tempConfig.anthropic.apiKey}
                    onChange={(e) => updateTempConfig('anthropic', { apiKey: e.target.value })}
                  />
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => toggleApiKeyVisibility('anthropic')}
                  >
                    {showApiKeys.anthropic ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </Button>
                </div>
              </div>
              <div>
                <label htmlFor="anthropic-base-url" className="text-sm font-medium">
                  API 基础 URL
                </label>
                <Input
                  id="anthropic-base-url"
                  className="mt-1"
                  placeholder="https://api.anthropic.com"
                  value={tempConfig.anthropic.baseUrl}
                  onChange={(e) => updateTempConfig('anthropic', { baseUrl: e.target.value })}
                />
              </div>
              <div>
                <label htmlFor="anthropic-model" className="text-sm font-medium">
                  模型
                </label>
                <Input
                  id="anthropic-model"
                  className="mt-1"
                  placeholder="claude-3-haiku-20240307"
                  value={tempConfig.anthropic.model}
                  onChange={(e) => updateTempConfig('anthropic', { model: e.target.value })}
                />
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => handleReset('anthropic')}
              >
                重置为默认值
              </Button>
            </CardContent>
          </Card>

          {/* Ollama 配置 */}
          <Card>
            <CardHeader>
              <CardTitle>
                Ollama 配置
              </CardTitle>
              <CardDescription>
                配置本地 Ollama 服务器设置
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="ollama-base-url" className="text-sm font-medium">
                    服务器地址
                  </label>
                  <Input
                    id="ollama-base-url"
                    className="mt-1"
                    placeholder="http://localhost"
                    value={tempConfig.ollama.baseUrl}
                    onChange={(e) => updateTempConfig('ollama', { baseUrl: e.target.value })}
                  />
                </div>
                <div>
                  <label htmlFor="ollama-port" className="text-sm font-medium">
                    端口号
                  </label>
                  <Input
                    id="ollama-port"
                    className="mt-1"
                    type="number"
                    placeholder="11434"
                    value={tempConfig.ollama.port}
                    onChange={(e) => updateTempConfig('ollama', { port: parseInt(e.target.value) || 11434 })}
                  />
                </div>
              </div>
              <div>
                <label htmlFor="ollama-model" className="text-sm font-medium">
                  模型
                </label>
                <Input
                  id="ollama-model"
                  className="mt-1"
                  placeholder="llama3.2:latest"
                  value={tempConfig.ollama.model}
                  onChange={(e) => updateTempConfig('ollama', { model: e.target.value })}
                />
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => handleReset('ollama')}
              >
                重置为默认值
              </Button>
            </CardContent>
          </Card>

          {/* 安全提示 */}
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>安全提示</AlertTitle>
            <AlertDescription>
              API 密钥将被安全地存储在你的浏览器本地存储中。请不要在不受信任的设备上输入你的 API 密钥。
            </AlertDescription>
          </Alert>
        </div>

        {/* 操作按钮 */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            取消
          </Button>
          <Button onClick={handleSave}>
            保存设置
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}