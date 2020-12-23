from odoo import models
from odoo import fields
from odoo import api


class Partner(models.Model):
    _inherit = "res.partner"

    sla = fields.Selection(
        [
            ("0", "-"),
            ("1", "Level 1"),
            ("2", "Level 2"),
            ("3", "Level 3"),
            ("4", "Level 4"),
        ],
        string="Service level",
        default="1",
    )

    @api.model
    def _commercial_fields(self):
        """ Add SLA to commercial fields """

        return super(Partner, self)._commercial_fields() + ["sla"]
