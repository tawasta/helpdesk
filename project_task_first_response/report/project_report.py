from odoo import fields, models


class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"

    date_reply = fields.Datetime(
        string="First Reply Date",
        readonly=True,
    )

    working_days_reply = fields.Float(
        string="# Working Days to Reply",
        digits=(16, 2),
        readonly=True,
        aggregator="avg",
        help="Number of Working Days to reply to the task",
    )

    def _select(self):
        return super()._select() + """
            ,
            t.date_reply as date_reply,
            NULLIF(t.working_days_reply, 0) as working_days_reply
        """

    def _group_by(self):
        return super()._group_by() + """
            ,
            t.date_reply,
            t.working_days_reply
        """