# -*- coding: utf-8 -*-

# 1. Standard library imports:
from datetime import datetime

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models, _

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class ProjectIssue(models.Model):

    # 1. Private attributes
    _inherit = 'project.issue'

    # 2. Fields declaration
    stage_change_ids = fields.One2many(
        comodel_name='project.issue.stage.change',
        inverse_name='issue_id',
        string='Stage changes',
        readonly=True,
        help="Issue's stage changes",
    )
    # Remove thread tracking from fields that aren't needed
    kanban_state = fields.Selection(track_visibility=False)
    stage_id = fields.Many2one(track_visibility=False)
    project_id = fields.Many2one(track_visibility=False)
    stage_duration = fields.Float(
        string='Ongoing stage duration',
        compute='_compute_stage_duration',
    )
    time_open = fields.Float(
        string='Time open',
        compute='compute_time_open',
        store=True,
        help='Count how long the issue has been open (closed stages excluded), updates only when stage is changed.',
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
        datetime_format = '%Y-%m-%d %H:%M:%S'
        for record in self:
            if record.stage_change_ids:
                last_stage = record.stage_change_ids[0]
                last_end_date = datetime.strptime(
                    last_stage.create_date, datetime_format)
            else:
                last_end_date = datetime.strptime(record.create_date, datetime_format)
            difference = datetime.now() - last_end_date
            duration = difference.total_seconds() / 3600
            record.stage_duration = duration

    @api.multi
    @api.depends('stage_change_ids')
    def compute_time_open(self):
        for record in self:
            time_open = 0.00
            if record.create_date and not record.stage_change_ids:
                datetime_format = '%Y-%m-%d %H:%M:%S'
                difference = datetime.now() - datetime.strptime(record.create_date, datetime_format)
                time_open = difference.total_seconds() / 3600
            else:
                stage_changes = record.stage_change_ids.sorted(
                    key=lambda r: r.create_date, reverse=True)
                for stage_change in stage_changes:
                    # Don't calculate folded stage changes
                    if stage_change.old_stage_id.fold:
                        continue
                    time_open += stage_change.hours
            record.time_open = time_open

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.multi
    def write(self, values):
        """
        Add a new row to stage_change_ids, when stage is changed
        Reopen ticket / change stage if external user sends message
        """
        for record in self:
            closed = record.stage_id.fold or record.stage_id.closed
            if closed and values.get('message_follower_ids'):
                values['stage_id'] = self.env.ref(
                    'project_issue_stage.project_issue_stage_data_2').id
                # TODO: Issue reopened message removed for now to prevent recursion
                # Only post message for folded stages
                # msg_body = _("Re-opening issue due to a new message.")

                # msg = record.sudo().message_post(
                #     body=msg_body,
                #     message_type='comment',
                #     subtype='mail.mt_note',
                # )
                # msg.needaction_partner_ids = [record.user_id.partner_id.id]

            stage_id = values.get('stage_id')
            if stage_id:
                end_date = record.create_date
                if record.stage_change_ids:
                    end_date = record.stage_change_ids[0].end_date
                values['stage_change_ids'] = [(0, 0, {
                    'old_stage_id': record.stage_id.id,
                    'new_stage_id': stage_id,
                    'start_date': end_date,
                    'end_date': fields.Datetime.now(),
                    'hours': record.stage_duration,
                })]
                # Reset stage_duration
        return super(ProjectIssue, self).write(values)

    # 7. Action methods

    # 8. Business methods
