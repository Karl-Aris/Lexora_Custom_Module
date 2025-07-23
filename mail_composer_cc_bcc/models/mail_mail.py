import re
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

        mail = self[0]

        bcc_partners = mail.recipient_bcc_ids
        cc_partners = mail.recipient_cc_ids
        all_cc_bcc = cc_partners + bcc_partners

        to_partners = mail.recipient_ids.filtered(lambda p: p not in all_cc_bcc)

        email_to = format_emails(to_partners)
        email_to_raw = format_emails_raw(to_partners)
        email_cc = format_emails(cc_partners)

        base_msg = res[0] if res else {}
        original_body = base_msg.get("body", "")

        # Main message for To and CC (clean, no BCC)
        clean_msg = base_msg.copy()
        clean_msg.update({
            "email_to": email_to,
            "email_to_raw": email_to_raw,
            "email_cc": email_cc,
            "email_bcc": "",
            "body": original_body,
            "recipient_ids": [(6, 0, (to_partners + cc_partners).ids)],
        })

        result = [clean_msg]

        # Separate message for each BCC recipient
        for partner in bcc_partners:
            if not partner.email:
                continue

            bcc_email = tools.email_normalize(partner.email)

            bcc_msg = base_msg.copy()
            bcc_msg.update({
                "headers": {
                    **base_msg.get("headers", {}),
                    "X-Odoo-Bcc": bcc_email,
                },
                "email_to": partner.email,
                "email_to_raw": partner.email,
                "email_cc": email_cc,
                "email_bcc": "",
                "recipient_ids": [(6, 0, [partner.id])],
            })

            # Inject special context for composer to append BCC notice
            bcc_msg["context"] = {
                **bcc_msg.get("context", {}),
                "is_from_composer": True,
                "force_bcc_partner_id": partner.id,
            }

            result.append(bcc_msg)

        return result
