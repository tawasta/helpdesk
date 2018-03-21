# -*- coding: utf-8 -*-

# 1. Standard library imports:
import json
import os
import logging
from datetime import datetime

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


    @http.route(
        ['/my/issues/<int:issue_id>'],
        type='http',
        auth="user",
        website=True,
    )
    def my_issues_issue(self, issue_id=None, **kw):
        """
        If unread messages, mark them as read as the user enters the page
        @param issue_id: ID of issue
        @param kw: kwargs
        @return: rendered template
        """
        current_user = http.request.env.user
        issue = request.env['project.issue'].browse(issue_id)
        if issue.message_needaction_counter > 0:
            messages = request.env['mail.message'].search([
                ('model', '=', issue._name),
                ('res_id', '=', issue.id),
                ('needaction', '=', True)
            ])
            _logger.debug("Reading messages: %s" % (messages.ids))
            messages.write({'needaction_partner_ids': [(3, current_user.partner_id.id)]})

        interval = request.env['ir.config_parameter'].get_param(
            'website_project_issue_extension.portal_polling_interval')
        values = {
            'issue': issue,
            'polling_interval': interval,
        }
        return request.render("website_project_issue.my_issues_issue", values)


    @http.route(
        ['/my/issues/<int:issue_id>/message'],
        type='http',
        auth="user",
        website=True,
        methods=['POST'],
    )
    def issue_message(self, issue_id=None, **post):
        """
        Route to send messages through ajax
        @param issue_id: id of issue
        @param post: Contains values of the issue form
        @return: status message
        """
        current_user = http.request.env.user
        issue = request.env['project.issue'].browse(issue_id)
        values = dict()

        if post:
            message = post.get('comment')

            if not message:
                values['error'] = _('Message is missing!')
                return json.dumps(values)

            # Check attachment isn't too big
            attachment = post.get('message_attachment') or None
            attachment_list = None
            if attachment:
                attachment.seek(0, os.SEEK_END)
                file_size = attachment.tell()
                attachment.seek(0)
                attachment_list = [(attachment.filename, attachment.read())] \
                    if attachment and attachment.filename != "" else None

                if file_size > 20 * 1024 * 1024:
                    # File size too big
                    values['error'] = _('File too big!')
                    return json.dumps(values)

            # Send message to the thread
            subtype_id = http.request.env.ref('mail.mt_comment').id
            issue.sudo(current_user).message_post(
                subject=_("Portal message"),
                message_type='comment',
                subtype_id=subtype_id,
                body=message,
                attachments=attachment_list,
            )
            values['msg'] = _("New message sent!")
        return json.dumps(values)


    @http.route(
        ['/my/issues/<int:issue_id>/update_message'],
        type='http',
        auth='user',
        methods=['GET'],
        csrf=True,
        website=True,
    )
    def update_message(self, issue_id=None, timestamp=None, **post):
        """
        Returns only the newest messages, that have been created after timestamp.
        @param issue_id: ID of issue
        @param timestamp: Timestamp when the last messages were retrieved
        @return message_html: Rendered message
        """
        values = dict()
        current_user = http.request.env.user
        messages_html = ""
        issue = request.env['project.issue'].browse(issue_id)

        if issue and timestamp:
            # Fetch only new messages
            timestamp = timestamp.split('.')[0]
            timestamp_date = str(datetime.fromtimestamp(int(timestamp)))
            new_messages = http.request.env['mail.message'].sudo(current_user).search([
                ('model', '=', 'project.issue'),
                ('res_id', '=', issue.id),
                ('date', '>', timestamp_date)
            ])
            if new_messages:
                # The submessage types that we are interested in
                values['message_subtype_id'] = http.request.env.ref('mail.mt_comment').id

                for message in new_messages:
                    values['message'] = message
                    messages_html += request.render(
                        "website_project_issue_extension.single_message_template",
                        values,
                        lazy=False,
                    )
        return messages_html
