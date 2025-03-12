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
    previous_message_id = fields.Many2one(
        comodel_name="mail.message",
        string="Previous message",
        help="Previous message (in thread)",
        compute="_compute_previous_message",
    )

    def _compute_previous_message(self):
        """Search the message that precedes the latest message"""
        mail_message = self.env["mail.message"].sudo()

        for record in self:
            previous_message = mail_message.search(
                [
                    ("res_id", "=", record.id),
                    ("model", "=", self._name),
                    ("subtype_id.internal", "=", False),
                    ("message_type", "!=", "notification"),
                ],
                limit=1,
                offset=1,
            )

            record.previous_message_id = previous_message.id

    @api.model
    def create(self, vals):
        # Get default project from fetchmail server, if not supplied in vals
        ctx = self.env.context
        params = ctx.get("params", {})
        related_model = params.get("model")

        if related_model == "fetchmail.server" and not vals.get("project_id"):
            mail_server = self.env["fetchmail.server"].sudo().browse(params.get(("id")))

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

        subtype_xmlid = values.get("subtype_xmlid")
        internal = False

        # The "subtype_xmlid" won't work when using "with_template",
        # but internal notes rarely are done with template.
        # Posting an internal note with template would add blockquotes to internal note,
        # but will not expose any internal notes to external recipients.
        # It just adds unnecessary junk to internal notes
        if subtype_xmlid:
            subtype = self.env.ref(subtype_xmlid)
            # Set message as internal to avoid unnecessarily adding blockquotes
            if subtype.internal:
                internal = True

        if values.get("message_type") == "comment" and not internal:
            for message in self.message_ids:
                if (
                    message.message_type in ["comment", "email"]
                    and not message.subtype_id.internal
                ):
                    blockquote += _("From: {}<br/>").format(message.email_from)
                    blockquote += _("Date: {}<br/>".format(message.date))
                    # blockquote += _("Subject: {}<br/>".format(message.subject))
                    blockquote += _("{}<br/>".format(message.body))

                    # Dummy variable, if we want to implement this as an option
                    full_thread = False
                    if not full_thread:
                        # Just show the latest message to avoid bloating the thread
                        return

            if blockquote:
                blockquote = (
                    "<br/><blockquote "
                    "style='padding-right:0px; padding-left:5px; "
                    "border-left-color: #000; margin-left:5px; "
                    "margin-right:0px;border-left-width: 2px; "
                    "border-left-style:solid'>{}</blockquote>".format(blockquote)
                )

        return blockquote
