# -*- coding: utf-8 -*-

# 1. Standard library imports:
import os
import json
import logging
import base64

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import http, _
from odoo.addons.website_project_issue.controllers.main import WebsiteAccount
from odoo.http import request

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

_logger = logging.getLogger(__name__)

class WebsiteAccount(WebsiteAccount):


    def issue_form_validate(self, values):
        """
        Validation for issue form
        """
        errors = False
        mandatory = [
            "name", "issue_email", "issue_summary"
        ]
        for key in values:
            if key in mandatory:
                value = values[key].strip()
                if not value:
                    errors = True
        return errors


    @http.route(
        ['/my/issues/create'],
        type='http',
        auth="user",
        website=True,
        methods=['POST'],
    )
    def create_issue(self, **post):
        """
        Route to create issues from website.
        This method is called with ajax.

        @param post: Contains values of the issue form
        @return: redirect
        """
        current_user = http.request.env.user
        partner = current_user.partner_id
        values = dict()
        error = False
        if post:
            # Validate form fields
            errors = self.issue_form_validate(post)
            _logger.debug("Creating issue with values:\n%s" % (post))
            if errors:
                values['error'] = _('An error occured!')
            else:
                name = post.get('issue_name')
                description = post.get('issue_summary')
                # Find issue project with incoming mail server and alias
                company_id = int(post.get('issue_email'))
                settings = http.request.env['project.issue.settings'].sudo().search([
                    ('company_id', '=', company_id)
                ])
                project_id = settings.helpdesk_project.id
                # Check attachment isn't too big
                attachment_ids = post.get('issue_attachments') or None
                max_size = http.request.env['ir.config_parameter'].get_param(
                    'website_project_issue_extension.attachment_max_size')
                if attachment_ids:
                    files_dict = dict(request.httprequest.files)
                    for attachment_file in files_dict['issue_attachments']:
                        attachment_file_value = attachment_file.value
                        attachment_file_value.seek(0, os.SEEK_END)
                        file_size = attachment_file_value.tell()
                        attachment_file_value.seek(0)
                        if file_size > max_size * 1000 * 1000:
                            # File size too big
                            error = True
                if not error:
                    issue_values = {
                        'name': name,
                        'description': description,
                        'project_id': project_id,
                        'partner_id': partner.id,
                        'email_from': partner.email,
                        'user_id': None,
                    }
                    issue = http.request.env['project.issue'].sudo(current_user).create(issue_values)
                    if attachment_ids:
                        files_dict = dict(request.httprequest.files)
                        for attachment_file in files_dict['issue_attachments']:
                            attachment_file_value = attachment_file.value
                            attachment_name = attachment_file_value.filename
                            attachment_data = attachment_file_value.read()
                            # Create attachment
                            attachment_data = {
                                'name': attachment_name,
                                'datas_fname': attachment_name,
                                'description': attachment_name,
                                'datas': base64.b64encode(str(attachment_data)),
                                'type': 'binary',
                                'res_name': issue.name,
                                'res_model': 'project.issue',
                                'res_id': issue.id,
                            }
                            http.request.env['ir.attachment'].sudo().create(attachment_data)
                    issue.stage_id = issue.stage_find(project_id)
        return request.redirect('/my/issues')
