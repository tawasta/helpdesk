from odoo import fields, models


class ProjectTask(models.Model):

    _inherit = "project.task"

    helpdesk_project = fields.Boolean(related="project_id.helpdesk_project")
