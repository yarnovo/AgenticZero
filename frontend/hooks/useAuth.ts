'use client'

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { User } from '@supabase/supabase-js'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
    })

    return () => subscription.unsubscribe()
  }, [])

  const signUp = async (email: string, password: string, username?: string) => {
    const response = await fetch('/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, username })
    })
    return response.json()
  }

  const signIn = async (emailOrUsername: string, password: string) => {
    const isEmail = emailOrUsername.includes('@')
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        [isEmail ? 'email' : 'username']: emailOrUsername,
        password
      })
    })
    return response.json()
  }

  const signInWithOAuth = async (provider: 'github' | 'google') => {
    const response = await fetch('/api/auth/oauth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider })
    })
    const data = await response.json()
    if (data.url) {
      window.location.href = data.url
    }
    return data
  }

  const signOut = async () => {
    const response = await fetch('/api/auth/logout', {
      method: 'POST'
    })
    return response.json()
  }

  return {
    user,
    loading,
    signUp,
    signIn,
    signInWithOAuth,
    signOut
  }
}