# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, models, fields

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class ProjectIssue(models.Model):

    # 1. Private attributes
    _inherit = 'project.issue'

    # 2. Fields declaration
    email_other_recipients = fields.Many2many(
        'res.partner',
        string="Email other recipients",
        help="Other recipients to emails"
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model
    def create(self, vals):
        """ Add other recipients to followers when issue created """
        issue = super(ProjectIssue, self).create(vals)
        if vals.get('email_other_recipients') and vals.get('email_other_recipients')[0][0] == 6:
            partner_ids = vals.get('email_other_recipients')[0][2]
            issue.message_subscribe(partner_ids)
        return issue

    @api.multi
    def write(self, values):
        """ Add other email recipients to followers when updated """
        if values.get('email_other_recipients') and values.get('email_other_recipients')[0][0] == 6:
            partner_ids = values.get('email_other_recipients')[0][2]
            self.message_subscribe(partner_ids)
        return super(ProjectIssue, self).write(values)

    # 7. Action methods
    @api.multi
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, subtype=None, **kwargs):
        """
        Ensure that inbox email addresses are removed from followers
        before every message_post.
        """
        self.ensure_one()
        self._remove_inbox()
        return super(ProjectIssue, self).message_post(subtype=subtype, **kwargs)

    def update_other_recipients(self, message_dict):
        """ Update other recipients accordingly """
        email_list = self.email_split(message_dict)
        partner_ids = filter(None, self._find_partner_from_emails(email_list, force_create=True))
        self.message_subscribe(partner_ids)
        inbox_ids = self._remove_inbox()
        # Other recipients (msg['to']) and CCs (msg['cc']) to other recipients
        if len(email_list) > 0:
            other_recipients = [partner_id for partner_id in partner_ids
                                if partner_id not in inbox_ids]
            other_recipients.extend(self.email_other_recipients.ids)
            self.email_other_recipients = [(6, 0, other_recipients)]

    def _remove_inbox(self):
        """ Remove inboxes from subscribers and other recipients """
        helpdesk_settings = self.env['project.issue.settings'].sudo().search([])
        inbox_emails = [setting.email_reply_to for setting in helpdesk_settings]
        inbox_ids = filter(None, self._find_partner_from_emails(inbox_emails))
        self.message_unsubscribe(inbox_ids)
        return inbox_ids

    # 8. Business methods
