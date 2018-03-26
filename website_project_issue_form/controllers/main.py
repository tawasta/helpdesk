# -*- coding: utf-8 -*-

# 1. Standard library imports:
import os
import json
import logging

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
        @return: status message
        """
        current_user = http.request.env.user
        partner = current_user.partner_id
        values = dict()

        if post:
            # Validate form fields
            errors = self.issue_form_validate(post)
            _logger.info("Creating issue with values:\n%s" % (post))
            if errors:
                values['error'] = _('An error occured!')
            else:
                name = post.get('issue_name')
                description = post.get('issue_summary')

                # Find issue project with incoming mail server and alias
                server_id = int(post.get('issue_email'))
                email_inbox = http.request.env['fetchmail.server'].sudo().browse(
                    server_id).user.split('@')[0]
                project_id = http.request.env['project.project'].sudo().search([
                    ('alias_name', '=', email_inbox),
                ], limit=1).id
                issue_values = {
                    'name': name,
                    'description': description,
                    'project_id': project_id,
                    'partner_id': partner.id,
                    'email_from': partner.email,
                    'user_id': None,
                }

                # Check attachment isn't too big
                attachment = post.get('issue_attachment') or None
                max_size = http.request.env['ir.config_parameter'].get_param(
                    'website_project_issue_extension.attachment_max_size')
                attachment_list = None
                if attachment:
                    attachment.seek(0, os.SEEK_END)
                    file_size = attachment.tell()
                    attachment.seek(0)
                    attachment_list = [(attachment.filename, attachment.read())] \
                        if attachment and attachment.filename != "" else None

                    if file_size > max_size * 1000 * 1000:
                        # File size too big
                        values['error'] = _('An error occured!')
                        return json.dumps(values)
                # Set default stage from project
                issue = http.request.env['project.issue'].sudo(current_user).create(issue_values)
                issue.stage_id = issue.stage_find(project_id)
                values['id'] = issue.id
                values['name'] = issue.name
                values['stage'] = issue.stage_id.name
                values['issue_number'] = issue.issue_number

                # Add partner as follower
                notified_partner_ids = [partner.id]
                issue.message_subscribe(notified_partner_ids)

                # Send message to the thread
                subtype_id = http.request.env.ref('mail.mt_comment').id
                issue.message_post(
                    subject=_("Issue created"),
                    message_type='comment',
                    subtype_id=subtype_id,
                    body=post.get('issue_summary'),
                    partner_ids=notified_partner_ids,
                    attachments=attachment_list,
                )
                values['msg'] = _("New issue created!")
        return json.dumps(values)
