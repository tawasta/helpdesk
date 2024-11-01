from odoo import fields, models


class ProjectTaskType(models.Model):

    _inherit = "project.task.type"

    reopen = fields.Boolean(
        string="Re-open stage",
        default=False,
        help="When a new message is sent to a closed stage, "
        "move message to this stage.",
    )

    is_closed = fields.Boolean('Closing Stage', help="Tasks in this stage are considered as closed.")
