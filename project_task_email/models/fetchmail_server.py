from odoo import models
from odoo import fields


class FetchmailServer(models.Model):

    _inherit = "fetchmail.server"

    # Allow creating new tasks directly to a project
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Related project',
        help='Create task to project',
    )

    # Helper for XML conditions
    object_model = fields.Char(
        related='object_id.model',
    )
