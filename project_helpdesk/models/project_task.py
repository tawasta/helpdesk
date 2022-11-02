import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):

    _inherit = "project.task"

    helpdesk_project = fields.Boolean(related="project_id.helpdesk_project")

    def _message_create(self, values_list):
        if values_list.get("author_id") and values_list.get("subtype_id"):
            # search interal user for message author
            internal_user = self.env["res.users"].search(
                [
                    ("partner_id", "=", values_list.get("author_id")),
                    ("share", "=", False),
                ]
            )
            # only override default "Discussions" subtype
            if internal_user and values_list.get("subtype_id") == 1:
                values_list["subtype_id"] = self.env.ref(
                    "project_helpdesk.internal_user_discussions"
                ).id
                _logger.debug(
                    "Discussions subtype overriden by Internal User Discussions subtype."
                )
        return super(ProjectTask, self)._message_create(values_list)
