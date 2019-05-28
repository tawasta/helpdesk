# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import models, fields

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class ProjectIssue(models.Model):

    # 1. Private attributes
    _inherit = 'project.issue'

    # 2. Fields declaration
    sla = fields.Selection(
        [
            ('0', '-'),
            ('1', 'Level 1'),
            ('2', 'Level 2'),
            ('3', 'Level 3'),
            ('4', 'Level 4'),
        ],
        string='Service level',
        default='1',
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
