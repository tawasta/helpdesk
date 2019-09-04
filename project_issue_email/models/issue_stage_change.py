# -*- coding: utf-8 -*-
from odoo import fields, models


class IssueStageChange(models.Model):

    _inherit = 'project.issue.stage.change'

    issue_number = fields.Char(
        related='issue_id.issue_number',
    )
