# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResCompany(models.Model):

    _inherit = 'res.company'

    mattermost_active = fields.Boolean(
        string='Active',
        help='Use mattermost notifications for this company?',
        default=False,
    )
    mattermost_login_id = fields.Char(
        string='User',
    )
    mattermost_password = fields.Char(
        string='Password',
    )
    mattermost_team = fields.Char(
        string='Team',
    )
    mattermost_channel = fields.Char(
        string='Channel',
    )
    mattermost_url = fields.Char(
        string='URL',
    )
    mattermost_port = fields.Char(
        string='Port',
        default='443',
    )
    mattermost_basepath = fields.Char(
        string='Path',
        default='/api/v4',
    )
    mattermost_scheme = fields.Selection(
        string='Scheme',
        selection=[('http', 'http'), ('https', 'https')],
        default='https',
    )
    mattermost_verify = fields.Boolean(
        string='Verify',
        default=True,
    )
