# -*- coding: utf-8 -*-

# 1. Standard library imports:
from datetime import datetime
import pytz

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, models, _

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
    # TODO: Add this to mail template
    '''
    @api.model
    def _notify_send(self, body, subject, recipients, **mail_values):
        """
        Use email_template when sending emails from system.
        We do this here since we don't want change the actual mail.message's
        body, just the outgoing email's.

        @param body: message body
        @param subject: message subject
        @param recipients: message recipients
        @param mail_values: Additional mail values that are passed to super
        @return: super
        """
        mail_message_id = mail_values.get('mail_message_id', False)
        mail_message = self.env['mail.message'].browse(mail_message_id)
        body_html = mail_message.body
        if mail_message and mail_message.model == 'project.issue' and \
                mail_message.message_type != 'notification':
            issue = self.env[mail_message.model].browse(mail_message.res_id)
            settings = self.env['project.issue.settings'].sudo().search([
                ('company_id', '=', issue.company_id.id),
            ], limit=1)
            last_message = self.env['mail.message'].sudo().search([
                ('res_id', '=', issue.id),
                ('model', '=', 'project.issue'),
                ('subtype_id.internal', '=', False),
                ('message_type', '!=', 'notification'),
                ('id', '!=', mail_message_id),
            ], limit=1)

            if last_message:
                # If previous message in thread,
                # send issue reply template with body and last message
                email_values = settings.email_issue_reply.generate_email(issue.id)
                local = pytz.timezone('Europe/Helsinki')
                localized_time = pytz.utc.localize(datetime.strptime(
                    last_message.create_date, '%Y-%m-%d %H:%M:%S')).astimezone(local)
                create_date = datetime.strftime(localized_time, "%d.%m.%Y %H:%M:%S")
                body_html += "<div style='margin-top:30px;padding-left:40px;"
                body_html += "border-left:solid 3px #ccc;'>"
                body_html += "<h3>" + _("Previous message") + "</h3>"
                body_html += "<span style='margin-bottom:20px;color:#909090;'>" + _("Author: ")
                body_html += last_message.author_id.name + ", " + create_date
                body_html += "<br/>" + last_message.body + "</div>"
                body_html = email_values['body'].replace('#issuemessagebody', body_html)

            mail_values['body_html'] = body_html
        return super(ResPartner, self)._notify_send(body_html, subject, recipients, **mail_values)
    '''

    # 8. Business methods
