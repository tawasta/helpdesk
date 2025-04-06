##############################################################################
#
#    Author: Futural Oy
#    Copyright 2023- Futural Oy (https://futural.fi)
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

        # TODO: in 14.0 we auto-added eTuki users to multiple tickets' allowed_user_ids.
        # If we want similar functionality in 17, needs to be reimplemented

        return res

    # 8. Business methods


class PortalMixin(models.AbstractModel):
    _inherit = "portal.mixin"

    def _portal_ensure_token(self):
        """Don't generate tokens for portal access"""
        if self.access_token:
            self.sudo().write({"access_token": None})
        return False

    def _notify_get_groups(self, msg_vals=None):
        # TODO: this seems to do nothing in 17, leftover code from 14.
        # Probably OK to delete
        """Prevent portal customers group"""
        groups = super()._notify_get_groups(msg_vals)
        new_groups = []
        partner_id = hasattr(self, "partner_id") and self.partner_id.id

        portal_privacy = (
            # If model has no "project_id" attribute, don't allow portal access
            hasattr(self, "project_id")
            and self.project_id.privacy_visibility == "portal"
        )

        if hasattr(self, "allowed_user_ids"):
            allowed_user_ids = self.allowed_user_ids.partner_id.ids
        else:
            # If model has no "allowed_user_ids" attribute, don't allow portal access
            allowed_user_ids = []

        if portal_privacy and partner_id in allowed_user_ids:
            _logger.info("Granting access to portal user")
            groups.append(
                (
                    "allowed_helpdesk_portal_users",
                    lambda pdata: pdata["type"] == "portal"
                    and pdata["id"] in allowed_user_ids,
                    {"has_button_access": True},
                )
            )

        for group_name, group_method, group_data in groups:
            if group_name == "portal_customer" and partner_id not in allowed_user_ids:
                _logger.error("Skipping portal_customer group")
            else:
                new_groups.append((group_name, group_method, group_data))

        return new_groups
