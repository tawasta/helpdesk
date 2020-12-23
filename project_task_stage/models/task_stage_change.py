# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class TaskStageChange(models.Model):

    # 1. Private attributes
    _name = "project.task.stage.change"
    _order = "create_date DESC"

    # 2. Fields declaration
    old_stage_id = fields.Many2one("project.task.type", string="Old stage",)
    new_stage_id = fields.Many2one("project.task.type", string="New stage",)
    task_id = fields.Many2one("project.task", string="Task id",)
    task_company_id = fields.Many2one(
        "res.company", related="task_id.company_id", string="Company id", store=True,
    )
    task_partner_id = fields.Many2one(
        comodel_name="res.partner", related="task_id.partner_id", store=True,
    )
    task_create_date = fields.Datetime(related="task_id.create_date", store=True,)
    start_date = fields.Datetime(
        string="Start date", help="When stage was started", store=True,
    )
    end_date = fields.Datetime(string="End date", help="When stage ended", store=True,)
    hours = fields.Float(string="Hours", help="Duration of the stage",)

    # 3. Default methods

    # 4. Compute and search fields

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
