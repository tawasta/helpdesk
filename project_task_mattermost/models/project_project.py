from odoo import fields, models


class ProjectProject(models.Model):

    _inherit = "project.project"

    use_mattermost_hooks = fields.Boolean(
        "Use Mattermost hooks",
        default=False,
        copy=True,
        help="Trigger Mattermost hooks from tasks belonging to this project",
    )
