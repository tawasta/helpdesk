# -*- coding: utf-8 -*-

# 1. Standard library imports:

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

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.multi
    def write(self, values):
        """
        Add a new row to stage_change_ids, when stage is changed
        """
        stage_id = values.get('stage_id')
        # Create new line to stage change log
        if stage_id:
            values['stage_change_ids'] = [(0, _, {'stage': stage_id})]
        for record in self:
            if record.stage_id.fold and 'message_follower_ids' in values:
                # Reopen ticket / change stage if external user sends message
                # message_post has 'message_follower_ids' key in values
                latest_message = record.message_ids.sorted(
                    key=lambda r: r.create_date, reverse=True)[0]
                author = self.env['res.users'].search([
                    ('partner_id', '=', latest_message.author_id.id)
                ])
                if not author or (author and not author.has_group('base.group_user')):
                    values['stage_id'] = self.env.ref('project_issue_stage.project_issue_stage_data_2').id
                    msg_body = _("Re-opening issue due to a new message.")
                    record.sudo().message_post(
                        body=msg_body,
                        message_type='comment',
                        subtype='mail.mt_note',
                    )
        return super(ProjectIssue, self).write(values)

    # 7. Action methods

    # 8. Business methods
