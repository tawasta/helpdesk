# -*- coding: utf-8 -*-
from odoo import fields, models


class FetchmailServer(models.Model):

    _inherit = 'fetchmail.server'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        help='Company which the mail server belongs to',
    )
