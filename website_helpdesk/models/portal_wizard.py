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
from odoo import models

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
            # We are eTuki partner, find all tickets for commercial partner
            commercial_partner = self.partner_id.commercial_partner_id
            comm_tickets = (
                self.env["project.task"]
                .sudo()
                .search(
                    [
                        ("commercial_partner_id", "=", commercial_partner.id),
                        ("project_id.helpdesk_project", "=", True),
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
