import { ServiceShell, UserButton } from "@agenteresolve/ui"
import Home from "./pages/Home"
import { ApiTokenProvider } from "./lib/apiToken"

function Logo() {
  return (
    <a href="https://agenteresolve.com.br" className="flex items-center gap-2">
      <img src="/logo_agenteresolve.png" alt="Agenteresolve" className="h-8 w-auto" />
    </a>
  )
}

export default function App() {
  return (
    <ServiceShell
      logo={<Logo />}
      authSlot={<UserButton signInLabel="Entrar" />}
      publishableKey={import.meta.env.VITE_CLERK_PUBLISHABLE_KEY}
      contentClassName="text-foreground"
    >
      <ApiTokenProvider>
        <Home />
      </ApiTokenProvider>
    </ServiceShell>
  )
}
