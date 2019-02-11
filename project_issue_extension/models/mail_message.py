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


class MailMessage(models.Model):

    # 1. Private attributes
    _inherit = 'mail.message'

    # 2. Fields declaration
    portal_message = fields.Boolean(
        string="Message was sent from portal",
        default=False,
        help="This field is used for sending issue comments through portal",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model
    def create(self, vals):
        """
        Use issue subject in every message.
        Send "Issue has been received" -message when issue created.
        """
        model = vals.get('model')
        if model and model == 'project.issue':
            # Use subject saved to issue as subject of all messages
            issue = self.env[model].browse([vals['res_id']])
            vals['subject'] = issue.subject
        res = super(MailMessage, self).create(vals)
        if model and model == 'project.issue' and not issue.issue_received_email:
            # If issue received message hasn't been send (first message), send it
            issue.send_issue_autoreply()
            issue.issue_received_email = True
        return res

    # 7. Action methods
    @api.multi
    def _notify(self, force_send=False, send_after_commit=True, user_signature=True):
        """ Add the related record followers to the destination partner_ids if is not a private message.
            Call mail_notification.notify to manage the email sending
        """
        print "MENIKÖ TÄNNEKIN??!?"
        return super(MailMessage, self)._notify(force_send, send_after_commit, user_signature)

    # 8. Business methods
