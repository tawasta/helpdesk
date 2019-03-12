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
    _rec_name = 'stage'
    _order = 'create_date DESC'

    # 2. Fields declaration
    stage = fields.Many2one(
        'project.task.type',
        'New stage',
    )
    issue_id = fields.Many2one(
        'project.issue',
        string='Issue id',
    )
    hours = fields.Float(
        string='Hours',
        compute='_compute_hours',
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.multi
    def _compute_hours(self):
        """
        Compute how long task was in the previous state
        """
        all_records = self.sorted(key=lambda stage_change: stage_change.create_date, reverse=True)
        datetime_format = '%Y-%m-%d %H:%M:%S'
        previous_record = False
        for record in all_records:
            this_date = datetime.strptime(record.create_date, datetime_format)
            if not previous_record:
                previous_record = record
                previous_date = datetime.now()
            else:
                previous_date = datetime.strptime(previous_record.create_date, datetime_format)
            difference = previous_date - this_date
            record.hours = difference.total_seconds() / 3600

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
