# -*- coding: utf-8 -*-

# 1. Standard library imports:
import os

# 2. Known third party imports:
from bs4 import BeautifulSoup

# 3. Odoo imports (openerp):
from odoo import http, _
from odoo.addons.website_project_issue.controllers.main import WebsiteAccount
from odoo.http import request

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class WebsiteAccount(WebsiteAccount):

    @http.route(
        ['/my/issues/create'],
        type='http',
        auth="user",
        website=True,
        methods=['POST'],
    )
    def create_issue(self, **post):
        """
        Route to create issues from website
        """
        current_user = http.request.env.user
        partner = current_user.partner_id
        if post:
            name = post.get('issue_name')
            # Parse HTML since description field is plain text
            description = BeautifulSoup(post.get('issue_summary'), 'lxml').text

            # Find issue project with incoming mail server and alias
            server_id = int(post.get('issue_email'))
            email_inbox = http.request.env['fetchmail.server'].sudo().browse(
                server_id).user.split('@')[0]
            project_id = http.request.env['project.project'].sudo().search([
                ('alias_name', '=', email_inbox),
            ], limit=1).id
            values = {
                'name': name,
                'description': description,
                'project_id': project_id,
                'partner_id': partner.id,
                'email_from': partner.email,
            }
            # Set default stage from project
            issue = http.request.env['project.issue'].sudo(current_user).create(values)
            issue.stage_id = issue.stage_find(project_id)

            # Add partner as follower
            notified_partner_ids = [partner.id]
            issue.message_subscribe(notified_partner_ids)

            # Check attachment isn't too big
            attachment = post.get('issue_attachment')
            attachment.seek(0, os.SEEK_END)
            file_size = attachment.tell()
            attachment.seek(0)
            attachment_list = [(attachment.filename, attachment.read())] \
                if attachment.filename != "" else None

            if file_size > 20 * 1024 * 1024:
                # File size too big
                return request.redirect('/my/issues')

            # Send message to the thread
            discussion_id = http.request.env.ref('mail.mt_comment').id
            issue.message_post(
                subject=_("Issue created"),
                message_type='comment',
                subtype_id=discussion_id,
                body=post.get('issue_summary'),
                partner_ids=notified_partner_ids,
                attachments=attachment_list,
            )
        return request.redirect('/my/issues')
