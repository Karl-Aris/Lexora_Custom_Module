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
        res = super()._prepare_outgoing_list(recipients_follower_status=recipients_follower_status)
        is_out_of_scope = len(self.ids) > 1
        is_from_composer = self.env.context.get("is_from_composer", False)
    
        if is_out_of_scope or not is_from_composer:
            return res
    
        mail = self[0]
    
        # Prepare display values
        partners_cc_bcc = mail.recipient_cc_ids + mail.recipient_bcc_ids
        partner_to_ids = [r.id for r in mail.recipient_ids if r not in partners_cc_bcc]
        partner_to = self.env["res.partner"].browse(partner_to_ids)
    
        email_to = format_emails(partner_to)
        email_to_raw = format_emails_raw(partner_to)
        email_cc = format_emails(mail.recipient_cc_ids)
        bcc_partners = [p for p in mail.recipient_bcc_ids if p.email]
    
        bcc_emails = {tools.email_normalize(p.email) for p in bcc_partners}
    
        # ❌ Remove original BCC messages from default list
        filtered_res = []
        for m in res:
            rcpt_to = extract_rfc2822_addresses(m.get("email_to", "") or m.get("email_cc", ""))
            if rcpt_to and tools.email_normalize(rcpt_to[0]) in bcc_emails:
                continue  # skip original BCC version
            filtered_res.append(m)
    
        # ✅ Update first (main) message with To/Cc only
        base_msg = filtered_res[0] if filtered_res else {}
        base_msg.update({
            "email_to": email_to,
            "email_to_raw": email_to_raw,
            "email_cc": email_cc,
            "email_bcc": "",
        })
    
        result = [base_msg]
    
        # ✅ Append BCC version with note
        for partner in bcc_partners:
            bcc_msg = base_msg.copy()
            bcc_msg["headers"] = bcc_msg.get("headers", {})
            bcc_msg["headers"].update({"X-Odoo-Bcc": partner.email})
    
            bcc_note = (
                "<p style='color:gray; font-size:small;'>"
                "🔒 You received this email as a BCC (Blind Carbon Copy). "
                "Please do not reply to all.</p>"
            )
    
            bcc_msg["body"] = bcc_note + bcc_msg.get("body", "")
            bcc_msg["email_bcc"] = ""
            bcc_msg["recipient_ids"] = [(6, 0, [partner.id])]
    
            result.append(bcc_msg)
    
        return result

