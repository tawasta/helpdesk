from odoo import api, models


class MailMessage(models.Model):

    _inherit = "mail.message"

    @api.model
    def create_removed(self, values):
        # REMOVED this due over-zealous parsing
        if (
            values.get("model") == "project.task"
            and values.get("body")
            and values.get("message_type") == "email"
        ):
            body = values.get("body")
            if body:
                # Remove everything after the first blockquote
                # This is really crude, but trims most of the excess content
                values["body"] = body.split("<blockquote", 1)[0]

        return super().create(values)
