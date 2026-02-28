import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Job Hunter OS',
  description: 'Automated Job Application System',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr" className="dark">
      <body className={`${inter.className} bg-gray-950 text-gray-50 flex h-screen overflow-hidden`}>
        {/* Sidebar placeholder */}
        <aside className="w-64 border-r border-gray-800 bg-gray-900/50 p-4">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
            Job Hunter OS
          </h1>
        </aside>
        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-8">
          {children}
        </main>
      </body>
    </html>
  )
}
