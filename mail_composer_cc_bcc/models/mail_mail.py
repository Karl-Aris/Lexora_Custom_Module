from odoo import fields, models, tools

from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses


def format_emails(partners):
    emails = [
        tools.formataddr((p.name or "", tools.email_normalize(p.email)))
        for p in partners
        if p.email
    ]
    return ", ".join(emails)


def format_emails_raw(partners):
    emails = [p.email for p in partners if p.email]
    return ", ".join(emails)


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
    
        partner_to = self.recipient_ids - self.recipient_cc_ids - self.recipient_bcc_ids
        email_to = format_emails(partner_to)
        email_to_raw = format_emails_raw(partner_to)
        email_cc = format_emails(self.recipient_cc_ids)
    
        recipients = []
    
        new_res = []
        for m in res:
            m.update(
                {
                    "email_to": email_to,
                    "email_to_raw": email_to_raw,
                    "email_cc": email_cc,
                }
            )
            # Split message if it's for a BCC recipient
            if self.recipient_bcc_ids:
                for bcc_partner in self.recipient_bcc_ids:
                    if not bcc_partner.email:
                        continue
                    bcc_msg = m.copy()
                    bcc_msg["email_to"] = tools.email_normalize(bcc_partner.email)
                    bcc_msg["headers"].update({"X-Odoo-Bcc": bcc_msg["email_to"]})
                    bcc_msg["is_bcc_split"] = True  # Optional flag for later
                    new_res.append(bcc_msg)
                    recipients.append(bcc_msg["email_to"])
            else:
                new_res.append(m)
                if m["email_to"]:
                    recipients.append(m["email_to"])
    
        self.env.context = {**self.env.context, "recipients": recipients}
    
        return new_res

