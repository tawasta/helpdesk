# -*- coding: utf-8 -*-

# 1. Standard library imports:
import logging

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models, _

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


_logger = logging.getLogger(__name__)



class ProjectIssue(models.Model):

    # 1. Private attributes
    _inherit = 'project.issue'

    _sql_constraints = [
        ('issue_number', 'unique(issue_number)', _('This issue number is already in use.'))
    ]

    # 2. Fields declaration
    issue_number = fields.Char(
        string='Issue number',
        help='Number assigned to issue as identifier',
    )
    doc_count = fields.Integer(
        compute='_compute_attached_docs_count',
        string='Number of documents attached',
        help='Number of documents attached to this record',
    )
    description = fields.Html(
        string='Description',
    )
    stage_change_ids = fields.One2many(
        'project.issue.stage.change',
        'issue_id',
        string='Stage changes',
        readonly=True,
        help="Issue's stage changes",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_attached_docs_count(self):
        attachment = self.env['ir.attachment']
        for record in self:
            record.doc_count = attachment.search_count([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id),
            ])


    @api.multi
    def attachment_tree_view(self):
        """
        Issue's attachments
        """
        self.ensure_one()
        domain = [
            ('res_model', '=', self._name), ('res_id', 'in', self.ids),
        ]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,kanban,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached to the issues.</p><p>
                        Send messages or log internal notes with attachments to link
                        documents to issues.
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model
    def create(self, values):
        """
        Set issue number to issue
        """
        if not values.get('issue_number'):
            values['issue_number'] = self.env['ir.sequence'].sudo().next_by_code('project.issue')
        return super(ProjectIssue, self).create(values)


    @api.multi
    def write(self, values):
        """

        """
        stage_id = values.get('stage_id')
        # Create new line to stage change log
        if stage_id:
            print stage_id
            values['stage_change_ids'] = [(0, _, {'stage': stage_id})]
        return super(ProjectIssue, self).write(values)


    # 7. Action methods

    # 8. Business methods
    @api.model
    def _init_issue_numbers(self):
        """
        Initialize issue numbers when module is installed
        """
        issues = self.search([('issue_number', '=', False)])
        for issue in issues:
            issue.issue_number = self.env['ir.sequence'].next_by_code('project.issue')
            _logger.debug("Setting issue number for %s", issue.issue_number)
