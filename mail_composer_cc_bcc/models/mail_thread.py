# Copyright 2023 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


def format_emails(partners):
    """
    Formats a list of res.partner records into email strings with names.
    Example: 'John Doe <john@example.com>, Jane <jane@example.com>'
    """
    return ", ".join(
        f'{partner.name} <{partner.email}>' if partner.name else partner.email
        for partner in partners if partner.email
    )


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    # ------------------------------------------------------------
    # MAIL.MESSAGE HELPERS
    # ------------------------------------------------------------

    def _get_message_create_valid_field_names(self):
        """
        Add cc and bcc field to create record in mail.mail.
        """
        field_names = super()._get_message_create_valid_field_names()
        field_names.update({"recipient_cc_ids", "recipient_bcc_ids"})
        return field_names

    # ------------------------------------------------------
    # NOTIFICATION API
    # ------------------------------------------------------

    def _notify_by_email_get_base_mail_values(self, message, additional_values=None):
        """
        Add cc, bcc addresses to mail.mail objects so that email can be sent to those addresses.
        """
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

        partners_bcc = context.get("partner_bcc_ids")
        if partners_bcc:
            res["recipient_bcc_ids"] = [(6, 0, [p.id for p in partners_bcc])]

        return res  # <- make sure this line is present

    def _notify_get_recipients(self, message, msg_vals, **kwargs):
        """
        Add cc, bcc recipients so they can be grouped with other recipients.
        """
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
        """
        Ensure all recipients, including CC/BCC, are grouped under the same customer notification group.
        """
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
        """
        Prevent CC/BCC from being added in system notification messages.
        """
        if message.message_type == "notification":
            self = self.with_context(skip_adding_cc_bcc=True)
        return super()._notify_thread(message, msg_vals, **kwargs)
