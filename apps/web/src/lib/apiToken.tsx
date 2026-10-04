import { createContext, useContext, type ReactNode } from "react"
import { useAuth } from "@clerk/clerk-react"
import { useClerkAvailable } from "@agenteresolve/ui"

type TokenGetter = () => Promise<string | null>

const TokenContext = createContext<TokenGetter>(async () => null)

function LiveTokenProvider({ children }: { children: ReactNode }) {
  const { getToken } = useAuth()
  return <TokenContext.Provider value={getToken}>{children}</TokenContext.Provider>
}

function AnonymousTokenProvider({ children }: { children: ReactNode }) {
  return (
    <TokenContext.Provider value={async () => null}>{children}</TokenContext.Provider>
  )
}

/**
 * Provides a `getToken` function backed by Clerk when configured, or an
 * anonymous `null` getter otherwise. Must be rendered inside the ServiceShell
 * (i.e. inside `AuthProvider`).
 */
export function ApiTokenProvider({ children }: { children: ReactNode }) {
  const available = useClerkAvailable()
  return available ? (
    <LiveTokenProvider>{children}</LiveTokenProvider>
  ) : (
    <AnonymousTokenProvider>{children}</AnonymousTokenProvider>
  )
}

export function useApiToken(): TokenGetter {
  return useContext(TokenContext)
}
