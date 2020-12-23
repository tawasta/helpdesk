from datetime import datetime
import logging
from odoo import api
from odoo import fields
from odoo import models
from odoo import _

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):

    # 1. Private attributes
    _inherit = "project.task"

    # 2. Fields declaration
    stage_change_ids = fields.One2many(
        comodel_name="project.task.stage.change",
        inverse_name="task_id",
        string="Stage changes",
        readonly=True,
        help="Task's stage changes",
    )
    # Remove thread tracking from fields that aren't needed
    # kanban_state = fields.Selection(track_visibility=False)
    # stage_id = fields.Many2one(track_visibility=False)
    # project_id = fields.Many2one(track_visibility=False)
    stage_duration = fields.Float(
        string="Ongoing stage duration", compute="_compute_stage_duration",
    )
    time_open = fields.Float(
        string="Time open",
        compute="compute_time_open",
        store=True,
        help="Count how long the task has been open (closed stages excluded), updates only when stage is changed.",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.multi
    def _compute_stage_duration(self):
        """
        Compute ongoing stage duration:
        - In first stage, from create date to this moment
        - After that, always from previous stage ending date to this moment
        """
        for record in self:
            if record.stage_change_ids:
                last_stage = record.stage_change_ids[0]
                last_end_date = last_stage.create_date
            else:
                last_end_date = record.create_date
            difference = datetime.now() - last_end_date
            duration = difference.total_seconds() / 3600
            record.stage_duration = duration

    @api.multi
    @api.depends("stage_change_ids")
    def compute_time_open(self):
        for record in self:
            time_open = 0.00
            if record.create_date and not record.stage_change_ids:
                difference = datetime.now() - record.create_date
                time_open = difference.total_seconds() / 3600
            else:
                stage_changes = record.stage_change_ids.sorted(
                    key=lambda r: r.create_date, reverse=True
                )
                for stage_change in stage_changes:
                    # Don't calculate folded stage changes
                    if stage_change.old_stage_id.fold:
                        continue
                    time_open += stage_change.hours
            record.time_open = time_open

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
    @api.multi
    def _track_template(self, tracking):
        res = super(ProjectTask, self)._track_template(tracking)

        stage_change = self.env["project.task.stage.change"]

        # Stage was changed. Save a state change record
        for record in self:
            changes, tracking_value_ids = tracking[record.id]

            if "stage_id" not in changes:
                # Stage is not changed. Nothing else to do
                continue

            # Create stage change record
            start_date = record.create_date
            if record.stage_change_ids:
                start_date = record.stage_change_ids[0].end_date

            values = {
                "task_id": record.id,
                "start_date": start_date,
                "end_date": fields.Datetime.now(),
                "hours": record.stage_duration,
            }

            try:
                # Get the actual values
                tracking_dict = tracking_value_ids[0][2]
                values["old_stage_id"] = tracking_dict.get("old_value_integer")
                values["new_stage_id"] = tracking_dict.get("new_value_integer")
            except IndexError:
                # Didn't get tracking values
                # Nothing we can do here
                pass

            stage_change.create(values)

        return res

    @api.multi
    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, *args, **kwargs):

        # Reopen the issue if a message is posted to a closed stage
        # TODO: Does this check work with portal?
        if kwargs.get("message_type") and kwargs.get("message_type") == "email":
            self._reopen()

        return super(ProjectTask, self).message_post(*args, **kwargs,)

    @api.multi
    def message_post_with_template(self, template_id, **kwargs):

        # Reopen the issue if a message is posted to a closed stage
        # TODO: Does this check work with portal?
        if kwargs.get("message_type") and kwargs.get("message_type") == "email":
            self._reopen()

        return super(ProjectTask, self).message_post_with_template(
            template_id, **kwargs,
        )

    def _reopen(self):
        """
        Re-open the issue if a message is posted to a closed stage
        """

        for record in self:
            closed = record.stage_id.fold or record.stage_id.closed

            if not closed:
                # Task is not closed. Nothing to do
                continue

            reopen_stage = self._get_reopen_stage()

            if not reopen_stage:
                # Reopen stage is not set. Nothing to do
                continue

            # Task is in a closed stage. Reopen it
            record.stage_id = reopen_stage.id
            # Post a message about stage change
            msg_body = _("Re-opening task due to a new message.")

            msg = record.sudo().message_post(
                body=msg_body, message_type="comment", subtype="mail.mt_note",
            )

            if record.user_id:
                msg.needaction_partner_ids = [record.user_id.partner_id.id]

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
