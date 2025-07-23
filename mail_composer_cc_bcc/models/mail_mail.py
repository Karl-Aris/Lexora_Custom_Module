from odoo import fields, models, tools
from copy import deepcopy


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

        mail = self[0]

        bcc_partners = mail.recipient_bcc_ids
        cc_partners = mail.recipient_cc_ids
        to_partners = mail.recipient_ids - cc_partners - bcc_partners

        email_to = format_emails(to_partners)
        email_to_raw = format_emails_raw(to_partners)
        email_cc = format_emails(cc_partners)

        # Instead of reusing res[0], build a clean base message dict
        base_msg = {
            "subject": mail.subject,
            "body": mail.body_html or "",
            "email_from": mail.email_from,
            "reply_to": mail.reply_to,
            "mail_server_id": mail.mail_server_id.id,
            "auto_delete": mail.auto_delete,
            "model": mail.model,
            "res_id": mail.res_id,
            "headers": mail.headers or {},
            "attachments": [(4, att.id) for att in mail.attachment_ids],
            "scheduled_date": mail.scheduled_date,
            "email_cc": email_cc,
            "email_bcc": "",
            "email_to": email_to,
            "email_to_raw": email_to_raw,
            "recipient_ids": [(6, 0, (to_partners + cc_partners).ids)],
        }

        result = [base_msg]

        for partner in bcc_partners:
            if not partner.email:
                continue

            bcc_note = (
                "<p style='color:gray; font-size:small;'>"
                "🔒 You received this email as a BCC (Blind Carbon Copy). "
                "Please do not reply to all.</p>"
            )

            bcc_msg = deepcopy(base_msg)
            bcc_msg.update({
                "headers": {**base_msg["headers"], "X-Odoo-Bcc": tools.email_normalize(partner.email)},
                "body": bcc_note + base_msg["body"],
                "recipient_ids": [(6, 0, [partner.id])],
            })

            result.append(bcc_msg)

        return result
