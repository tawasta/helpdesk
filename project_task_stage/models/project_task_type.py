from odoo import fields, models


class ProjectTaskType(models.Model):

    _inherit = "project.task.type"

    website_label_class = fields.Selection(
        selection=[
            ("default", "Default"),
            ("primary", "Primary"),
            ("success", "Success"),
            ("info", "Info"),
            ("warning", "Warning"),
            ("danger", "Danger"),
        ],
        default="info",
        string="Bootstrap label class",
        help="Define label class (Bootstrap) to be used on frontend",
    )
    reopen = fields.Boolean(
        string="Re-open stage",
        default=False,
        help="When a new message is sent to a closed stage, "
        "move message to this stage.",
    )

    public_name = fields.Char(
        string="Stage public name",
        help="Stage public name, which is shown in portal to customer",
        translate=True,
    )
