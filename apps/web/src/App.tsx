import Home from "./pages/Home"

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <header className="border-b border-slate-200 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900">bg-removal</h1>
            <p className="text-sm text-slate-500">
              Remove image backgrounds with AI
            </p>
          </div>
        </div>
      </header>
      <main>
        <Home />
      </main>
    </div>
  )
}
