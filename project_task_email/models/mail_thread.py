import logging

from odoo import api
from odoo import models


_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def message_process(
        self,
        model,
        message,
        custom_values=None,
        save_original=False,
        strip_attachments=False,
        thread_id=None,
    ):
        res = super().message_process(
            model, message, custom_values, save_original, strip_attachments, thread_id
        )

        fetchmail_server_id = self.env.context.get("default_fetchmail_server_id")
        if model == "project.task" and fetchmail_server_id:
            fetchmail_server = (
                self.env["fetchmail.server"].sudo().browse([fetchmail_server_id])
            )
            if fetchmail_server.project_id:
                task = self.env["project.task"].browse([res])
                vals = {
                    "project_id": fetchmail_server.project_id.id,
                    "company_id": fetchmail_server.project_id.company_id.id,
                }

                task.write(vals)

        return res
