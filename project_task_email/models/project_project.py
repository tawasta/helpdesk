import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):

    _inherit = "project.project"

    email_from = fields.Char(
        string="Sender email",
        help="Force sender email address on tasks",
    )
