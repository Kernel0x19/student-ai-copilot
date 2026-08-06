import { useEffect } from 'react'
import { createClient } from '@/app/lib/supabase/client'
import { useRouter } from 'next/navigation'

const SESSION_KEY = 'session_login_time'
const SEVEN_DAYS_MS = 7 * 24 * 60 * 60 * 1000

export function useSessionExpiry() {
  const router = useRouter()
  const supabase = createClient()

  useEffect(() => {
    const checkExpiry = async () => {
      const { data: { session } } = await supabase.auth.getSession()

      if (!session) {
        localStorage.removeItem(SESSION_KEY)
        return
      }

      const loginTime = localStorage.getItem(SESSION_KEY)

      if (!loginTime) {
        localStorage.setItem(SESSION_KEY, Date.now().toString())
        return
      }

      const elapsed = Date.now() - parseInt(loginTime, 10)

      if (elapsed > SEVEN_DAYS_MS) {
        localStorage.removeItem(SESSION_KEY)
        await supabase.auth.signOut()
        router.push('/login')
      }
    }

    checkExpiry()
  }, [])
}