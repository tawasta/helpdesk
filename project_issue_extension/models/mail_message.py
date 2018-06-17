# -*- coding: utf-8 -*-

# 1. Standard library imports:
import re

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, models, _
from odoo import SUPERUSER_ID

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class MailMessage(models.Model):

    # 1. Private attributes
    _inherit = 'mail.message'

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model
    def create(self, vals):
        """
        When creating an issue, autoreply to customer
        with a message, where the subject is updated to include
        issue number
        """
        model = vals.get('model')
        settings = None
        print "TÄMÄ ON MAIL.MESSAGE CREATE"
        if model and model == 'project.issue':
            issue = self.env[model].browse([vals['res_id']])

            if self._context.get('fetchmail_server_id'):
                fetchmail_server = self.env['fetchmail.server'].browse([self._context.get('fetchmail_server_id')])
                if fetchmail_server:
                    company_id = fetchmail_server.company_id.id
            else:
                company_id = self.env.user.company_id.id

            settings = self.env['project.issue.settings'].sudo().search([
                ('company_id', '=', company_id),
                ], limit=1)

            if 'subject' in vals and vals['subject'] and not re.match('.*[#][0-9]{5,6}.*', vals['subject']):

                # Add issue number to the first post
                vals['subject'] = _('Issue') + " #" + str(issue.issue_number) + ": " + vals['subject']

                # Send autoreply to customer
                if settings:
                    print "Uusi: %s" % (issue.id)
                    email_values = settings.email_issue_received.generate_email(issue.id)
                    vals['body'] = email_values['body']
                    vals['reply_to'] = settings.email_reply_to

                if issue.partner_id:
                    issue.message_subscribe([issue.partner_id.id])
            elif vals.get('message_type') == 'comment':
                # Reply to existing ticket by employee
                if settings:
                    email_values = settings.email_issue_received.generate_email(issue.id)
                    vals['subject'] = _('Issue') + " #" + issue.issue_number + ": " + issue.name
                    # vals['body'] = email_values['body']
                    vals['email_from'] = settings.email_reply_to
                    vals['reply_to'] = settings.email_reply_to
                # print "EXISTING TEMPLATE: %s" % (issue.id)
        # print "Updated vals:\n%s" % vals
        res = super(MailMessage, self).create(vals)

        return res

    # 7. Action methods

    # 8. Business methods
