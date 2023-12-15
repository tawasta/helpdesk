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

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class ProjectTask(models.Model):

    # 1. Private attributes
    _inherit = "project.task"

    # 2. Fields declaration
    portal_description = fields.Html(
        string="Portal description",
        help="Description for the task which is shown for portal customers",
    )
    portal_planned_hours = fields.Float(
        string="Portal planned hours",
        help="Planned hours which is shown for portal customers",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges
    @api.depends("project_id.allowed_user_ids", "project_id.privacy_visibility")
    def _compute_allowed_user_ids(self):
        """
        By default project allowed_user_ids see all the tasks. Overwrite this
        so that you have to explicitely give permission for each task.
        """
        for task in self.with_context(prefetch_fields=False):
            portal_users = task.allowed_user_ids.filtered("share")
            internal_users = task.allowed_user_ids - portal_users
            if task.project_id.privacy_visibility == "followers":
                task.allowed_user_ids |= task.project_id.allowed_internal_user_ids
                task.allowed_user_ids -= portal_users
            # elif task.project_id.privacy_visibility == "portal":
            #     task.allowed_user_ids |= task.project_id.allowed_portal_user_ids
            if task.project_id.privacy_visibility != "portal":
                task.allowed_user_ids -= portal_users
            elif task.project_id.privacy_visibility != "followers":
                task.allowed_user_ids -= internal_users

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
