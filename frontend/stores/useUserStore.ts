import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// 用户信息接口
export interface User {
  id: string
  name: string
  email: string
  avatar?: string
  plan: 'free' | 'pro' | 'enterprise'
  createdAt: Date
}

// 用户状态接口
interface UserState {
  user: User | null
  isLoading: boolean
  
  // 方法
  setUser: (user: User) => void
  updateUser: (updates: Partial<User>) => void
  logout: () => void
  setLoading: (loading: boolean) => void
}

// 默认用户数据（用于演示）
const defaultUser: User = {
  id: '1',
  name: 'John Doe',
  email: 'john.doe@example.com',
  avatar: 'https://avatar.vercel.sh/john',
  plan: 'pro',
  createdAt: new Date()
}

// 创建用户状态存储
export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      user: defaultUser, // 临时使用默认用户
      isLoading: false,
      
      setUser: (user) => set({ user }),
      
      updateUser: (updates) => {
        const currentUser = get().user
        if (currentUser) {
          set({ user: { ...currentUser, ...updates } })
        }
      },
      
      logout: () => set({ user: null }),
      
      setLoading: (loading) => set({ isLoading: loading })
    }),
    {
      name: 'user-storage', // localStorage 中的存储 key
      // 只持久化用户信息，不持久化 loading 状态
      partialize: (state) => ({ user: state.user })
    }
  )
)