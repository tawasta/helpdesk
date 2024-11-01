from odoo import fields, models


class ProjectProject(models.Model):

    _inherit = "project.project"

    helpdesk_project = fields.Boolean(
        "Helpdesk project",
        help="Select this to tag the project as a helpdesk project",
        default=False,
    )
