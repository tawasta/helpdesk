# -*- coding: utf-8 -*-

# 1. Standard library imports:
from math import log

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class IrAttachment(models.Model):

    # 1. Private attributes
    _inherit = 'ir.attachment'

    # 2. Fields declaration
    file_size_hr = fields.Char(
        compute='_compute_attachment_file_size_hr',
        string='File size',
        help='File size for attachment in human readable format',
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.multi
    def _compute_attachment_file_size_hr(self):
        """
        Compute human readable version of file size
        """
        for record in self:
            suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
            size = record.file_size
            order = int(log(size, 2) / 10) if size else 0
            record.file_size_hr = '{:.4g} {}'.format(size / (1 << (order * 10)), suffixes[order])

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
