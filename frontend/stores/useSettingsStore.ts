import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// API 提供商类型
export type ApiProvider = 'openai' | 'anthropic' | 'ollama'

// API 配置接口
export interface ApiConfig {
  openai: {
    apiKey: string
    baseUrl: string
    model: string
  }
  anthropic: {
    apiKey: string
    baseUrl: string
    model: string
  }
  ollama: {
    baseUrl: string
    port: number
    model: string
  }
}

// 设置状态接口
interface SettingsState {
  apiConfig: ApiConfig
  activeProvider: ApiProvider
  
  // 方法
  updateApiConfig: (provider: ApiProvider, config: Partial<ApiConfig[ApiProvider]>) => void
  setActiveProvider: (provider: ApiProvider) => void
  resetApiConfig: (provider?: ApiProvider) => void
  validateApiConfig: (provider: ApiProvider) => boolean
}

// 默认配置
const defaultApiConfig: ApiConfig = {
  openai: {
    apiKey: '',
    baseUrl: 'https://api.openai.com/v1',
    model: 'gpt-4o-mini'
  },
  anthropic: {
    apiKey: '',
    baseUrl: 'https://api.anthropic.com',
    model: 'claude-3-haiku-20240307'
  },
  ollama: {
    baseUrl: 'http://localhost',
    port: 11434,
    model: 'llama3.2:latest'
  }
}

// 创建设置状态存储
export const useSettingsStore = create<SettingsState>()(
  persist(
    (set, get) => ({
      apiConfig: defaultApiConfig,
      activeProvider: 'openai',
      
      updateApiConfig: (provider, config) => {
        const currentConfig = get().apiConfig
        set({
          apiConfig: {
            ...currentConfig,
            [provider]: {
              ...currentConfig[provider],
              ...config
            }
          }
        })
      },
      
      setActiveProvider: (provider) => set({ activeProvider: provider }),
      
      resetApiConfig: (provider) => {
        if (provider) {
          const currentConfig = get().apiConfig
          set({
            apiConfig: {
              ...currentConfig,
              [provider]: defaultApiConfig[provider]
            }
          })
        } else {
          set({ apiConfig: defaultApiConfig })
        }
      },
      
      validateApiConfig: (provider) => {
        const config = get().apiConfig[provider]
        
        switch (provider) {
          case 'openai':
          case 'anthropic':
            return !!(config as any).apiKey && !!(config as any).baseUrl && !!(config as any).model
          case 'ollama':
            return !!(config as any).baseUrl && !!(config as any).port && !!(config as any).model
          default:
            return false
        }
      }
    }),
    {
      name: 'settings-storage',
      // 加密敏感信息（这里简单示例，实际应用中需要更安全的加密方案）
      partialize: (state) => ({
        apiConfig: {
          ...state.apiConfig,
          // 在实际应用中，API keys 应该被加密存储
          openai: { ...state.apiConfig.openai },
          anthropic: { ...state.apiConfig.anthropic }
        },
        activeProvider: state.activeProvider
      })
    }
  )
)