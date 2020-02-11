# -*- coding: utf-8 -*-

# 1. Standard library imports:
import logging
from datetime import datetime

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


_logger = logging.getLogger(__name__)


class ProjectIssue(models.Model):

    # 1. Private attributes
    _inherit = 'project.issue'

    # 2. Fields declaration
    suggested_message = fields.Char(
        'Suggested message',
        compute='_compute_suggested_message',
        help='Issue prefix to timesheet message as suggestion',
    )
    suggested_time = fields.Float(
        'Suggested time',
        compute='_compute_suggested_time',
        help='Suggested time for a timesheet record based on stage changes',
    )
    suggested_task_id = fields.Many2one(
        comodel_name='project.task',
        string='Suggested task',
        compute='_compute_suggested_task_id',
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.multi
    def _compute_suggested_message(self):
        """
        Compute suggested message to timesheet record
        """
        for rec in self:
            partner_name = rec.commercial_partner_id.name
            msg = "%s (#%s): " % (partner_name, rec.issue_code)
            rec.suggested_message = msg

    @api.multi
    def _compute_suggested_time(self):
        """
        Compute suggested time to timesheet record
        """
        for rec in self:
            if hasattr(rec, 'stage_change_ids'):
                # Sort the record set so we can be sure it will suggest the latest stage change
                stage_changes = rec.stage_change_ids.sorted(key=lambda r: r.create_date)
                if len(stage_changes) < 2:
                    continue
                rec.suggested_time = round(stage_changes[1].hours, 2)

    @api.multi
    def _compute_suggested_task_id(self):
        """
        Compute suggested task to timesheet record
        """
        project_task = self.env['project.task']
        for rec in self:
            rec.suggested_task_id = project_task.search([
                ('project_id', '=', rec.project_id.id),
                ('stage_id.sequence', '>', 1),
                ('stage_closed', '=', False),
            ], limit=1)

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
