import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):

    _inherit = "project.task"

    issue_type = fields.Char(
        string="Issue type",
        help="How issue was created",
        readonly=True,
    )

    @api.model
    def create(self, vals):

        # Get default project from fetchmail server, if not supplied in vals
        fetchmail_server_id = self.env.context.get(
            "fetchmail_server_id"
        ) or self.env.context.get("default_fetchmail_server_id")

        if fetchmail_server_id and not vals.get("project_id"):
            mail_server = (
                self.env["fetchmail.server"].sudo().browse(fetchmail_server_id)
            )

            if mail_server.project_id:
                vals["project_id"] = mail_server.project_id.id or False
                vals["company_id"] = mail_server.project_id.company_id.id or False

        return super().create(vals)

    # 8. Business methods
    @api.model
    def message_new(self, msg, custom_values=None):
        """
        This method is called, when a new issue is starting from an email

        @param msg: message payload json
        @param custom_values: dict of values
        @return: issue id
        """
        defaults = {
            "issue_type": "email",
            "description": msg.get("body"),
        }
        if custom_values:
            defaults.update(custom_values)
        res = super().message_new(msg, custom_values=defaults)

        if not res.description:
            res.description = msg.get("body", False)

        return res

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, *args, **kwargs):

        values = kwargs

        # Overwrite values
        values["subject"] = self.display_name
        values["email_layout_xmlid"] = "project_task_email.mail_notification_helpdesk"

        if self.project_id.email_from:
            values["email_from"] = self.project_id.email_from

        res = super().message_post(
            *args,
            **values,
        )

        if self.project_id.email_from:
            # Change the author
            if self.env.user.partner_id.email:
                res.email_from = self.env.user.partner_id.email
            res.author_id = self.env.user.partner_id.id

        return res

    def message_post_with_template(self, template_id, **kwargs):
        values = kwargs

        # Overwrite values
        values["subject"] = self.display_name
        values["email_layout_xmlid"] = "project_task_email.mail_notification_helpdesk"

        if self.project_id.email_from:
            values["email_from"] = self.project_id.email_from

        return super().message_post_with_template(
            template_id,
            **values,
        )
