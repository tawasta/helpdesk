# 1. Standard library imports:
import logging

# 2. Known third party imports:
# 3. Odoo imports (openerp):
from odoo import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = "project.project"

    restrict_selectable_external_users = fields.Boolean(
        string="Restrict Selectable External Users for Tasks",
        tracking=True,
        default=False,
        copy=False,
        help="If set, task assignees or portal users "
        "can be only those configured below",
    )

    selectable_external_user_ids = fields.Many2many(
        "res.users",
        string="Selectable External Users for Tasks",
        tracking=True,
        copy=False,
        domain=[("share", "=", True)],
        help="Only these external users can be set as tasks' Assignee or Portal Users",
    )

    # 3. Default methods

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
