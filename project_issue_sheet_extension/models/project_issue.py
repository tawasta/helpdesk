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
        compute='compute_suggested_message',
        help='Issue prefix to timesheet message as suggestion',
    )
    suggested_time = fields.Float(
        'Suggested time',
        compute='compute_suggested_time',
        help='Suggested time for a timesheet record based on stage changes',
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.multi
    def compute_suggested_message(self):
        """
        Compute suggested message to timesheet record
        """
        for rec in self:
            partner_name = rec.partner_id.parent_id.name or rec.partner_id.name
            msg = "%s (#%s): " % (partner_name, rec.issue_code)
            rec.suggested_message = msg

    @api.multi
    def compute_suggested_time(self):
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

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
