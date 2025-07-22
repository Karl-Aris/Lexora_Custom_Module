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
        partner_to_ids = [
            r.id for r in self.recipient_ids
            if r.id not in self.recipient_cc_ids.ids and r.id not in self.recipient_bcc_ids.ids
        ]
        partner_to = self.env["res.partner"].browse(partner_to_ids)
        email_to = format_emails(partner_to)
        email_to_raw = format_emails_raw(partner_to)
        email_cc = format_emails(self.recipient_cc_ids)
        bcc_emails = [p.email for p in self.recipient_bcc_ids if p.email]

        normal_recipients = set()
        base_msg = None
        new_res = []

        for m in res:
            recipient_email = None
            to_addr = m.get("email_to", "")
            cc_addr = m.get("email_cc", "")

            to_addrs = extract_rfc2822_addresses(to_addr or "")
            cc_addrs = extract_rfc2822_addresses(cc_addr or "")
            recipient_email = (to_addrs + cc_addrs)[0] if (to_addrs + cc_addrs) else None

            if recipient_email in bcc_emails:
                continue

            if recipient_email:
                normal_recipients.add(recipient_email)

            m.update({
                "email_to": email_to,
                "email_to_raw": email_to_raw,
                "email_cc": email_cc,
            })
            base_msg = m
            new_res.append(m)

        # Generate separate emails for each BCC recipient
        for bcc_email in bcc_emails:
            if not bcc_email:
                continue
            new_msg = base_msg.copy()
            new_msg.update({
                "email_to": tools.email_normalize(str(bcc_email)),
                "email_cc": "",
                "body": (
                    "<p style='color:gray; font-style:italic;'>🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply.</p>"
                    + base_msg.get("body", "")
                ),
            })
            new_res.append(new_msg)

        self.env.context = {
            **self.env.context,
            "recipients": list(normal_recipients | set(bcc_emails))
        }

        # Deduplicate based on unique TO+CC combo (not just TO)
        unique_keys = set()
        final_res = []

        for m in new_res:
            to = m.get("email_to") or ""
            cc = m.get("email_cc") or ""
            key = f"{to}|{cc}"
            if key not in unique_keys:
                unique_keys.add(key)
                final_res.append(m)

        return final_res
