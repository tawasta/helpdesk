from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class ProjectTaskPortalAccessUpdater(models.TransientModel):
    _name = "project.task.portal.access.updater"
    _description = "Task Portal User Update Wizard"

    line_ids = fields.One2many(
        "project.task.portal.access.updater.line", "wizard_id", string="Task Lines"
    )

    @api.model
    def default_get(self, fields_list):
        """Prepopulate the wizard with all of the tasks, their current portal
        users, and suggestions who the portal users should be."""
        res = super().default_get(fields_list)
        active_ids = self.env.context.get("active_ids", [])
        if not active_ids:
            return res

        task_lines = []
        portal_group = self.env.ref("base.group_portal")

        tasks = self.env["project.task"].browse(active_ids)

        if any(task.helpdesk_project for task in tasks):
            raise ValidationError(
                _("This tool is intended for project tasks, not helpdesk tickets.")
            )

        for task in tasks:
            current_users = task.allowed_portal_user_ids
            assignees = task.user_ids.filtered(lambda u: portal_group in u.groups_id)
            followers = task.message_partner_ids.mapped("user_ids")
            portal_followers = followers.filtered(lambda u: portal_group in u.groups_id)

            suggested_users = (current_users | assignees | portal_followers).filtered(
                lambda u: portal_group in u.groups_id
            )

            task_lines.append(
                (
                    0,
                    0,
                    {
                        "task_id": task.id,
                        "current_user_ids": [(6, 0, current_users.ids)],
                        "suggested_user_ids": [(6, 0, suggested_users.ids)],
                        "to_apply": True,
                    },
                )
            )

        res["line_ids"] = task_lines
        return res

    def action_confirm(self):
        """Save changes to the portal users field according to the wizard lines data"""

        for line in self.line_ids.filtered("to_apply"):
            task = line.task_id

            task.allowed_portal_user_ids = [(6, 0, line.suggested_user_ids.ids)]
            _logger.info(
                "Adding the following portal users to task %s: %s "
                % (
                    task.code,
                    ", ".join(user.partner_id.name for user in line.suggested_user_ids),
                )
            )

        return {"type": "ir.actions.act_window_close"}


class ProjectTaskPortalAccessUpdaterLine(models.TransientModel):
    _name = "project.task.portal.access.updater.line"
    _description = "Task Portal User Update Line Wizard"

    wizard_id = fields.Many2one(
        "project.task.portal.access.updater", required=True, ondelete="cascade"
    )
    task_id = fields.Many2one("project.task", string="Task")
    current_user_ids = fields.Many2many(
        "res.users",
        relation="task_access_updater_res_user_current_rel",
        string="Current Portal Users with Access",
    )
    suggested_user_ids = fields.Many2many(
        "res.users",
        relation="task_access_updater_res_user_suggested_rel",
        string="Suggested Portal Users to Add",
    )
    to_apply = fields.Boolean("Apply", default=True)
