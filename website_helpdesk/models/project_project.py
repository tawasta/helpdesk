from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    helpdesk_project = fields.Boolean(
        string='Support Ticket Project',
        help='Portal support ticket creation uses the first active project with this enabled.',
        tracking=True,
        copy=False,
    )
