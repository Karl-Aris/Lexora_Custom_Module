from odoo.addons.mail.models.mail_mail import format_emails, format_emails_raw, extract_rfc2822_addresses
from odoo import models


class MailMail(models.Model):
    _inherit = "mail.mail"

    def _prepare_outgoing_list(self, recipients_follower_status=None):
        res = super()._prepare_outgoing_list(recipients_follower_status=recipients_follower_status)

        is_out_of_scope = len(self.ids) > 1
        is_from_composer = self.env.context.get("is_from_composer", False)
        if is_out_of_scope or not is_from_composer:
            return res

        partners_cc_bcc = self.recipient_cc_ids + self.recipient_bcc_ids
        partner_to_ids = [r.id for r in self.recipient_ids if r not in partners_cc_bcc]
        partner_to = self.env["res.partner"].browse(partner_to_ids)

        email_to = format_emails(partner_to)
        email_to_raw = format_emails_raw(partner_to)
        email_cc = format_emails(self.recipient_cc_ids)
        email_bcc_list = [p.email for p in self.recipient_bcc_ids if p.email]

        new_res = []
        for m in res:
            if m.get("email_to"):
                rcpt_to = extract_rfc2822_addresses(m["email_to"][0])[0]
            elif m.get("email_cc"):
                rcpt_to = extract_rfc2822_addresses(m["email_cc"][0])[0]
            else:
                rcpt_to = None

            if not rcpt_to:
                continue

            m.update({
                "email_to": email_to,
                "email_to_raw": email_to_raw,
                "email_cc": email_cc,
            })

            if rcpt_to in email_bcc_list:
                m["headers"].update({"Bcc": rcpt_to})

            new_res.append(m)

        return new_res
