# Sample documents for ClickComply testing

## Ideal DPDP-aligned privacy policy

| File | Purpose |
|------|---------|
| `ClickComply_Sample_DPDP_Privacy_Policy.pdf` | Upload this to the dashboard for a full compliance test |
| `ClickComply_Sample_DPDP_Privacy_Policy.md` | Editable source (same content) |

The sample policy is written for a fictional company (**Acme Digital Services Pvt Ltd**) and addresses all **16** automated compliance rules aligned with the **DPDP Act 2023** and **DPDP Rules 2025**, including:

- Itemised notice, consent, Consent Manager, legitimate uses  
- Security safeguards, retention/erasure, children's data, disability/guardian  
- Data principal rights, grievance (90-day), DPO contact, Board complaint  
- Breach notification (72-hour), cross-border transfer, Data Processors, SDF  

> **Not legal advice.** For production use, obtain qualified legal review.

## Regenerate the PDF

```bash
pip install fpdf2
python samples/generate_sample_pdf.py
```
