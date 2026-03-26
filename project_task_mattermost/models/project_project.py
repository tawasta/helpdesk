from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    use_mattermost_hooks = fields.Boolean(
        default=False,
        copy=True,
        help="Trigger Mattermost hooks from tasks belonging to this project",
    )
    mattermost_hook_ids = fields.Many2many("mattermost.hook", string="Mattermost Hooks")

    mattermost_channel = fields.Char(
        help="Channel the message is posted to. Leave empty to use default",
    )
    mattermost_username = fields.Char(
        help="Username who posts the message to Mattermost. Leave empty to use default",
    )
    mattermost_icon_url = fields.Char(
        string="Mattermost Icon URL",
        help="Icon url to be used for posting the message. Leave empty to use default",
    )
