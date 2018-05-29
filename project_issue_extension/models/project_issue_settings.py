# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class ProjectIssueSettings(models.Model):

    # 1. Private attributes
    _name = 'project.issue.settings'
    _description = "Project issue settings"

    # 2. Fields declaration
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        help='Company for which these settings are defined',
    )
    email_reply_to = fields.Char(
        string='Helpdesk reply to email address',
        size=256,
        help='Reply to email address for the company',
    )
    email_issue_received = fields.Many2one(
        'mail.template',
        string='Email template for autoreply',
        help='Auto reply email when customer submits a new issue',
    )
    email_issue_reply = fields.Many2one(
        'mail.template',
        string='Email template for new reply',
        help='When employee sends a new message from issue, this template is used',
    )
    helpdesk_project = fields.Many2one(
        'project.project',
        string='Helpdesk project',
        help='Currently used helpdesk project for the company',
    )
    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
