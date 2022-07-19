from odoo import _, api, fields, models
from odoo.tools import html2plaintext


class ProjectTask(models.Model):

    _inherit = "project.task"

    use_mattermost_hooks = fields.Boolean(related="project_id.use_mattermost_hooks")

    @api.model
    def create(self, values):
        res = super().create(values)
        if res.use_mattermost_hooks:
            res.mattermost_task_created()
        return res

    def write(self, values):
        res = super().write(values)
        for record in self.filtered("use_mattermost_hooks"):
            if "user_id" in values:
                record.mattermost_task_author_changed()
            if "stage_id" in values:
                record.mattermost_task_stage_changed()
        return res

    def mattermost_get_url(self):
        """Generate url for related task"""
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        url = "%(base_url)s/web/#id=%(record_id)s&view_type=form&model=project.task" % {
            "base_url": base_url,
            "record_id": self.id,
        }
        return url

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
                ],
                limit=1,
            )
        )
        if hook and self.name and self.partner_id:
            msg = self._get_mattermost_task_created_content()

            hook.sudo().post_mattermost(msg, verify=False)

    def _get_mattermost_task_created_content(self):
        subject = "[%s](%s)" % (self.display_name, self.mattermost_get_url())
        msg = _(
            ":incoming_envelope: A new task **%(subject)s** from **%(partner)s**\n"
        ) % {"subject": subject, "partner": self.partner_id.display_name}

        # Tags
        if self.tag_ids:
            msg += "\n{}".format(", ".join(self.tag_ids.mapped("name")))

        # Priority
        priority = int(self.priority)
        if priority > 0:
            msg += "\n"
        for i in range(priority):
            # Add star icons depending on the priority
            msg += ":star:"

        # Description
        desc = html2plaintext(self.description).replace("\n", " ")
        dots = "..." if len(desc) > 300 else ""
        msg += "\n*{}{}*".format(desc[:300], dots)

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
                ],
                limit=1,
            )
        )
        if hook:
            subject = "[%s](%s)" % (self.display_name, self.mattermost_get_url())
            author = self.user_id.name or "No one"
            msg = _("**%(user)s** assigned **%(subject)s** to **%(author)s**") % {
                "user": self.write_uid.name,
                "subject": subject,
                "author": author,
            }
            hook.sudo().post_mattermost(msg, verify=False)

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
            hook.sudo().post_mattermost(msg, verify=False)

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
                    ]
                )
            )

            stages = (
                self.env["project.task.type"]
                .sudo()
                .search(
                    [
                        ("project_ids", "=", project.id),
                    ]
                )
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
                hook.sudo().post_mattermost(msg, verify=False)
