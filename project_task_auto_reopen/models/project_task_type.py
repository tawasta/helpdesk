from odoo import fields, models


class ProjectTaskType(models.Model):

    _inherit = "project.task.type"

    reopen = fields.Boolean(
        string="Re-open stage",
        default=False,
        help="When a new message is sent to a closed stage, "
        "move message to this stage.",
    )
