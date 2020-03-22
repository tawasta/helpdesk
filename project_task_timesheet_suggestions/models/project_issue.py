import logging
from odoo import api, fields, models


_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):

    _inherit = 'project.task'

    suggested_message = fields.Char(
        string='Suggested message',
        compute='_compute_suggested_message',
        help='Task display name timesheet message as suggestion',
    )
    suggested_time = fields.Float(
        string='Suggested time',
        compute='_compute_suggested_time',
        help='Suggested time for a timesheet record based on stage changes',
    )

    @api.multi
    def _compute_suggested_message(self):
        """
        Compute suggested message to timesheet record
        """
        for rec in self:
            partner_name = rec.partner_id.commercial_partner_id.name
            msg = "{}, {}: ".format(rec.display_name, partner_name)
            rec.suggested_message = msg

    @api.multi
    def _compute_suggested_time(self):
        """
        Compute suggested time to timesheet record
        """
        for rec in self:
            rec.suggested_time = rec.stage_duration
