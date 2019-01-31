# -*- coding: utf-8 -*-

# 1. Standard library imports:
import json
import os
import logging
from datetime import datetime
import re

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import http, _
from odoo.addons.website_project_issue.controllers.main import WebsiteAccount
from odoo.http import request

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

_logger = logging.getLogger(__name__)


def validate_follower_emails(emails):
    """
    Validate issue followers email format

    @param emails: Comma separated emails
    @return res: Dict of emails and info if error occured
    """
    res = dict()
    res['emails'] = re.sub(r"\s+", "", emails.lower())
    pat = re.compile(r"^(([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\,?)+$")
    if not pat.match(res['emails']):
        _logger.debug("Emails didn't match pattern: %s" % (res['emails']))
        res['error'] = True
    return res


def subscribe_issue_followers(issue, new_emails):
    """
    Add followers to issue and create partners if needed

    @param issue: Issue to which followers are added
    @param new_emails: Followers' emails to be added
    @return new_partners: List of new partners (id, email)
    """
    new_emails = new_emails.split(',')
    existing_emails = list()
    partners = request.env['res.partner'].sudo().search([
        ('email', 'in', new_emails)
    ])
    if partners:
        existing_emails = [partner.email for partner in partners]
    for email in new_emails:
        if email not in existing_emails:
            # Create partner and add it to recordset
            partner_values = {
                'name': email,
                'email': email,
            }
            partners += request.env['res.partner'].sudo().create(partner_values)
            _logger.debug("New partner (issue id: %s) created with email: %s" % (issue.id, email))
    issue.message_subscribe(partner_ids=partners.ids)
    return partners.search_read([('id', 'in', partners.ids)], ['email'])


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
        issue = request.env['project.issue'].search([('id', '=', issue_id)])
        if not issue:
            return request.render('website.404')
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
        # Get external followers
        follower_partners = [follower.partner_id.id for follower in issue.message_follower_ids]
        follower_users = request.env['res.users'].sudo().search([
            ('partner_id', 'in', follower_partners)
        ])
        employees = set([user.partner_id.id for user in follower_users if user.has_group('base.group_user')])
        external_partners = list(set(follower_partners) - employees)
        attachments = request.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'project.issue'),
            ('res_id', '=', issue.id),
        ])
        values = {
            'issue': issue,
            'polling_interval': interval,
            'external_partners': external_partners,
            'attachments': attachments,
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
        Route to send messages

        @param issue_id: id of issue
        @param post: Contains values of the issue form
        @return: redirect
        """
        current_user = http.request.env.user
        issue = request.env['project.issue'].search([('id', '=', issue_id)])
        error = False

        if post:
            message = post.get('comment')

            if message:
                # Check attachment isn't too big and add them to a list
                attachment_ids = post.get('attachment_ids') or None
                max_size = http.request.env['ir.config_parameter'].get_param(
                    'website_project_issue_extension.attachment_max_size')
                attachment_list = list()
                if attachment_ids:
                    files_dict = dict(request.httprequest.files)
                    for attachment_file in files_dict['attachment_ids']:
                        attachment_file_value = attachment_file.value
                        attachment_file_value.seek(0, os.SEEK_END)
                        file_size = attachment_file_value.tell()
                        attachment_file_value.seek(0)
                        if file_size > max_size * 1000 * 1000:
                            # File size too big
                            error = True
                        else:
                            attachment_list.append(
                                (attachment_file_value.filename, attachment_file_value.read())
                            )
                if not error:
                    subject = _('Issue') + " #" + issue.issue_number + ": " + issue.name
                    subtype_id = http.request.env.ref('mail.mt_comment').id
                    issue.sudo(current_user).message_post(
                        subject=subject,
                        message_type='comment',
                        subtype_id=subtype_id,
                        body=message,
                        attachments=attachment_list,
                        portal_message=True,
                    )
        return request.redirect('/my/issues/%d' % issue_id)


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
        issue = request.env['project.issue'].search([('id', '=', issue_id)])

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


    @http.route(
        '/my/issues/<int:issue_id>/follower/add',
        type='json',
        auth='public',
        website=True)
    def issue_add_followers(self, issue_id=None, followers=None):
        """
        Add followers to issue

        @param issue_id: ID of issue
        @param followers: String of comma separated emails
        @return result: Created followers (id email)
        """
        result = list()
        res = dict()
        issue = request.env['project.issue'].search([('id', '=', issue_id)])
        _logger.debug("Issue: %s, Followers: %s" % (issue.id, followers))
        if issue and followers:
            # Validate format and create partners if needed
            res = validate_follower_emails(followers)
            if not res.get('error', False):
                result = subscribe_issue_followers(issue, res['emails'])
        return result


    @http.route(
        '/my/issues/<int:issue_id>/follower/remove',
        type='json',
        auth='public',
        website=True)
    def issue_remove_follower(self, issue_id=None, follower_id=None):
        """
        Remove follower from issue

        @param issue_id: ID of issue
        @param follower_id: ID of follower to be deleted
        @return result: Created followers (id email)
        """
        res = dict()
        issue = request.env['project.issue'].search([('id', '=', issue_id)])
        follower_id = int(follower_id)
        _logger.debug("Issue: %s, Follower: %s" % (issue.id, follower_id))
        if issue and follower_id and follower_id != issue.partner_id.id:
            res['id'] = follower_id
            issue.message_unsubscribe([int(follower_id)])
        return res
