from odoo import fields, models, tools
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses


def format_emails(partners):
    return ", ".join([
        tools.formataddr((p.name or "", tools.email_normalize(p.email)))
        for p in partners if p.email
    ])


def format_emails_raw(partners):
    return ", ".join([p.email for p in partners if p.email])


class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char("Bcc", help="Blind Cc message recipients")

    def _prepare_outgoing_list(self, recipients_follower_status=None):
        res = super()._prepare_outgoing_list(recipients_follower_status=recipients_follower_status)

        if len(self.ids) > 1 or not self.env.context.get("is_from_composer", False):
            return res

        # Compute email addresses
        partners_cc_bcc = self.recipient_cc_ids + self.recipient_bcc_ids
        partner_to_ids = [
            r.id for r in self.recipient_ids
            if r.id not in self.recipient_cc_ids.ids and r.id not in self.recipient_bcc_ids.ids
        ]
        partner_to = self.env["res.partner"].browse(partner_to_ids)
        email_to = format_emails(partner_to)
        email_to_raw = format_emails_raw(partner_to)
        email_cc = format_emails(self.recipient_cc_ids)
        bcc_emails = [tools.email_normalize(p.email) for p in self.recipient_bcc_ids if p.email]

        # Clean original messages
        normal_recipients = set()
        new_res = []

        for m in res:
            recipient_email = None
            if m.get("email_to"):
                recipient_email = extract_rfc2822_addresses(m["email_to"])[0]
            elif m.get("email_cc"):
                recipient_email = extract_rfc2822_addresses(m["email_cc"])[0]

            if recipient_email in bcc_emails:
                continue  # skip original BCC message

            if recipient_email:
                normal_recipients.add(recipient_email)

            m.update({
                "email_to": email_to,
                "email_to_raw": email_to_raw,
                "email_cc": email_cc,
            })
            new_res.append(m)

        # Save base set to avoid modifying while iterating
        base_res = list(new_res)

        for bcc_email in bcc_emails:
            for m in base_res:
                new_msg = m.copy()
                # Add BCC notice only once
                body = m.get("body", "")
                if "🔒 You received this email as a BCC" not in body:
                    body = (
                        "<p style='color:gray; font-style:italic;'>🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply.</p>"
                        + body
                    )
                new_msg.update({
                    "email_to": bcc_email,
                    "email_cc": "",
                    "body": body,
                })
                new_res.append(new_msg)

        self.env.context = {
            **self.env.context,
            "recipients": list(normal_recipients | set(bcc_emails))
        }

        # Deduplicate final list based on recipient
        seen = set()
        final_res = []
        for m in new_res:
            email = m.get("email_to") or m.get("email_cc") or m.get("email_bcc")
            if isinstance(email, list):
                email = email[0]
            if email and email not in seen:
                seen.add(email)
                final_res.append(m)

        return final_res
