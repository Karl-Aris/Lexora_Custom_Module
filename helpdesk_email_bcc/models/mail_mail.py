from odoo import models, fields

class MailMail(models.Model):
    _inherit = 'mail.mail'

    email_bcc = fields.Char(string='BCC Emails')
