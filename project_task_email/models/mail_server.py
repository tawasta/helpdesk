from odoo import models


class MailServer(models.Model):

    _inherit = "ir.mail_server"

    def build_email(self, *args, **kwargs):
        """Override the sender if project has sender email"""

        values = kwargs

        if values.get("object_id"):
            res_id, res_model = values.get("object_id").split("-")

            if res_model == "project.task":
                # Only apply for project tasks
                record = self.env[res_model].browse([int(res_id)])

                if record.project_id.email_from:
                    # Override the sender address, if it is set
                    values["email_from"] = record.project_id.email_from
                    values["reply_to"] = record.project_id.email_from

        return super().build_email(*args, **values)
