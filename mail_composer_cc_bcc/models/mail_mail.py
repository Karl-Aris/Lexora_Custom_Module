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

        if len(self.ids) > 1 or not self.env.context.get("is_from_composer"):
            return res

        partner_to_ids = [
            p.id for p in self.recipient_ids
            if p.id not in self.recipient_cc_ids.ids and p.id not in self.recipient_bcc_ids.ids
        ]
        partners_to = self.env["res.partner"].browse(partner_to_ids)

        email_to = format_emails(partners_to)
        email_to_raw = format_emails_raw(partners_to)
        email_cc = format_emails(self.recipient_cc_ids)
        bcc_emails = [tools.email_normalize(p.email) for p in self.recipient_bcc_ids if p.email]

        # Track final unique messages
        final_msgs = []
        used_recipients = set()

        # Update the original message (TO + CC)
        for msg in res:
            msg_to = extract_rfc2822_addresses(msg.get("email_to") or "")[0] if msg.get("email_to") else None
            msg_cc = extract_rfc2822_addresses(msg.get("email_cc") or "")[0] if msg.get("email_cc") else None
            base_rcpt = msg_to or msg_cc

            if base_rcpt and base_rcpt in bcc_emails:
                # Skip BCC messages from base set — handled separately below
                continue

            msg.update({
                "email_to": email_to,
                "email_to_raw": email_to_raw,
                "email_cc": email_cc,
            })

            final_msgs.append(msg)
            used_recipients.add(base_rcpt)

        # Now add one message per BCC recipient
        for bcc_email in bcc_emails:
            if not bcc_email or bcc_email in used_recipients:
                continue

            # Use first message as template
            base_msg = final_msgs[0].copy()
            base_msg.update({
                "email_to": bcc_email,
                "email_cc": "",
                "body": (
                    "<p style='color:gray; font-style:italic;'>🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply.</p>"
                    + base_msg.get("body", "")
                )
            })
            final_msgs.append(base_msg)
            used_recipients.add(bcc_email)

        return final_msgs
