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
        res = super()._prepare_outgoing_list(
            recipients_follower_status=recipients_follower_status
        )

        is_out_of_scope = len(self.ids) > 1
        is_from_composer = self.env.context.get("is_from_composer", False)

        if is_out_of_scope or not is_from_composer:
            return res

        # Prepare TO/CC headers
        partners_cc_bcc = self.recipient_cc_ids + self.recipient_bcc_ids
        partner_to_ids = [r.id for r in self.recipient_ids if r not in partners_cc_bcc]
        partner_to = self.env["res.partner"].browse(partner_to_ids)
        email_to = format_emails(partner_to)
        email_to_raw = format_emails_raw(partner_to)
        email_cc = format_emails(self.recipient_cc_ids)
        bcc_emails = [p.email for p in self.recipient_bcc_ids if p.email]

        normal_recipients = set()
        new_res = []

        for m in res:
            recipient_email = None

            if m.get("email_to"):
                recipient_email = extract_rfc2822_addresses(m["email_to"][0])[0]
            elif m.get("email_cc"):
                recipient_email = extract_rfc2822_addresses(m["email_cc"][0])[0]

            if recipient_email in bcc_emails:
                # Skip original bcc message – we will replace it below
                continue

            if recipient_email:
                normal_recipients.add(recipient_email)

            m.update({
                "email_to": email_to,
                "email_to_raw": email_to_raw,
                "email_cc": email_cc,
            })
            new_res.append(m)

        # Now generate separate emails for each BCC
        for bcc_email in bcc_emails:
            for m in res:
                # Create a copy to avoid mutating the original
                new_msg = m.copy()
                new_msg.update({
                    "email_to": bcc_email,
                    "email_cc": "",  # No CC for BCC recipients
                    "body": "<p style='color:gray; font-style:italic;'>🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply.</p>" + m.get("body", ""),
                })
                new_res.append(new_msg)

        self.env.context = {**self.env.context, "recipients": list(normal_recipients | set(bcc_emails))}

        return new_res
