import { NextRequest, NextResponse } from 'next/server'
import { createSupabaseServerClient } from '@/lib/supabase-server'

export async function POST(req: NextRequest) {
  try {
    const { provider } = await req.json()

    if (!provider || !['github', 'google'].includes(provider)) {
      return NextResponse.json(
        { error: 'Invalid provider' },
        { status: 400 }
      )
    }

    const supabase = await createSupabaseServerClient()

    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: provider as 'github' | 'google',
      options: {
        redirectTo: `${req.nextUrl.origin}/api/auth/callback`,
      }
    })

    if (error) {
      return NextResponse.json(
        { error: error.message },
        { status: 400 }
      )
    }

    return NextResponse.json({ url: data.url })
  } catch (error) {
    console.error('OAuth error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}