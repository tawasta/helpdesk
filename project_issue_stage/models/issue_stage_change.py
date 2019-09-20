# -*- coding: utf-8 -*-

# 1. Standard library imports:
from datetime import datetime

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class IssueStageChange(models.Model):

    # 1. Private attributes
    _name = 'project.issue.stage.change'
    _order = 'create_date DESC'

    # 2. Fields declaration
    old_stage_id = fields.Many2one(
        'project.task.type',
        string='Old stage',
    )
    new_stage_id = fields.Many2one(
        'project.task.type',
        string='New stage',
    )
    issue_id = fields.Many2one(
        'project.issue',
        string='Issue id',
    )
    issue_partner_id = fields.Many2one(
        comodel_name='res.partner',
        related='issue_id.partner_id',
    )
    issue_date = fields.Datetime(
        related='issue_id.date',
    )
    start_date = fields.Datetime(
        string='Start date',
        help='When stage was started',
    )
    end_date = fields.Datetime(
        string='End date',
        help='When stage ended',
    )
    hours = fields.Float(
        string='Hours',
        help='Duration of the stage',
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
