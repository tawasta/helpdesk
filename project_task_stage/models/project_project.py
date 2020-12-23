from odoo import api, models


class Project(models.Model):

    _inherit = "project.project"

    @api.model
    def create(self, vals):
        """ Default stages for projects' that contain tasks """
        project = super(Project, self).create(vals)

        if vals.get("use_tasks") and (
            not vals.get("type_ids") or len(vals.get("type_ids")[0][2]) == 0
        ):

            task_stages = (
                self.env["project.task.type"]
                .sudo()
                .search([("task_stage", "=", True),])
            )
            project.type_ids = [(6, 0, task_stages.ids)]
        return project
