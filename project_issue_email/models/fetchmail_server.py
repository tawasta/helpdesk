# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class FetchmailServer(models.Model):

    # 1. Private attributes
    _inherit = 'fetchmail.server'

    # 2. Fields declaration
    # The point of company id in fetchmail servers is to allow
    # matching the claims to a correct company in a multi-company environment
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        help='Company which the mail server belongs to',
    )

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
