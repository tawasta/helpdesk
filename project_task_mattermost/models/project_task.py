import logging

from odoo import _, api, fields, models
from odoo.tools import html2plaintext

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = "project.task"

    use_mattermost_hooks = fields.Boolean(related="project_id.use_mattermost_hooks")

    @api.model
    def create(self, values):
        res = super().create(values)
        if res.use_mattermost_hooks and not self.env.context.get(
            "bypass_mattermost_hooks"
        ):
            res.mattermost_task_created()
        return res

    def write(self, values):
        res = super().write(values)
        if not self.env.context.get("bypass_mattermost_hooks"):
            for record in self.filtered("use_mattermost_hooks"):
                if "user_id" in values:
                    record.mattermost_task_author_changed()
                if "stage_id" in values:
                    record.mattermost_task_stage_changed()
        return res

    @api.onchange("user_id")
    def onchange_user_id_hook(self):
        if not self.env.context.get("bypass_mattermost_hooks"):
            for record in self.filtered("use_mattermost_hooks"):
                record.mattermost_task_author_changed()

    def _message_post_after_hook(self, message, msg_vals):
        # Mattermost post on internal messages only
        if self.use_mattermost_hooks and message.message_type not in [
            "notification",
            "user_notification",
        ]:
            self.mattermost_task_comment_posted(message)
        return super(ProjectTask, self)._message_post_after_hook(message, msg_vals)

    def mattermost_get_url(self):
        """Generate url for related task"""
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        url = "%(base_url)s/web/#id=%(record_id)s&view_type=form&model=project.task" % {
            "base_url": base_url,
            "record_id": self.id,
        }
        return url

    def mattermost_post(self, hook, msg, project):
        _logger.info(
            _("Posting project mattermost hook %(hook_id)s:\n%(msg)s")
            % {"hook_id": hook, "msg": msg}
        )
        hook.sudo().post_mattermost(
            msg,
            channel=project.mattermost_channel,
            username=project.mattermost_username,
            icon_url=project.mattermost_icon_url,
            verify=False,
        )

    def mattermost_task_comment_posted(self, message):
        """Post task comment posted message"""
        function = "mattermost_task_comment_posted"
        hook = (
            self.env["mattermost.hook"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "project.task"),
                    ("function", "=", function),
                    ("company_id", "=", self.company_id.id),
                    ("hook", "!=", False),
                    ("id", "in", self.sudo().project_id.mattermost_hook_ids.ids),
                ],
                limit=1,
            )
        )
        if hook:
            msg = self._get_mattermost_task_comment_posted_content(message)
            self.mattermost_post(hook, msg, self.project_id)

    def mattermost_task_created(self):
        """Post task created message"""
        function = "mattermost_task_created"
        hook = (
            self.env["mattermost.hook"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "project.task"),
                    ("function", "=", function),
                    ("company_id", "=", self.company_id.id),
                    ("hook", "!=", False),
                    ("id", "in", self.sudo().project_id.mattermost_hook_ids.ids),
                ],
                limit=1,
            )
        )
        if hook and self.name:
            msg = self._get_mattermost_task_created_content()

            self.mattermost_post(hook, msg, self.project_id)

    def _get_mattermost_task_created_content(self):
        subject = "[%s](%s)" % (self.display_name, self.mattermost_get_url())
        msg = _(":incoming_envelope: A new task **{}**").format(subject)

        if self.partner_id:
            msg += _(" from **{}**").format(self.partner_id.display_name)

        msg += "\n"
        # Tags
        if self.tag_ids:
            msg += "\n{}".format(", ".join(self.tag_ids.mapped("name")))
        # Priority
        priority = int(self.priority)
        if priority > 0:
            msg += "\n"
        for _i in range(priority):
            # Add star icons depending on the priority
            msg += ":star:"
        # Description
        if self.description:
            desc = html2plaintext(self.description).replace("\n", " ")
            dots = "..." if len(desc) > 300 else ""
            msg += "\n*{}{}*".format(desc[:300], dots)
        return msg

    def _get_mattermost_task_comment_posted_content(self, message):
        subject = "[%s](%s)" % (self.display_name, self.mattermost_get_url())
        if message.subtype_id and message.subtype_id.internal:
            msg = _("**{}** posted an internal comment on **{}**").format(
                message.author_id.display_name, subject
            )
        else:
            msg = _("**{}** posted a message on **{}**").format(
                message.author_id.display_name, subject
            )

        # Description
        if message.body:
            content = html2plaintext(message.body).replace("\n", " ")
            dots = "..." if len(content) > 300 else ""
            msg += "\n*{}{}*".format(content[:300], dots)
        return msg

    def mattermost_task_author_changed(self):
        """Post author changed message"""
        function = "mattermost_task_author_changed"
        hook = (
            self.env["mattermost.hook"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "project.task"),
                    ("function", "=", function),
                    ("company_id", "=", self.company_id.id),
                    ("hook", "!=", False),
                    ("id", "in", self.project_id.mattermost_hook_ids.ids),
                ],
                limit=1,
            )
        )
        if hook:
            subject = "[%s](%s)" % (self.display_name, self.mattermost_get_url())
            author = self.user_ids and self.user_ids[0].name or "No one"
            msg = _("**%(user)s** assigned **%(subject)s** to **%(author)s**") % {
                "user": self.write_uid.name,
                "subject": subject,
                "author": author,
            }
            self.mattermost_post(hook, msg, self.project_id)

    def mattermost_task_stage_changed(self):
        """Post stage changed message"""
        function = "mattermost_task_stage_changed"
        hook = (
            self.env["mattermost.hook"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "project.task"),
                    ("function", "=", function),
                    ("company_id", "=", self.company_id.id),
                    ("hook", "!=", False),
                    ("id", "in", self.project_id.mattermost_hook_ids.ids),
                ],
                limit=1,
            )
        )
        if hook:
            subject = "[%s](%s)" % (self.display_name, self.mattermost_get_url())
            msg = _("**%(user)s** changed **%(subject)s** stage to **%(stage)s**") % {
                "user": self.write_uid.name,
                "subject": subject,
                "stage": self.stage_id.display_name,
            }
            self.mattermost_post(hook, msg, self.project_id)

    def mattermost_task_summary(self):
        """Post summary of tasks"""
        function = "mattermost_task_summary"
        projects = (
            self.env["project.project"]
            .sudo()
            .search([("use_mattermost_hooks", "=", True)])
        )

        for project in projects:
            hooks = (
                self.env["mattermost.hook"]
                .sudo()
                .search(
                    [
                        ("res_model", "=", "project.task"),
                        ("function", "=", function),
                        ("company_id", "=", project.company_id.id),
                        ("hook", "!=", False),
                        ("id", "in", project.mattermost_hook_ids.ids),
                    ]
                )
            )

            stages = (
                self.env["project.task.type"]
                .sudo()
                .search([("project_ids", "=", project.id), ("is_closed", "=", False)])
            )
            for hook in hooks:
                msg = _("### Task summary for {}\n").format(project.name)
                total_count = 0
                msg += _("| Stage | Count |\n")
                msg += "|:------|:------|\n"
                for stage in stages:
                    count = (
                        self.env["project.task"]
                        .sudo()
                        .search_count(
                            [
                                ("project_id", "=", project.id),
                                ("stage_id", "=", stage.id),
                            ]
                        )
                    )
                    total_count += count
                    msg += "|%s| **%s**|\n" % (stage.name, count)
                total_string = _("Total count")
                msg += "|**%s**| **%s**\n" % (total_string, total_count)

                self.mattermost_post(hook, msg, project)
