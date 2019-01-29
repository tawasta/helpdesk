# -*- coding: utf-8 -*-

# 1. Standard library imports:
import re

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models, _
from odoo import SUPERUSER_ID

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class ResPartner(models.Model):

    # 1. Private attributes
    _inherit = 'res.partner'

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    @api.model
    def _notify_send(self, body, subject, recipients, **mail_values):
        """
        Use email_template when sending emails from system.
        We do this here since we don't want change the actual mail.message's
        body, just the outgoing email's.
        """
        mail_message_id = mail_values.get('mail_message_id', False)
        mail_message = self.env['mail.message'].browse(mail_message_id)
        if mail_message and mail_message.model == 'project.issue':
            issue = self.env[mail_message.model].browse(mail_message.res_id)
            settings = self.env['project.issue.settings'].sudo().search([
                ('company_id', '=', issue.company_id.id),
            ], limit=1)
            email_values = settings.email_issue_reply.generate_email(issue.id)
            email_values['body'] = email_values['body'].replace('#body', mail_message.body)
            mail_values['body_html'] = email_values['body']
        return super(ResPartner, self)._notify_send(body, subject, recipients, **mail_values)

    # 8. Business methods
