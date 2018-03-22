# -*- coding: utf-8 -*-

# 1. Standard library imports:
import logging

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, models, _

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


_logger = logging.getLogger(__name__)



class ProjectProject(models.Model):

    # 1. Private attributes
    _inherit = 'project.project'

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_attached_docs_count(self):
        """
        Add issues to project's attachments
        """
        Attachment = self.env['ir.attachment']
        for project in self:
            project.doc_count = Attachment.search_count([
                '|',
                '&',
                ('res_model', '=', 'project.project'), ('res_id', '=', project.id),
                '|',
                '&',
                ('res_model', '=', 'project.task'), ('res_id', 'in', project.task_ids.ids),
                '&',
                ('res_model', '=', 'project.issue'), ('res_id', 'in', project.issue_ids.ids),
            ])


    @api.multi
    def attachment_tree_view(self):
        """
        Add issues to project's attachments
        """
        self.ensure_one()
        domain = [
            '|',
            '&', ('res_model', '=', 'project.project'), ('res_id', 'in', self.ids),
            '|',
            '&',
            ('res_model', '=', 'project.task'), ('res_id', 'in', self.task_ids.ids),
            '&',
            ('res_model', '=', 'project.issue'), ('res_id', 'in', self.issue_ids.ids)
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
                        Documents are attached to the tasks and issues of your project.</p><p>
                        Send messages or log internal notes with attachments to link
                        documents to your project.
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
