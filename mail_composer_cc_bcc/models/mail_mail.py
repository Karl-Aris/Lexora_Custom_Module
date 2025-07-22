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
    
        if len(self.ids) > 1 or not self.env.context.get("is_from_composer"):
            return res
    
        partner_to_ids = [
            p.id for p in self.recipient_ids
            if p.id not in self.recipient_cc_ids.ids and p.id not in self.recipient_bcc_ids.ids
        ]
        partners_to = self.env["res.partner"].browse(partner_to_ids)
    
        email_to = format_emails(partners_to)
        email_cc = format_emails(self.recipient_cc_ids)
        bcc_emails = [tools.email_normalize(p.email) for p in self.recipient_bcc_ids if p.email]
    
        final_msgs = []
        seen_recipients = set()
    
        # TO + CC original message
        for msg in res:
            to_header_emails = extract_rfc2822_addresses(msg.get("email_to", ""))[0]
            if to_header_emails and to_header_emails in bcc_emails:
                continue
    
            msg.update({
                "email_to": email_to,
                "email_cc": email_cc,
            })
    
            final_msgs.append(msg)
            seen_recipients.update(extract_rfc2822_addresses(email_to)[0])
            seen_recipients.update(extract_rfc2822_addresses(email_cc)[0])
    
        # Now create messages for each BCC separately
        for bcc_email in bcc_emails:
            if not bcc_email or bcc_email in seen_recipients:
                continue
    
            base_msg = final_msgs[0].copy()
            base_msg.update({
                "email_to": bcc_email,
                "email_cc": "",
                "email_bcc": "",  # clear it so Odoo doesn't re-process
                "body": (
                    "<p style='color:gray; font-style:italic;'>🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply.</p>"
                    + base_msg.get("body", "")
                ),
                "headers": {
                    "To": email_to,
                    "Cc": email_cc,
                }
            })
    
            final_msgs.append(base_msg)
            seen_recipients.add(bcc_email)
    
        return final_msgs
