# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

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

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for record in self:
            if record.partner_id and record.partner_id.sla:
                record.sla = record.partner_id.sla

    @api.model
    def create(self, vals):
        partner_id = vals.get('partner_id')

        # When creating a new task, get SLA from partner
        if partner_id and not vals.get('sla'):
            vals['sla'] = self.env['res.partner'].browse([partner_id]).sla

        return super(ProjectIssue, self).create(vals)
