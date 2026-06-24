"use client"

import { useRef, useState } from "react"
import { ChevronLeft, ChevronRight, ClipboardList, Upload, FileText } from "lucide-react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Checkbox } from "@/components/ui/checkbox"
import { Switch } from "@/components/ui/switch"
import { Progress } from "@/components/ui/progress"
import {
  type OrgProfile,
  type WizardCompletePayload,
  defaultOrgProfile,
  WIZARD_STEPS,
  FORM_COVERAGE_NOTE,
  PROCESSING_TYPE_OPTIONS,
  AUDIENCE_OPTIONS,
  DATA_COLLECTED_OPTIONS,
  STORAGE_OPTIONS,
  RETENTION_OPTIONS,
  YES_NO_OPTIONS,
} from "@/lib/org-profile"

interface OrgQuestionnaireWizardProps {
  onComplete: (payload: WizardCompletePayload) => void
  disabled?: boolean
}

export function OrgQuestionnaireWizard({ onComplete, disabled = false }: OrgQuestionnaireWizardProps) {
  const [step, setStep] = useState(0)
  const [profile, setProfile] = useState<OrgProfile>(defaultOrgProfile())
  const [policyFile, setPolicyFile] = useState<File | null>(null)
  const [generateDraft, setGenerateDraft] = useState(false)
  const [draftFormat, setDraftFormat] = useState<"docx" | "pdf">("docx")
  const [error, setError] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  function update<K extends keyof OrgProfile>(key: K, value: OrgProfile[K]) {
    setProfile((prev) => ({ ...prev, [key]: value }))
  }

  function validateStep(): string | null {
    if (step === 0) {
      if (!profile.legal_name.trim()) return "Step 1 — Your company → Company name: Enter your company's legal name."
      if (!profile.website_domain.trim()) return "Step 1 — Your company → Website: Enter your website address."
      if (!profile.contact_email.trim()) return "Step 1 — Your company → Privacy email: Enter a contact email."
      if (!profile.grievance_officer_name.trim()) return "Step 1 — Your company → Grievance officer name: Enter a contact name."
    }
    if (step === 4 && generateDraft && !policyFile) {
      // draft only — ok without upload
    }
    return null
  }

  function handleNext() {
    const msg = validateStep()
    if (msg) {
      setError(msg)
      return
    }
    setError(null)
    if (step < WIZARD_STEPS.length - 1) {
      setStep((s) => s + 1)
    } else {
      onComplete({ profile, policyFile, generateDraft, draftFormat })
    }
  }

  const progress = Math.round(((step + 1) / WIZARD_STEPS.length) * 100)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <ClipboardList className="h-4 w-4 text-primary" />
          Privacy questionnaire
        </CardTitle>
        <CardDescription>
          Step {step + 1} of {WIZARD_STEPS.length}: {WIZARD_STEPS[step].description}
        </CardDescription>
        <Progress value={progress} className="mt-2 h-1.5" />
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {step > 0 && step < 4 && (
          <p className="text-xs text-muted-foreground">{FORM_COVERAGE_NOTE}</p>
        )}

        {step === 0 && (
          <div className="grid gap-3 sm:grid-cols-2">
            <Field label="Company name" className="sm:col-span-2">
              <Input value={profile.legal_name} onChange={(e) => update("legal_name", e.target.value)} disabled={disabled} />
            </Field>
            <Field label="Website">
              <Input value={profile.website_domain} onChange={(e) => update("website_domain", e.target.value)} placeholder="https://yoursite.com" disabled={disabled} />
            </Field>
            <Field label="Privacy email">
              <Input type="email" value={profile.contact_email} onChange={(e) => update("contact_email", e.target.value)} disabled={disabled} />
            </Field>
            <Field label="Grievance officer name">
              <Input value={profile.grievance_officer_name} onChange={(e) => update("grievance_officer_name", e.target.value)} disabled={disabled} />
            </Field>
            <Field label="Their job title">
              <Input value={profile.grievance_officer_designation} onChange={(e) => update("grievance_officer_designation", e.target.value)} disabled={disabled} />
            </Field>
          </div>
        )}

        {step === 1 && (
          <div className="flex flex-col gap-4">
            <SingleChoice
              label="Which best describes your main data processing?"
              options={PROCESSING_TYPE_OPTIONS.map((o) => ({ value: o.value, label: o.label, hint: o.hint }))}
              value={profile.processing_type}
              onChange={(v) => update("processing_type", v as OrgProfile["processing_type"])}
              disabled={disabled}
            />
            <SingleChoice
              label="Who mainly uses your service?"
              options={AUDIENCE_OPTIONS}
              value={profile.audience_type}
              onChange={(v) => update("audience_type", v as OrgProfile["audience_type"])}
              disabled={disabled}
            />
          </div>
        )}

        {step === 2 && (
          <div className="flex flex-col gap-4">
            <SingleChoice
              label="What personal data do you collect most?"
              options={DATA_COLLECTED_OPTIONS}
              value={profile.data_collected}
              onChange={(v) => update("data_collected", v as OrgProfile["data_collected"])}
              disabled={disabled}
            />
            <div>
              <Label className="mb-2 block text-sm">Where is data stored?</Label>
              <div className="flex flex-wrap gap-2">
                {STORAGE_OPTIONS.map((opt) => (
                  <Button
                    key={opt.value}
                    type="button"
                    size="sm"
                    variant={profile.data_storage_location === opt.value ? "default" : "outline"}
                    onClick={() => update("data_storage_location", opt.value)}
                    disabled={disabled}
                  >
                    {opt.label}
                  </Button>
                ))}
              </div>
            </div>
            <YesNoRow label="Do you use AI on personal data?" value={profile.uses_ai} onChange={(v) => update("uses_ai", v)} disabled={disabled} />
            <YesNoRow label="Do outside companies help you process data?" value={profile.uses_third_parties} onChange={(v) => update("uses_third_parties", v)} disabled={disabled} />
            <YesNoRow label="Do you use analytics or non-essential cookies?" value={profile.uses_analytics_cookies} onChange={(v) => update("uses_analytics_cookies", v)} disabled={disabled} />
            <SingleChoice
              label="After someone deletes their account, how long do you keep data?"
              options={RETENTION_OPTIONS}
              value={profile.retention_period}
              onChange={(v) => update("retention_period", v as OrgProfile["retention_period"])}
              disabled={disabled}
            />
          </div>
        )}

        {step === 3 && (
          <div className="flex flex-col gap-4">
            <YesNoRow label="Is your service meant for people under 18?" value={profile.platform_for_under_18} onChange={(v) => update("platform_for_under_18", v)} disabled={disabled} />
            <YesNoRow
              label="Do you have customers or users outside India?"
              value={profile.users_outside_india}
              onChange={(v) => update("users_outside_india", v)}
              disabled={disabled}
              hint="Choose Yes if you serve international business clients or overseas users."
            />
            <YesNoRow label="Do you have basic security measures in place?" value={profile.has_security_safeguards} onChange={(v) => update("has_security_safeguards", v)} disabled={disabled} />
            <ToggleRow label="We sell personal data" checked={profile.sells_personal_data} onCheckedChange={(v) => update("sells_personal_data", v)} disabled={disabled} />
            <ToggleRow label="We share data for advertising" checked={profile.shares_for_advertising} onCheckedChange={(v) => update("shares_for_advertising", v)} disabled={disabled} />
          </div>
        )}

        {step === 4 && (
          <div className="flex flex-col gap-4">
            <div>
              <Label className="mb-2 block text-sm">Upload your current privacy policy (PDF or Word)</Label>
              <p className="mb-2 text-xs text-muted-foreground">
                We will check this against DPDP requirements. You can skip this if you only want a suggested draft.
              </p>
              <div
                role="button"
                tabIndex={0}
                className="flex cursor-pointer flex-col items-center gap-2 rounded-lg border-2 border-dashed p-5 hover:border-primary/40"
                onClick={() => fileRef.current?.click()}
                onKeyDown={(e) => e.key === "Enter" && fileRef.current?.click()}
              >
                <input ref={fileRef} type="file" accept=".pdf,.docx,.doc" className="sr-only" onChange={(e) => setPolicyFile(e.target.files?.[0] ?? null)} />
                {policyFile ? (
                  <>
                    <FileText className="h-6 w-6 text-primary" />
                    <span className="text-sm font-medium">{policyFile.name}</span>
                  </>
                ) : (
                  <>
                    <Upload className="h-6 w-6 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Tap to choose a file</span>
                  </>
                )}
              </div>
            </div>

            <div className="rounded-lg border border-border p-4">
              <label className="flex cursor-pointer items-start gap-3">
                <Checkbox checked={generateDraft} onCheckedChange={(c) => setGenerateDraft(c === true)} disabled={disabled} className="mt-0.5" />
                <div>
                  <p className="text-sm font-medium">Create a suggested privacy policy for me</p>
                  <p className="text-xs text-muted-foreground">
                    Based on your answers, aligned with DPDP rules. We will not check this draft automatically — only an uploaded policy is analyzed.
                  </p>
                </div>
              </label>
              {generateDraft && (
                <RadioGroup value={draftFormat} onValueChange={(v) => setDraftFormat(v as "docx" | "pdf")} className="mt-3 flex gap-4 pl-7">
                  <label className="flex items-center gap-2 text-sm">
                    <RadioGroupItem value="docx" /> Word document (.docx)
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <RadioGroupItem value="pdf" /> PDF file
                  </label>
                </RadioGroup>
              )}
            </div>
          </div>
        )}

        {error && <p className="text-sm text-destructive">{error}</p>}

        <div className="flex justify-between gap-2 pt-2">
          <Button variant="outline" onClick={() => { setError(null); setStep((s) => Math.max(0, s - 1)) }} disabled={disabled || step === 0}>
            <ChevronLeft className="mr-1 h-4 w-4" /> Back
          </Button>
          <Button onClick={handleNext} disabled={disabled}>
            {step === WIZARD_STEPS.length - 1 ? "Finish" : "Next"}
            {step < WIZARD_STEPS.length - 1 && <ChevronRight className="ml-1 h-4 w-4" />}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

function Field({ label, children, className }: { label: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={className}>
      <Label className="mb-1.5 block text-sm">{label}</Label>
      {children}
    </div>
  )
}

function SingleChoice<T extends string>({
  label,
  options,
  value,
  onChange,
  disabled,
}: {
  label: string
  options: { value: T; label: string; hint?: string }[]
  value: T
  onChange: (v: T) => void
  disabled?: boolean
}) {
  return (
    <div>
      <Label className="mb-2 block text-sm">{label}</Label>
      <RadioGroup value={value} onValueChange={(v) => onChange(v as T)} className="gap-2">
        {options.map((opt) => (
          <label key={opt.value} className="flex cursor-pointer items-start gap-2 rounded-md border border-border p-2.5 text-sm has-[:checked]:border-primary/40 has-[:checked]:bg-primary/5">
            <RadioGroupItem value={opt.value} className="mt-0.5" disabled={disabled} />
            <div>
              <span className="font-medium">{opt.label}</span>
              {opt.hint && <p className="text-xs text-muted-foreground">{opt.hint}</p>}
            </div>
          </label>
        ))}
      </RadioGroup>
    </div>
  )
}

function YesNoRow({
  label,
  value,
  onChange,
  disabled,
  hint,
}: {
  label: string
  value: "yes" | "no"
  onChange: (v: "yes" | "no") => void
  disabled?: boolean
  hint?: string
}) {
  return (
    <div>
      <Label className="mb-1 block text-sm">{label}</Label>
      {hint && <p className="mb-2 text-xs text-muted-foreground">{hint}</p>}
      <div className="flex gap-2">
        {YES_NO_OPTIONS.map((opt) => (
          <Button
            key={opt.value}
            type="button"
            size="sm"
            variant={value === opt.value ? "default" : "outline"}
            onClick={() => onChange(opt.value)}
            disabled={disabled}
          >
            {opt.label}
          </Button>
        ))}
      </div>
    </div>
  )
}

function ToggleRow({ label, checked, onCheckedChange, disabled }: { label: string; checked: boolean; onCheckedChange: (v: boolean) => void; disabled?: boolean }) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-border p-3">
      <Label>{label}</Label>
      <Switch checked={checked} onCheckedChange={onCheckedChange} disabled={disabled} />
    </div>
  )
}
