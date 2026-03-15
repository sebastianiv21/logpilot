import { useEffect, useState } from 'react'
import { Sun, Moon } from 'lucide-react'

const THEME_KEY = 'theme'

function getTheme(): 'light' | 'dark' {
  if (typeof document === 'undefined') return 'light'
  const stored = localStorage.getItem(THEME_KEY) as 'light' | 'dark' | null
  if (stored === 'light' || stored === 'dark') return stored
  const doc = document.documentElement.getAttribute('data-theme') as 'light' | 'dark' | null
  if (doc === 'light' || doc === 'dark') return doc
  return 'light'
}

function applyTheme(next: 'light' | 'dark') {
  document.documentElement.setAttribute('data-theme', next)
  localStorage.setItem(THEME_KEY, next)
}

export function ThemeSwitcher() {
  const [theme, setTheme] = useState<'light' | 'dark'>(getTheme)

  useEffect(() => {
    const handler = (): void => setTheme(getTheme())
    window.addEventListener('storage', handler)
    const observer = new MutationObserver(handler)
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    return () => {
      window.removeEventListener('storage', handler)
      observer.disconnect()
    }
  }, [])

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault()
    const next = theme === 'dark' ? 'light' : 'dark'
    applyTheme(next)
    setTheme(next)
  }

  return (
    <label
      className="swap swap-rotate btn btn-ghost btn-circle btn-sm"
      title={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
      aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
      onClick={handleClick}
    >
      <input type="checkbox" checked={theme === 'dark'} readOnly tabIndex={-1} aria-hidden />
      <Sun className="swap-off h-5 w-5" aria-hidden />
      <Moon className="swap-on h-5 w-5" aria-hidden />
    </label>
  )
}
