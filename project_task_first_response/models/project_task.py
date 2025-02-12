from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    date_reply = fields.Datetime(
        compute="_compute_date_reply",
        string="First reply date",
        copy=False,
        readonly=True,
        store=True,
    )
    working_hours_reply = fields.Float(
        compute="_compute_elapsed_reply",
        string="Working hours to reply",
        store=True,
        group_operator="avg",
    )
    working_days_reply = fields.Float(
        compute="_compute_elapsed_reply",
        string="Working days to reply",
        store=True,
        group_operator="avg",
    )

    def _message_post_after_hook(self, message, msg_vals):
        for record in self:
            if (
                not record.date_reply
                and message.message_type == "comment"
                and not message.subtype_id.internal
            ):
                # Record the first reply date to task
                record.date_reply = fields.Datetime.now()

        return super()._message_post_after_hook(message, msg_vals)

    def _compute_date_reply(self):
        # Compute first reply dates for existing tasks
        for record in self:
            if record.date_reply:
                # Nothing to do
                record.date_reply = record.date_reply
            else:
                replies = record.message_ids.filtered(
                    lambda r: r.message_type == "comment" and not r.subtype_id.internal
                )
                if replies:
                    record.date_reply = replies[-1].date
                else:
                    record.date_reply = False

    @api.depends("date_reply")
    def _compute_elapsed_reply(self):
        task_linked_to_calendar = self.filtered(
            lambda t: t.project_id.resource_calendar_id and t.create_date
        )
        for task in task_linked_to_calendar:
            dt_create_date = fields.Datetime.from_string(task.create_date)

            if task.date_reply:
                dt_date_reply = fields.Datetime.from_string(task.date_reply)
                duration_data = (
                    task.project_id.resource_calendar_id.get_work_duration_data(
                        dt_create_date, dt_date_reply, compute_leaves=True
                    )
                )
                task.working_hours_reply = duration_data["hours"]
                task.working_days_reply = duration_data["days"]
            else:
                task.working_hours_reply = 0.0
                task.working_days_reply = 0.0
