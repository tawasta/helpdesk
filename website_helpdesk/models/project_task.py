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
from odoo import api, fields, models

# 2. Known third party imports:


# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


_logger = logging.getLogger(__name__)


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
    # @api.depends("project_id.allowed_user_ids", "project_id.privacy_visibility")
    # def _compute_allowed_user_ids(self):
    #     """
    #     By default project allowed_user_ids see all the tasks. Overwrite this
    #     so that you have to explicitely give permission for each task.
    #     """
    #     for task in self.with_context(prefetch_fields=False):
    #         portal_users = task.allowed_user_ids.filtered("share")
    #         internal_users = task.allowed_user_ids - portal_users
    #         if task.project_id.privacy_visibility == "followers":
    #             task.allowed_user_ids |= task.project_id.allowed_internal_user_ids
    #             task.allowed_user_ids -= portal_users
    #         # elif task.project_id.privacy_visibility == "portal":
    #         #     task.allowed_user_ids |= task.project_id.allowed_portal_user_ids
    #         if task.project_id.privacy_visibility != "portal":
    #             task.allowed_user_ids -= portal_users
    #         elif task.project_id.privacy_visibility != "followers":
    #             task.allowed_user_ids -= internal_users

    # # 6. CRUD methods
    # @api.model
    # def create(self, vals):
    #     """Add portal users automatically when creating ticket"""
    #     res = super().create(vals)

    #     trigger_fields = [
    #         "partner_id",
    #         "message_follower_ids",
    #     ]
    #     if vals.keys() & trigger_fields:
    #         # One of trigger fields, update portal users
    #         res.update_portal_users()

    #     return res

    # def write(self, vals):
    #     """Add portal users automatically"""
    #     res = super().write(vals)

    #     trigger_fields = [
    #         "partner_id",
    #         "message_follower_ids",
    #     ]
    #     if vals.keys() & trigger_fields:
    #         # One of trigger fields, update portal users
    #         self.update_portal_users()

    #     return res

    # def update_portal_users(self):
    #     """Update portal users accordingly"""
    #     helpdesk_projects = (
    #         self.env["project.project"].sudo().search([("helpdesk_project", "=", True)])
    #     )
    #     allowed_users = self.env["res.users"]

    #     for rec in self:
    #         if rec.project_id in helpdesk_projects:
    #             # Check if customer is portal user, grant access
    #             user = (
    #                 self.env["res.users"]
    #                 .sudo()
    #                 .search([("partner_id", "=", rec.partner_id.id)])
    #             )
    #             if user and user.has_group("base.group_portal"):
    #                 _logger.info("Add customer to portal users...")
    #                 allowed_users |= user

    #             # Figure out eTuki-users, add them as well
    #             commercial_partner = rec.partner_id.commercial_partner_id
    #             rec_etuki_partners = (
    #                 self.env["res.partner"]
    #                 .sudo()
    #                 .search(
    #                     [
    #                         ("commercial_partner_id", "=", commercial_partner.id),
    #                         ("installation_technical_contact_ids", "!=", False),
    #                     ]
    #                 )
    #             )
    #             etuki_users = (
    #                 self.env["res.users"]
    #                 .sudo()
    #                 .search(
    #                     [
    #                         ("partner_id", "in", rec_etuki_partners.ids),
    #                     ]
    #                 )
    #             ).filtered(lambda r: r.has_group("base.group_portal"))

    #             if etuki_users:
    #                 _logger.info("Add eTuki customers to portal users...")
    #                 allowed_users |= etuki_users

    #             # Figure out followers
    #             follower_partners = rec.message_follower_ids.mapped("partner_id")
    #             follower_users = (
    #                 self.env["res.users"]
    #                 .sudo()
    #                 .search(
    #                     [
    #                         ("partner_id", "in", follower_partners.ids),
    #                     ]
    #                 )
    #             ).filtered(lambda r: r.has_group("base.group_portal"))

    #             if follower_users:
    #                 _logger.info("Add follower customers to portal users...")
    #                 allowed_users |= follower_users

    #             rec.allowed_user_ids = allowed_users

    # 7. Action methods
    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, *args, **kwargs):
        """Trigger reopen if message from portal user"""
        author = kwargs.get("author_id", 0)
        author_user = self.env["res.users"].sudo().search([("partner_id", "=", author)])
        if author_user and author_user.has_group("base.group_portal"):
            self._reopen()

        return super().message_post(
            *args,
            **kwargs,
        )

    def message_post_with_template(self, template_id, **kwargs):
        """Trigger reopen if message from portal user"""
        author = kwargs.get("author_id", 0)
        author_user = self.env["res.users"].sudo().search([("partner_id", "=", author)])
        if author_user and author_user.has_group("base.group_portal"):
            self._reopen()

        return super().message_post_with_template(
            template_id,
            **kwargs,
        )

    # 8. Business methods
