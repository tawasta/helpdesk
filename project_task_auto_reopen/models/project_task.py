import logging

from odoo import _, api, models, fields

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    # 1. Private attributes
    _inherit = "project.task"

    # 2. Fields declaration
    is_closed = fields.Boolean(
        related="stage_id.is_closed",
        string="Closing Stage",
        readonly=True,
        related_sudo=False,
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, *args, **kwargs):
        # Reopen the issue if a message is posted to a closed stage
        # TODO: Does this check work with portal?
        if kwargs.get("message_type") and kwargs.get("message_type") == "email":
            self._reopen()

        return super().message_post(
            *args,
            **kwargs,
        )

    def message_post_with_template(self, template_id, **kwargs):
        # Reopen the issue if a message is posted to a closed stage
        # TODO: Does this check work with portal?
        if kwargs.get("message_type") and kwargs.get("message_type") == "email":
            self._reopen()

        return super().message_post_with_template(
            template_id,
            **kwargs,
        )

    def _reopen(self):
        """
        Re-open the issue if a message is posted to a closed stage
        """

        for record in self:
            if not record.is_closed:
                # Task is not closed. Nothing to do
                continue
            reopen_stage = self.sudo()._get_reopen_stage()

            if not reopen_stage:
                # Reopen stage is not set. Nothing to do
                continue

            # Task is in a closed stage. Reopen it
            record.sudo().stage_id = reopen_stage.id
            # Post a message about stage change
            msg_body = _("Re-opening task due to a new message.")

            record.sudo().message_post(
                body=msg_body,
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )

    def _get_reopen_stage(self):
        self.ensure_one()

        task_types = self.project_id.type_ids
        reopen_stage = task_types.filtered("reopen")

        if len(reopen_stage) == 0:
            # No reopen stage
            _logger.warning(
                _("No reopen stage set for {}").format(self.project_id.name)
            )

        elif len(reopen_stage) > 1:
            # Multiple reopen stages
            _logger.warning(
                _("Multiple reopen stages for {}").format(self.project_id.name)
            )
            reopen_stage = reopen_stage[0]

        return reopen_stage
