import { NextRequest, NextResponse } from 'next/server'
import { createSupabaseServerClient } from '@/lib/supabase-server'
import { prisma } from '@/lib/prisma'

export async function GET(req: NextRequest) {
  const requestUrl = new URL(req.url)
  const code = requestUrl.searchParams.get('code')

  if (code) {
    const supabase = await createSupabaseServerClient()
    const { data: sessionData, error: sessionError } = await supabase.auth.exchangeCodeForSession(code)

    if (!sessionError && sessionData.user) {
      // Check if user exists in our database
      let user = await prisma.user.findUnique({
        where: { supabaseId: sessionData.user.id }
      })

      // If not, create user
      if (!user) {
        const provider = sessionData.user.app_metadata.provider || 'oauth'
        user = await prisma.user.create({
          data: {
            email: sessionData.user.email!,
            supabaseId: sessionData.user.id,
            name: sessionData.user.user_metadata.full_name || sessionData.user.user_metadata.name,
            avatarUrl: sessionData.user.user_metadata.avatar_url,
            provider: provider,
            emailVerified: true, // OAuth providers verify email
          }
        })
      }
    }
  }

  // Redirect to home page or dashboard
  return NextResponse.redirect(new URL('/', requestUrl.origin))
}