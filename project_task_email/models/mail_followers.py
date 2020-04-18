from odoo import models


class Followers(models.Model):

    _inherit = "mail.followers"

    def _add_followers(self, res_model, res_ids, partner_ids, *args, **kwargs):
        """ Override to disallow adding admin to followers for tasks """

        if res_model == 'project.task':
            # These partner ids will never be added to followers
            remove_ids = [
                self.env.ref('base.partner_admin').id,
                self.env.ref('base.partner_root').id,
            ]

            for remove_id in remove_ids:
                if remove_id in partner_ids:
                    partner_ids.remove(remove_id)

        res = super(Followers, self)._add_followers(
            res_model, res_ids, partner_ids, *args, **kwargs
        )

        return res
