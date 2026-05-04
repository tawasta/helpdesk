from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    date_reply = fields.Datetime(
        compute="_compute_date_reply",
        string="First Reply Date",
        copy=False,
        readonly=True,
        store=True,
    )
    working_hours_reply = fields.Float(
        compute="_compute_elapsed",
        string="Working Hours to Reply",
        store=True,
        aggregator="avg",
    )
    working_days_reply = fields.Float(
        compute="_compute_elapsed",
        string="Working Days to Reply",
        store=True,
        aggregator="avg",
    )

    def _message_post_after_hook(self, message, msg_vals):
        for task in self:
            if (
                not task.date_reply
                and message.message_type == "comment"
                and not message.subtype_id.internal
            ):
                task.date_reply = fields.Datetime.now()

        return super()._message_post_after_hook(message, msg_vals)

    @api.depends("message_ids", "message_ids.message_type", "message_ids.subtype_id")
    def _compute_date_reply(self):
        for task in self:
            if task.date_reply:
                task.date_reply = task.date_reply
                continue

            replies = task.message_ids.filtered(
                lambda message: (
                    message.message_type == "comment"
                    and not message.subtype_id.internal
                )
            )
            task.date_reply = replies[-1].date if replies else False

    @api.depends(
        "create_date",
        "date_assign",
        "date_end",
        "date_reply",
        "project_id.resource_calendar_id",
    )
    def _compute_elapsed(self):
        super()._compute_elapsed()
        tasks = self.filtered(
            lambda task: task.project_id.resource_calendar_id and task.create_date
        )
        for task in tasks:
            if not task.date_reply:
                task.working_hours_reply = 0.0
                task.working_days_reply = 0.0
                continue

            domain = [
                ("company_id", "in", task.project_id.company_id.ids),
                ("time_type", "=", "leave"),
            ]

            duration_data = task.project_id.resource_calendar_id.get_work_duration_data(
                fields.Datetime.from_string(task.create_date),
                fields.Datetime.from_string(task.date_reply),
                compute_leaves=True,
                domain=domain,
            )

            task.working_hours_reply = duration_data["hours"]
            task.working_days_reply = duration_data["days"]

        (self - tasks).update({
            "working_hours_reply": 0.0,
            "working_days_reply": 0.0,
        })