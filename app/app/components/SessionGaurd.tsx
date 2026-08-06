'use client'
import { useSessionExpiry } from '@/app/src/hooks/useIdleLogout'

export function SessionGuard() {
  useSessionExpiry()
  return null
}