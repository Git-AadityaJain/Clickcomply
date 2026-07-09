"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Shield, Loader2, ArrowRight } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { loginUser, registerUser } from "@/lib/api"
import { saveTokens, setSkippedAuth } from "@/lib/auth"

type Mode = "login" | "register"

export default function LoginPage() {
  const router = useRouter()
  const [mode, setMode] = useState<Mode>("login")
  const [fullName, setFullName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const isRegister = mode === "register"

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const tokens = isRegister
        ? await registerUser(email, password, fullName)
        : await loginUser(email, password)
      saveTokens(tokens)
      router.replace("/")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.")
    } finally {
      setSubmitting(false)
    }
  }

  function handleSkip() {
    setSkippedAuth()
    router.replace("/")
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12">
      <div className="w-full max-w-md">
        <div className="mb-8 flex flex-col items-center gap-3 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary">
            <Shield className="h-6 w-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-foreground">
              ClickComply
            </h1>
            <p className="text-sm text-muted-foreground">DPDP policy review</p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>{isRegister ? "Create your account" : "Sign in"}</CardTitle>
            <CardDescription>
              {isRegister
                ? "Set up an account to keep your reviews private to you."
                : "Sign in to access your compliance reviews."}
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleSubmit}>
            <CardContent className="flex flex-col gap-4">
              {isRegister && (
                <div className="flex flex-col gap-2">
                  <Label htmlFor="fullName">Full name</Label>
                  <Input
                    id="fullName"
                    type="text"
                    autoComplete="name"
                    placeholder="Jane Doe"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                  />
                </div>
              )}

              <div className="flex flex-col gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  placeholder="you@company.com"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div className="flex flex-col gap-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  autoComplete={isRegister ? "new-password" : "current-password"}
                  placeholder={isRegister ? "At least 8 characters" : "Your password"}
                  required
                  minLength={isRegister ? 8 : undefined}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              {error && (
                <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                  {error}
                </p>
              )}
            </CardContent>

            <CardFooter className="mt-2 flex flex-col gap-3">
              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting && <Loader2 className="h-4 w-4 animate-spin" />}
                {isRegister ? "Create account" : "Sign in"}
              </Button>

              <button
                type="button"
                className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                onClick={() => {
                  setError(null)
                  setMode(isRegister ? "login" : "register")
                }}
              >
                {isRegister
                  ? "Already have an account? Sign in"
                  : "Need an account? Create one"}
              </button>
            </CardFooter>
          </form>
        </Card>

        <div className="mt-6 flex flex-col items-center gap-2">
          <Button
            type="button"
            variant="ghost"
            className="gap-1.5 text-muted-foreground"
            onClick={handleSkip}
          >
            Skip for now
            <ArrowRight className="h-4 w-4" />
          </Button>
          <p className="text-center text-xs text-muted-foreground">
            Continue without signing in. You can sign in later.
          </p>
        </div>
      </div>
    </div>
  )
}
