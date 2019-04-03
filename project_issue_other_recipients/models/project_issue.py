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
            issue.message_subscribe(partner_ids=partner_ids)
        return issue

    @api.multi
    def write(self, values):
        """ Add other email recipients to followers when updated """
        if values.get('email_other_recipients') and values.get('email_other_recipients')[0][0] == 6:
            partner_ids = values.get('email_other_recipients')[0][2]
            self.message_subscribe(partner_ids=partner_ids)
        return super(ProjectIssue, self).write(values)

    # 7. Action methods

    # 8. Business methods
