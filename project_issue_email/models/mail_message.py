# -*- coding: utf-8 -*-
from odoo import api
from odoo import fields
from odoo import models
from odoo import SUPERUSER_ID


class MailMessage(models.Model):

    _inherit = 'mail.message'

    portal_message = fields.Boolean(
        string="Message was sent from portal",
        default=False,
        help="This field is used for sending issue comments through portal",
    )

    @api.model
    def create(self, vals):
        """
        Use issue subject in every message.
        """
        model = vals.get('model')
        if model and model == 'project.issue':
            issue = self.env[model].browse([vals['res_id']])

            # If this is the first message, use admin as author
            if not vals.get('parent_id'):
                vals['author_id'] = \
                    self.env['res.users'].browse([SUPERUSER_ID]).partner_id.id

            # Override subject, reply to and email server
            vals.update(issue.get_issue_autoreply_values(vals))

        res = super(MailMessage, self).create(vals)

        return res

    @api.multi
    def _notify(self, force_send=False, send_after_commit=True, user_signature=True):
        """
        TODO:
        Check if message is "issue received" and set force_send = True (now uses email queue)??
        """
        return super(MailMessage, self)._notify(force_send, send_after_commit, user_signature)

