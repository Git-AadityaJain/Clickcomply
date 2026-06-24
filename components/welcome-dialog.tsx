"use client"

import { useEffect, useState, type ReactNode } from "react"
import { Shield } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { WELCOME_SECTIONS, WELCOME_SUBTITLE } from "@/lib/help-content"

function WelcomeBody() {
  return (
    <div className="space-y-5 text-sm text-muted-foreground">
      {WELCOME_SECTIONS.map((section) => (
        <section key={section.title}>
          <h3 className="mb-1.5 font-medium text-foreground">{section.title}</h3>
          {"body" in section && <p>{section.body}</p>}
          {"bullets" in section && (
            <ul className="list-disc space-y-1 pl-5">
              {section.bullets.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          )}
        </section>
      ))}
    </div>
  )
}

function WelcomeDialogContent({ onClose }: { onClose: () => void }) {
  return (
    <DialogContent className="max-h-[min(90vh,640px)] overflow-y-auto sm:max-w-lg">
      <DialogHeader>
        <DialogTitle className="flex items-center gap-2">
          <Shield className="h-5 w-5 text-primary" />
          Welcome to ClickComply
        </DialogTitle>
        <DialogDescription>{WELCOME_SUBTITLE}</DialogDescription>
      </DialogHeader>
      <WelcomeBody />
      <DialogFooter className="sm:justify-end">
        <Button type="button" onClick={onClose}>
          OK
        </Button>
      </DialogFooter>
    </DialogContent>
  )
}

export function WelcomeDialog() {
  const [open, setOpen] = useState(false)

  useEffect(() => {
    setOpen(true)
  }, [])

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <WelcomeDialogContent onClose={() => setOpen(false)} />
    </Dialog>
  )
}

export function WelcomeGuideTrigger({ trigger }: { trigger: ReactNode }) {
  const [open, setOpen] = useState(false)

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <WelcomeDialogContent onClose={() => setOpen(false)} />
    </Dialog>
  )
}
