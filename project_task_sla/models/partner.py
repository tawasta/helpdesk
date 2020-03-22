from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

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
