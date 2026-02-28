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
      <body className={`${inter.className} bg-[#050505] text-gray-200 flex h-screen overflow-hidden selection:bg-blue-500/30`}>
        {/* Sidebar */}
        <aside className="w-72 border-r border-white/5 bg-[#0a0a0a]/80 backdrop-blur-3xl p-6 flex flex-col justify-between relative overflow-hidden">
          {/* Subtle glow effect behind sidebar */}
          <div className="absolute top-0 left-0 w-full h-64 bg-blue-500/5 blur-[100px] pointer-events-none" />

          <div>
            <div className="flex items-center gap-3 mb-10">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-[0_0_20px_rgba(59,130,246,0.3)]">
                <span className="text-white font-bold text-sm">JH</span>
              </div>
              <h1 className="text-xl font-bold tracking-tight text-white">
                Job Hunter <span className="text-blue-500 font-light">OS</span>
              </h1>
            </div>

            <nav className="space-y-1">
              <div className="px-4 py-2.5 rounded-xl bg-white/5 text-white font-medium border border-white/5 flex items-center gap-3">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)]" />
                Sourcing & Builder
              </div>
              <div className="px-4 py-2.5 rounded-xl text-gray-400 font-medium hover:text-white hover:bg-white/5 cursor-pointer transition-all flex items-center gap-3">
                Kanban Board
              </div>
            </nav>
          </div>

          <div className="p-4 rounded-xl bg-gradient-to-br from-white/[0.03] to-white/[0.01] border border-white/5 backdrop-blur-md">
            <p className="text-xs text-gray-400 font-medium tracking-wider uppercase mb-1">Status</p>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)] animate-pulse" />
              <p className="text-sm text-gray-200">Scrapers Ready</p>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-10 relative bg-[#050505] selection:bg-blue-500/30">
          {/* Decorative ambient light */}
          <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-500/10 blur-[150px] rounded-full pointer-events-none translate-x-1/2 -translate-y-1/2" />

          <div className="max-w-6xl mx-auto h-full relative z-10">
            {children}
          </div>
        </main>
      </body>
    </html>
  )
}
