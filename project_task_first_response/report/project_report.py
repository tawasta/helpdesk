from odoo import fields, models


class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"

    date_reply = fields.Datetime(string="First reply date", readonly=True)
    working_days_reply = fields.Float(
        string="# Working Days to Reply",
        digits=(16, 2),
        readonly=True,
        group_operator="avg",
        help="Number of Working Days to reply to the task",
    )

    def _select(self):
        res = super()._select()

        res += ", t.working_days_reply as working_days_reply"

        return res
