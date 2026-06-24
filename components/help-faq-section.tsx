"use client"

import type { ReactNode } from "react"
import { CircleHelp, Mail, MessageCircleQuestion, BookOpen } from "lucide-react"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  FAQ_ITEMS,
  SUPPORT_EMAIL,
  SUPPORT_MAILTO,
} from "@/lib/help-content"
import { WelcomeGuideTrigger } from "@/components/welcome-dialog"

function SupportDialog({ trigger }: { trigger: ReactNode }) {
  return (
    <Dialog>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Need help or guidance?</DialogTitle>
          <DialogDescription>
            For setup issues, DPDP interpretation, or review questions
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-3 text-sm text-muted-foreground">
          <p>
            ClickComply automates policy checks. It does not replace legal
            counsel. For compliance decisions, work with a qualified privacy or
            legal advisor.
          </p>
          <p>
            Questions about setup, DPDP rules, or your review? Email{" "}
            <a
              href={SUPPORT_MAILTO}
              className="font-medium text-primary underline-offset-4 hover:underline"
            >
              {SUPPORT_EMAIL}
            </a>
            . We typically reply within one business day.
          </p>
        </div>
        <DialogFooter className="gap-2 sm:justify-end">
          <Button asChild variant="default">
            <a href={SUPPORT_MAILTO}>
              <Mail className="mr-2 h-4 w-4" />
              Email support
            </a>
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export function HelpFaqSection() {
  return (
    <Card id="help-faq">
      <CardHeader className="pb-3">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <CardTitle className="flex items-center gap-2 text-base">
              <MessageCircleQuestion className="h-4 w-4 text-primary" />
              FAQ
            </CardTitle>
            <CardDescription>Common questions about reviews and keeps</CardDescription>
          </div>
          <div className="flex flex-wrap gap-2">
            <WelcomeGuideTrigger
              trigger={
                <Button variant="ghost" size="sm" className="gap-1.5">
                  <BookOpen className="h-4 w-4" />
                  Guide
                </Button>
              }
            />
            <SupportDialog
            trigger={
              <Button variant="outline" size="sm" className="gap-1.5">
                <CircleHelp className="h-4 w-4" />
                Help
              </Button>
            }
            />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Accordion type="single" collapsible className="w-full">
          {FAQ_ITEMS.map((item) => (
            <AccordionItem key={item.id} value={item.id}>
              <AccordionTrigger className="text-left text-sm">
                {item.question}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {item.answer}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </CardContent>
    </Card>
  )
}
