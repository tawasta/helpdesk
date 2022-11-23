import logging

from odoo import _, api, fields, models

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

        # Overwrite subject
        values["subject"] = self.display_name

        blockquote = self._get_blockquote(values)
        if blockquote:
            values["body"] += blockquote

        res = super().message_post(
            *args,
            **values,
        )

        return res

    def message_post_with_template(self, template_id, **kwargs):
        values = kwargs

        # Overwrite subject
        values["subject"] = self.display_name

        blockquote = self._get_blockquote(values)
        if blockquote:
            values["body"] += blockquote

        return super().message_post_with_template(
            template_id,
            **values,
        )

    def _get_blockquote(self, values):
        blockquote = ""
        # subtype_xmlid won't work when using "with_template"
        # if values.get("subtype_xmlid") == 'mail.mt_comment':
        if values.get("message_type") == "comment":
            for message in self.message_ids:
                if (
                    message.message_type == "comment"
                    and not message.subtype_id.internal
                ):
                    blockquote += _("From: {}<br/>").format(message.email_from)
                    blockquote += _("Date: {}<br/>".format(message.date))
                    # blockquote += _("Subject: {}<br/>".format(message.subject))
                    blockquote += _("{}<br/>".format(message.body))
                    # Just show the latest message to avoid bloating the thread
                    break

            if blockquote:
                blockquote = (
                    "<br/><blockquote "
                    "style='padding-right:0px; padding-left:5px; "
                    "border-left-color: #000; margin-left:5px; "
                    "margin-right:0px;border-left-width: 2px; "
                    "border-left-style:solid'>{}</blockquote>".format(blockquote)
                )

        return blockquote
