# -*- coding: utf-8 -*-

# 1. Standard library imports:

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
        if post:
            name = post.get('issue_name')
            # Parse
            description = BeautifulSoup(post.get('issue_summary'), 'lxml').text
            values = {
                'name': name,
                'description': description,
                'project_id': 2,
                'partner_id': 8,
            }
            print values
            http.request.env['project.issue'].sudo().create(values)
        return request.redirect('/my/issues')