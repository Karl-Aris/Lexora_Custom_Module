from odoo import fields, models, tools
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses


def format_emails(partners):
    return ", ".join([
        tools.formataddr((p.name or "", tools.email_normalize(p.email)))
        for p in partners if p.email
    ])


class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char("Bcc", help="Blind Cc message recipients")

    def _prepare_outgoing_list(self, recipients_follower_status=None):
        res = super()._prepare_outgoing_list(recipients_follower_status=recipients_follower_status)

        if len(self.ids) != 1 or not self.env.context.get("is_from_composer"):
            return res

        mail = self[0]
        recipient_to = mail.recipient_ids - mail.recipient_cc_ids - mail.recipient_bcc_ids
        recipient_cc = mail.recipient_cc_ids
        recipient_bcc = mail.recipient_bcc_ids

        display_to = format_emails(recipient_to)
        display_cc = format_emails(recipient_cc)
        bcc_emails = [tools.email_normalize(p.email) for p in recipient_bcc if p.email]

        final_msgs = []

        # Step 1: Standard message to To/Cc
        base_msg = res[0].copy()
        base_msg.update({
            "email_to": display_to,
            "email_cc": display_cc,
            "email_bcc": "",  # Hide Bcc from visible message
        })
        final_msgs.append(base_msg)

        # Step 2: One email per BCC recipient
        for bcc_email in bcc_emails:
            if not bcc_email:
                continue

            partner = self.env['res.partner'].search([('email', '=', bcc_email)], limit=1)

            bcc_msg = base_msg.copy()
            # Insert BCC note at the top of the body
            note = (
                "<p style='color:gray; font-style:italic;'>"
                "🔒 You received this email as a BCC (Blind Carbon Copy). "
                "Please do not reply to all.</p>"
            )
            bcc_msg["body"] = note + base_msg.get("body", "")
            bcc_msg["email_to"] = display_to  # Keep original To header visible
            bcc_msg["email_cc"] = display_cc
            bcc_msg["email_bcc"] = ""  # Don't actually send with Bcc header
            if partner:
                bcc_msg["recipient_ids"] = [(6, 0, [partner.id])]
            final_msgs.append(bcc_msg)

        return final_msgs
