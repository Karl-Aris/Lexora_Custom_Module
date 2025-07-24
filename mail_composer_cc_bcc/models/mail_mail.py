from odoo import fields, models, tools
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses
import copy


def format_emails(partners):
    if not partners:
        return ""
    return ", ".join([
        tools.formataddr((p.name or "", tools.email_normalize(p.email)))
        for p in partners if p.email
    ])

def format_emails_raw(partners):
    if not partners:
        return ""
    return ", ".join([p.email for p in partners if p.email])



class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char("Bcc", help="Blind Cc message recipients")

    def _prepare_outgoing_list(self, recipients_follower_status=None):
        super_res = super()._prepare_outgoing_list(recipients_follower_status=recipients_follower_status)

        # Only customize single mail from composer
        if len(self.ids) > 1 or not self.env.context.get("is_from_composer", False):
            return super_res

        mail = self[0]

        bcc_partners = mail.recipient_bcc_ids
        cc_partners = mail.recipient_cc_ids
        all_cc_bcc_ids = set(cc_partners.ids + bcc_partners.ids)

        to_partners = self.env["res.partner"].browse([
            p.id for p in mail.recipient_ids if p.id not in all_cc_bcc_ids
        ])

        email_to = format_emails(to_partners)
        email_to_raw = format_emails_raw(to_partners)
        email_cc = format_emails(cc_partners)

        # Always get a copy of the original body and headers
        base_msg = copy.deepcopy(super_res[0]) if super_res else {}
        original_body = base_msg.get("body", "")
        original_headers = copy.deepcopy(base_msg.get("headers", {}))

        # Override the message list — do NOT include base message!
        result = []

        # TO + CC Message
        if to_partners or cc_partners:
            to_cc_msg = copy.deepcopy(base_msg)
            to_cc_msg.update({
                "email_to": email_to,
                "email_to_raw": email_to_raw,
                "email_cc": email_cc,
                "email_bcc": "",  # hide bcc in this version
                "body": original_body,
                "headers": original_headers,
                "recipient_ids": [(6, 0, [p.id for p in to_partners + cc_partners])],
            })
            result.append(to_cc_msg)

        # BCC Messages (split per recipient)
        for partner in bcc_partners:
            if not partner.email:
                continue
        
            bcc_email = tools.email_normalize(partner.email)
            bcc_note = (
                "<p style='color:gray; font-size:small;'>"
                "🔒 You received this email as a BCC (Blind Carbon Copy). "
                "Please do not reply to all.</p>"
            )
            bcc_body = bcc_note + original_body
        
            bcc_msg = copy.deepcopy(base_msg)
            bcc_msg.update({
                # 🚨 Only send to the BCC partner directly
                "email_to": bcc_email,
                "email_to_raw": bcc_email,
                "email_cc": "",
                "email_bcc": "",  # Hide bcc field
                "body": bcc_body,
                "headers": {
                    **original_headers,
                    "X-Odoo-Bcc": bcc_email,
                },
                "recipient_ids": [(6, 0, [partner.id])],
            })
            result.append(bcc_msg)
