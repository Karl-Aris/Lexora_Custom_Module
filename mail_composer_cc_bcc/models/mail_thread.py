from odoo import models


def format_emails(partners):
    return ", ".join(
        f'{partner.name} <{partner.email}>' if partner.name else partner.email
        for partner in partners if partner.email
    )


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _get_message_create_valid_field_names(self):
        field_names = super()._get_message_create_valid_field_names()
        field_names.update({"recipient_cc_ids", "recipient_bcc_ids"})
        return field_names

    def _notify_by_email_get_base_mail_values(self, message, additional_values=None):
        res = super()._notify_by_email_get_base_mail_values(
            message, additional_values=additional_values
        )
        context = self.env.context
        skip_adding_cc_bcc = context.get("skip_adding_cc_bcc", False)
        if skip_adding_cc_bcc:
            return res

        partners_cc = context.get("partner_cc_ids")
        if partners_cc:
            res["recipient_cc_ids"] = [(6, 0, [p.id for p in partners_cc])]
            res["email_cc"] = format_emails(partners_cc)

        # Don't include email_bcc in the header; keep Bcc secret
        partners_bcc = context.get("partner_bcc_ids")
        if partners_bcc:
            res["recipient_bcc_ids"] = [(6, 0, [p.id for p in partners_bcc])]

        return res

    def _notify_send(self, message, msg_vals, notif_recipients, **kwargs):
        """
        Split notifications: one for To+Cc, and separate ones for each Bcc.
        """
        MailMail = self.env['mail.mail']
        notif_to_cc = []
        notif_bcc_map = {}

        for notif in notif_recipients:
            partner = notif['partner']
            if not partner.email:
                continue

            # Determine recipient role
            if 'partner_bcc_ids' in self.env.context and partner in self.env.context['partner_bcc_ids']:
                notif_bcc_map[partner.id] = notif
            else:
                notif_to_cc.append(notif)

        # Send mail to To + Cc in one email
        if notif_to_cc:
            self.with_context(bcc_mode=False)._notify_send_single_mail(
                message, msg_vals, notif_to_cc, **kwargs
            )

        # Send individual emails to Bcc (one by one)
        for notif in notif_bcc_map.values():
            partner = notif['partner']
            self.with_context(
                bcc_mode=True,
                bcc_recipient_id=partner.id,
                email_to=format_emails([partner]),
                email_cc="",  # no cc
            )._notify_send_single_mail(
                message, msg_vals, [notif], **kwargs
            )

    def _notify_send_single_mail(self, message, msg_vals, notif_recipients, **kwargs):
        """
        Compose a single mail.mail object and send it.
        Context must contain proper headers.
        """
        MailMail = self.env['mail.mail']
        mail_values = self._notify_by_email_get_base_mail_values(message)
        email_to = self.env.context.get("email_to")
        email_cc = self.env.context.get("email_cc")
        bcc_mode = self.env.context.get("bcc_mode", False)

        if not bcc_mode:
            to_emails = [p['partner'].email for p in notif_recipients if p['partner'].email]
            mail_values['email_to'] = ", ".join(to_emails)
            mail_values['email_cc'] = email_cc or ""
        else:
            mail_values['email_to'] = email_to or ""
            # Do NOT include Bcc in header fields

        mail_values['recipient_ids'] = [(6, 0, [p['partner'].id for p in notif_recipients])]

        # Create and send mail
        mail = MailMail.create(mail_values)
        mail.send()

    def _notify_get_recipients(self, message, msg_vals, **kwargs):
        ResPartner = self.env["res.partner"]
        MailFollowers = self.env["mail.followers"]
        rdata = super()._notify_get_recipients(message, msg_vals, **kwargs)
        context = self.env.context
        is_from_composer = context.get("is_from_composer", False)
        skip_adding_cc_bcc = context.get("skip_adding_cc_bcc", False)
        if not is_from_composer or skip_adding_cc_bcc:
            return rdata

        for pdata in rdata:
            pdata["type"] = "customer"

        partners_cc_bcc = context.get("partner_cc_ids", ResPartner)
        partners_cc_bcc += context.get("partner_bcc_ids", ResPartner)
        msg_sudo = message.sudo()
        message_type = msg_vals.get("message_type") if msg_vals else msg_sudo.message_type
        subtype_id = msg_vals.get("subtype_id") if msg_vals else msg_sudo.subtype_id.id

        recipients_cc_bcc = MailFollowers._get_recipient_data(
            None, message_type, subtype_id, partners_cc_bcc.ids
        )
        partners_already_included = {r.get("id") for r in rdata}

        for _, value in recipients_cc_bcc.items():
            for _, data in value.items():
                partner_id = data.get("id")
                if not partner_id or partner_id in partners_already_included:
                    continue

                notif = data.get("notif") or "email"
                pdata = {
                    "id": partner_id,
                    "active": data.get("active"),
                    "share": data.get("share"),
                    "notif": notif,
                    "type": "customer",
                    "is_follower": data.get("is_follower"),
                }
                rdata.append(pdata)

        return rdata

    def _notify_get_recipients_classify(self, message, recipients_data, model_description, msg_vals=None):
        res = super()._notify_get_recipients_classify(
            message, recipients_data, model_description, msg_vals=msg_vals
        )
        is_from_composer = self.env.context.get("is_from_composer", False)
        skip_adding_cc_bcc = self.env.context.get("skip_adding_cc_bcc", False)
        if not is_from_composer or skip_adding_cc_bcc:
            return res

        ids = []
        customer_data = None
        for rcpt_data in res:
            if rcpt_data["notification_group_name"] == "customer":
                customer_data = rcpt_data
            else:
                ids += rcpt_data["recipients"]

        if not customer_data:
            customer_data = res[0]
            customer_data["notification_group_name"] = "customer"
            customer_data["recipients"] = ids
        else:
            customer_data["recipients"] += ids

        return [customer_data]

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        if message.message_type == "notification":
            self = self.with_context(skip_adding_cc_bcc=True)
        return super()._notify_thread(message, msg_vals, **kwargs)
