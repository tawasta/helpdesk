# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class MattermostHook(models.Model):

    # 1. Private attributes
    _inherit = 'mattermost.hook'

    # 2. Fields declaration
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        help='Company who owns the hook',
        required=True,
    )
    hook = fields.Char(
        string='Hook key',
        help='The incoming webhook generated key',
        required=True,
    )
    channel = fields.Char(
        string='Channel',
        help='Channel the message is posted to',
    )
    username = fields.Char(
        string='Username',
        help='Username who posts the message to Mattermost',
    )
    iconurl = fields.Char(
        string='Icon URL',
        help='Icon url to be used for posting the message',
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
