# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class ResCompany(models.Model):

    # 1. Private attributes
    _inherit = 'res.company'

    # 2. Fields declaration
    mattermost_active = fields.Boolean(
        string='Active',
        help='Use mattermost notifications for this company?',
        default=False,
    )
    mattermost_url = fields.Char(
        string='URL',
        help='URL of the mattermost server',
    )
    mattermost_hook_ids = fields.One2many(
        comodel_name='mattermost.hook',
        inverse_name='company_id',
        string='Company mattermost hooks',
        help='Mattermost hooks used by this company',
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
