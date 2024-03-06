##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2023- Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################

# 1. Standard library imports:
import logging

# 3. Odoo imports (openerp):
from odoo import fields, models

# 2. Known third party imports:


# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

_logger = logging.getLogger(__name__)


class PortalWizardUser(models.TransientModel):

    # 1. Private attributes
    _inherit = "portal.wizard.user"

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def _create_user(self):
        res = super()._create_user()

        # If portal user is eTuki partner, add to all tickets
        if self.partner_id.installation_technical_contact_ids:
            # We are eTuki partner, find all tickets for commercial partner created today
            commercial_partner = self.partner_id.commercial_partner_id
            comm_tickets = (
                self.env["project.task"]
                .sudo()
                .search(
                    [
                        ("commercial_partner_id", "=", commercial_partner.id),
                        ("project_id.helpdesk_project", "=", True),
                        ("create_date", ">", fields.Datetime.today()),
                    ]
                )
            )
            if comm_tickets:
                _logger.info(
                    "Add portal user (eTuki) to {} company tickets".format(
                        len(comm_tickets)
                    )
                )
                comm_tickets.write({"allowed_user_ids": [(4, res.id)]})

        return res

    # 8. Business methods


class PortalMixin(models.AbstractModel):
    _inherit = "portal.mixin"

    def _portal_ensure_token(self):
        """Don't generate tokens for portal access"""
        if self.access_token:
            self.sudo().write({"access_token": None})
        return "no_token"

    def _notify_get_groups(self, msg_vals=None):
        """Prevent portal customers group"""
        groups = super()._notify_get_groups(msg_vals)
        partner_id = hasattr(self, "partner_id") and self.partner_id.id
        user = self.env["res.users"]
        if partner_id:
            user = (
                self.env["res.users"].sudo().search([("partner_id", "=", partner_id)])
            )
        new_groups = []
        for group_name, group_method, group_data in groups:
            if group_name != "portal_customer":
                new_groups.append((group_name, group_method, group_data))
            elif user and user.has_group("base.group_portal"):
                new_groups.append((group_name, group_method, group_data))
                _logger.error("Grant portal user access")
            else:
                _logger.error("Skipping portal_customer group")

        return new_groups
