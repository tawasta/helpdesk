# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import http, _
from odoo.addons.website_project_issue.controllers.main import WebsiteAccount
from odoo.http import request

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

# _logger = logging.getLogger(__name__)


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
        """
        current_user = http.request.env.user
        issue = request.env['project.issue'].browse(issue_id)
        if issue.message_needaction_counter > 0:
            messages = request.env['mail.message'].search([
                ('model', '=', issue._name),
                ('res_id', '=', issue.id),
                ('needaction', '=', True)
            ])
            messages.write({'needaction_partner_ids': [(3, current_user.partner_id.id)]})
        return super(WebsiteAccount, self).my_issues_issue(issue_id)
