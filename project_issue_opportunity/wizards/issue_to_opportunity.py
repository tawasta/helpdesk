# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models, _

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class IssueToOpportunity(models.TransientModel):

    # 1. Private attributes
    _name = 'issue.to.opportunity'

    # 2. Fields declaration
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
        help=_("Related partner to this opportunity")
    )
    name = fields.Char(
        string='Name',
        required=True,
        help=_("Opportunity's name")
    )
    description = fields.Text(
        string='Description',
        help=_("Opportunity's description in plain text")
    )
    user = fields.Many2one(
        comodel_name='res.users',
        string='User',
        help=_("Created by user")
    )

    # 3. Default methods
    @api.model
    def default_get(self, field_list):
        """
        Get default values for fields when
        creating a new opportunity from issue
        """
        active_id = self._context['active_id']
        issue = self.env['project.issue'].browse([active_id])
        name = "%s - %s" % (issue.partner_id.name, issue.name) \
            if issue.partner_id else issue.name
        values = {
            'name': name,
            'description': issue.description,
            'partner_id': issue.partner_id.id,
            'user': self._uid,
        }
        return values

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    @api.multi
    def create_opportunity(self):
        """
        Action method for creating an opportunity
        from an issue
        """
        self.ensure_one()
        context = self._context

        values = {
            'partner_id': self.partner_id.id,
            'name': self.name,
            'description': self.description,
            'type': 'opportunity',
        }
        opportunity = self.env['crm.lead'].create(values)

        if 'active_id' in context:
            active_id = context['active_id']
            issue = self.env['project.issue'].browse([active_id])
            opportunity.issue = issue.id
        # Select opportunity form as the view
        view_id = self.env.ref('crm.crm_case_form_view_oppor').id
        return {
            'name': _('Opportunity created'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'crm.lead',
            'target': 'current',
            'res_id': opportunity.id,
            'type': 'ir.actions.act_window',
        }

    # 8. Business methods
