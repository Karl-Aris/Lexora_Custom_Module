from odoo.tools.mail import formataddr

def _prepare_outgoing_list(self, recipients_follower_status=None):
    res = super()._prepare_outgoing_list(recipients_follower_status=recipients_follower_status)

    if len(self.ids) > 1 or not self.env.context.get("is_from_composer", False):
        return res

    partners_cc_bcc = self.recipient_cc_ids + self.recipient_bcc_ids
    partner_to_ids = [r.id for r in self.recipient_ids if r not in partners_cc_bcc]
    partner_to = self.env["res.partner"].browse(partner_to_ids)

    email_to = format_emails(partner_to)
    email_to_raw = format_emails_raw(partner_to)
    email_cc_raw = format_emails_raw(self.recipient_cc_ids)
    bcc_emails = [p.email for p in self.recipient_bcc_ids if p.email]

    new_res = []
    base_msg = res[0] if res else {}
    body_content = base_msg.get("body") or self.body_html or ""

    # 1. BCC: dump.lexora@gmail.com receives the normal email (with TO/CC visible)
    for bcc_email in bcc_emails:
        normal_msg = base_msg.copy()
        normal_msg.update({
            "email_to": bcc_email,
            "email_cc": email_to,
            "email_bcc": '',
            "body": body_content,
            "message_id": make_msgid(domain='bcc.lexora.local'),  # ensure uniqueness
        })
        new_res.append(normal_msg)

    # 2. TO: areglado291995@gmail.com receives the fake BCC message
    for to_email in email_to_raw:
        bcc_note_msg = base_msg.copy()
        bcc_note_msg.update({
            "email_to": to_email,
            "email_cc": '',
            "email_bcc": '',
            "body": (
                "<p style='color:gray; font-style:italic;'>"
                "🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply.</p>"
                + body_content
            ),
            "message_id": make_msgid(domain='to.lexora.local'),
        })
        new_res.append(bcc_note_msg)

    # 3. CC: dump.lexora@gmail.com receives the same BCC-style message
    for cc_email in email_cc_raw:
        cc_msg = base_msg.copy()
        cc_msg.update({
            "email_to": cc_email,
            "email_cc": '',
            "email_bcc": '',
            "body": (
                "<p style='color:gray; font-style:italic;'>"
                "🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply.</p>"
                + body_content
            ),
            "message_id": make_msgid(domain='cc.lexora.local'),
        })
        new_res.append(cc_msg)

    self.env.context = {
        **self.env.context,
        "recipients": email_to_raw + email_cc_raw + bcc_emails,
    }

    _logger.info("Final outgoing list:")
    for msg in new_res:
        _logger.info("TO: %s | CC: %s | BCC: %s", msg["email_to"], msg["email_cc"], msg["email_bcc"])

    return new_res
