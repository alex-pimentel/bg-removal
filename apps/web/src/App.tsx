import Home from "./pages/Home"

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <header className="border-b border-slate-200 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
          <div className="flex items-center gap-3">
            <img src="/logo_agenteresolve.png" alt="bg-removal" className="h-10 w-auto" />
            <div>
              <h1 className="text-xl font-bold text-slate-900">bg-removal</h1>
              <p className="text-sm text-slate-500">
                Remove image backgrounds with AI
              </p>
            </div>
          </div>
        </div>
      </header>
      <main>
        <Home />
      </main>
      <footer className="border-t border-slate-200 bg-white/80 py-6 text-center text-sm text-slate-500 backdrop-blur-sm">
        Created by{" "}
        <a
          href="https://alexwebmaster.com.br"
          target="_blank"
          rel="noopener noreferrer"
          className="font-medium text-blue-600 hover:text-blue-700"
        >
          alexwebmaster.com.br
        </a>
      </footer>
    </div>
  )
}
