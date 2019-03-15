# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, models, _

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class ProjectIssue(models.Model):

    # 1. Private attributes
    _inherit = 'project.issue'

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model
    def create(self, values):
        res = super(ProjectIssue, self).create(values)
        res.mattermost_issue_created()
        return res

    @api.multi
    def write(self, values):
        res = super(ProjectIssue, self).write(values)
        for record in self:
            if 'user_id' in values:
                record.mattermost_issue_author_changed()
            if 'stage_id' in values:
                record.mattermost_issue_stage_changed()
        return res

    # 7. Action methods
    def mattermost_get_url(self):
        """ Generate url for related issue """
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        url = "%(base_url)sweb/#id=%(record_id)s&view_type=form&model=project.issue" \
              % {'base_url': base_url, 'record_id': self.id}
        return url

    def mattermost_issue_created(self):
        """ Post issue created message """
        function = 'mattermost_issue_created'
        hook = self.env['mattermost.hook'].search([
            ('res_model', '=', 'project.issue'),
            ('function', '=', function),
        ], limit=1)
        if hook and self.name and self.partner_id:
            subject = "[%s](%s)" % (self.name, self.mattermost_get_url())
            msg = _(':incoming_envelope: A new issue **%(subject)s** from **%(partner)s**') \
                % {'subject': subject, 'partner': self.partner_id.display_name}
            hook.post_mattermost(msg, verify=False)

    def mattermost_issue_author_changed(self):
        """ Post author changed message """
        function = 'mattermost_issue_author_changed'
        hook = self.env['mattermost.hook'].search([
            ('res_model', '=', 'project.issue'),
            ('function', '=', function),
        ], limit=1)
        if hook:
            subject = "[%s](%s)" % (self.name, self.mattermost_get_url())
            author = self.user_id.name or 'No one'
            msg = _('**%(user)s** assigned **%(subject)s** to **%(author)s**') \
                % {'user': self.write_uid.name, 'subject': subject, 'author': author}
            hook.post_mattermost(msg, verify=False)

    def mattermost_issue_stage_changed(self):
        """ Post stage changed message """
        function = 'mattermost_issue_stage_changed'
        hook = self.env['mattermost.hook'].search([
            ('res_model', '=', 'project.issue'),
            ('function', '=', function),
        ], limit=1)
        if hook:
            subject = "[%s](%s)" % (self.name, self.mattermost_get_url())
            msg = _('**%(user)s** changed **%(subject)s** stage to **%(stage)s**') \
                % {'user': self.write_uid.name, 'subject': subject, 'stage': self.stage_id.name}
            hook.post_mattermost(msg, verify=False)

    def mattermost_summary(self):
        """ Post summary of issues """
        function = 'mattermost_summary'
        helpdesk_settings = self.env['project.issue.settings'].sudo().search([])
        for setting in helpdesk_settings:
            hooks = self.env['mattermost.hook'].sudo().search([
                ('res_model', '=', 'project.issue'),
                ('function', '=', function),
                ('company_id', '=', setting.company_id.id)
            ])
            stages = self.env['project.task.type'].sudo().search([
                ('fold', '=', False),
                ('issue_stage', '=', True),
            ])
            for hook in hooks:
                msg = _('### Issue summary\n')
                total_count = 0
                msg += _('| Stage | Count |\n')
                msg += '|:------|:------|\n'
                for stage in stages:
                    count = self.env['project.issue'].sudo().search_count([
                        ('project_id', '=', setting.project_id.id),
                        ('stage_id', '=', stage.id),
                    ])
                    total_count += count
                    msg += '|%s| **%s**|\n' % (stage.name, count)
                total_string = _('Total count')
                msg += '|**%s**| **%s**\n' % (total_string, total_count)
                hook.sudo().post_mattermost(msg, verify=False)

    # 8. Business methods
