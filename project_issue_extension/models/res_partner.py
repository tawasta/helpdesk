# -*- coding: utf-8 -*-

# 1. Standard library imports:
import re
from datetime import datetime
import pytz

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
        body_html = mail_message.body
        if mail_message and mail_message.model == 'project.issue' and mail_message.message_type != 'notification':
            issue = self.env[mail_message.model].browse(mail_message.res_id)
            settings = self.env['project.issue.settings'].sudo().search([
                ('company_id', '=', issue.company_id.id),
            ], limit=1)
            last_message = self.env['mail.message'].sudo().search([
                ('res_id', '=', issue.id),
                ('model', '=', 'project.issue'),
                ('message_type', '!=', 'notification'),
                ('id', '!=', mail_message_id),
            ], limit=1)
            email_values = dict()
            if last_message:
                # If previous message in thread - send issue reply template with body and last message
                email_values = settings.email_issue_reply.generate_email(issue.id)
                local = pytz.timezone('Europe/Helsinki')
                create_date = datetime.strftime(pytz.utc.localize(datetime.strptime(
                    last_message.create_date, '%Y-%m-%d %H:%M:%S')).astimezone(local), "%d.%m.%Y %H:%M:%S")
                body_html += "<div style='margin-top:30px;padding-left:40px;border-left:solid 3px #ccc;'>"
                body_html += "<h3>" + _("Previous message") + "</h3>"
                body_html += _("Author: ") + last_message.author_id.name + ", " + create_date
                body_html += "<br/>" + last_message.body + "</div>"
                body_html = email_values['body'].replace('#issuemessagebody', body_html)
            else:
                # Issue created - send issue received template
                email_values = settings.email_issue_received.generate_email(issue.id)
                body_html = email_values['body'].replace('#issuemessagebody', body_html)
            mail_values['body_html'] = body_html
        return super(ResPartner, self)._notify_send(body_html, subject, recipients, **mail_values)

    # 8. Business methods
