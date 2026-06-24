export const DEFAULT_SUPPORT_EMAIL = "support@clickcomply.example"

export const SUPPORT_EMAIL =
  process.env.NEXT_PUBLIC_SUPPORT_EMAIL?.trim() || DEFAULT_SUPPORT_EMAIL

export const SUPPORT_MAILTO = `mailto:${SUPPORT_EMAIL}?subject=ClickComply%20support`

export const FAQ_ITEMS = [
  {
    id: "upload-format",
    question: "What can I upload for review?",
    answer:
      "A privacy policy in PDF or DOCX (max file size set by your server). Only your uploaded policy is analyzed, not the optional suggested draft.",
  },
  {
    id: "refresh-keep",
    question: "How do I save a review?",
    answer:
      "Tick Keep on a review to save it. Unchecked reviews are removed when you refresh or close the page. Keep your policy file handy if you need to upload again.",
  },
  {
    id: "questionnaire",
    question: "Why fill in the questionnaire first?",
    answer:
      "Your answers decide which India DPDP Act rules apply to your business (e.g. consent, children, cross-border storage). The check only runs against rules that match your situation.",
  },
  {
    id: "draft-vs-upload",
    question: "Should I use the suggested policy draft?",
    answer:
      "The DOCX/PDF draft is optional and is not legal advice. Download it if helpful, but upload your own published or lawyer-reviewed policy when you want a compliance check.",
  },
  {
    id: "analysis-time",
    question: "How long does a check take, and can I stop it?",
    answer:
      "Each applicable rule is reviewed one by one, so it can take a few minutes. Use Stop check on the Results panel while a review is running. You can re-run after it finishes.",
  },
] as const

export const WELCOME_SECTIONS = [
  {
    title: "What ClickComply does",
    body: "Answer a short questionnaire about your company, upload your privacy policy, and get an automated check against India’s DPDP Act rules that apply to you.",
  },
  {
    title: "Before you start, have ready",
    bullets: [
      "Your privacy policy as a PDF or DOCX file",
      "Company name, website, and privacy contact email",
      "Grievance officer name (required under DPDP for many businesses)",
    ],
  },
  {
    title: "Keep your reviews",
    body: "Tick Keep on a document to save it. Unchecked reviews are removed when you refresh or close the page.",
  },
] as const

export const WELCOME_SUBTITLE = "How ClickComply works"
