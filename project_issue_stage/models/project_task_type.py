# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class ProjectTaskType(models.Model):

    # 1. Private attributes
    _inherit = 'project.task.type'

    # 2. Fields declaration
    website_label_class = fields.Selection(
        selection=[
            ('default', 'Default'),
            ('primary', 'Primary'),
            ('success', 'Success'),
            ('info', 'Info'),
            ('warning', 'Warning'),
            ('danger', 'Danger'),
        ],
        default='info',
        string='Bootstrap label class',
        help='Define label class (Bootstrap) to be used on frontend',
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
