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
        """
        model = vals.get('model')
        real_author = False
        if model and model == 'project.issue':
            # Use subject saved to issue as subject of all messages
            issue = self.env[model].browse([vals['res_id']])
            real_author = vals.get('author_id')
            if not real_author:
                real_author = issue.partner_id.id
            vals.update(issue.get_issue_autoreply_values(vals))
        print "------- MAIL MESSAGE VALS -------"
        print vals
        res = super(MailMessage, self).create(vals)
        if model and model == 'project.issue':
            res.author_id = real_author
        return res

    # 7. Action methods
    @api.multi
    def _notify(self, force_send=False, send_after_commit=True, user_signature=True):
        """
        TODO:
        Check if message is "issue received" and set force_send = True (now uses email queue)??
        """
        print "MENIKÖ TÄNNEKIN??!?"
        return super(MailMessage, self)._notify(force_send, send_after_commit, user_signature)

    # 8. Business methods
