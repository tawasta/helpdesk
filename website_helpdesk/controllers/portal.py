import base64
import logging
import os

from markupsafe import Markup

from odoo import _, http
from odoo.exceptions import UserError
from odoo.fields import Domain
from odoo.http import request

from odoo.addons.project.controllers.portal import ProjectCustomerPortal

_logger = logging.getLogger(__name__)

def process_file(file):
    """
    Check if the file is too large.
    Max size can be set on system parameters.

    :param file: processed file
    :return: boolean if the file was too big
    """
    max_size_key = "website_helpdesk.attachment_max_size"
    # Default size 20 MB
    MAX_SIZE = int(
        request.env["ir.config_parameter"].sudo().get_param(max_size_key, 20)
    )
    too_big = False
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > MAX_SIZE * 1024 * 1024:
        too_big = True
        _logger.warning(
            "Attachment filesize too big: %d MB" % (file_size / 1024 / 1024)
        )
    return too_big


class ProjectHelpdeskPortal(ProjectCustomerPortal):

    def _is_support_tickets(self):
        return request.params.get("filterby") == "support_tickets"

    def _get_my_tasks_searchbar_filters(self, project_domain=None, task_domain=None):
        filters = super()._get_my_tasks_searchbar_filters(
            project_domain=project_domain,
            task_domain=task_domain,
        )

        regular_task_domain = Domain("project_id.helpdesk_project", "=", False)
        support_ticket_domain = Domain("project_id.helpdesk_project", "=", True)

        if task_domain:
            regular_task_domain &= Domain(task_domain)
            support_ticket_domain &= Domain(task_domain)

        if "all" in filters:
            filters["all"]["domain"] = regular_task_domain

        support_filter = {
            "label": _("Support tickets"),
            "domain": support_ticket_domain,
        }

        # kun ollaan support ticket -näkymässä, älä näytä muita projekteja filterissä
        if self._is_support_tickets():
            return {
                "support_tickets": support_filter,
            }

        filters["support_tickets"] = support_filter
        return filters

    def _prepare_tasks_values(
        self,
        page,
        date_begin,
        date_end,
        sortby,
        search,
        search_in,
        groupby,
        url="/my/tasks",
        domain=None,
        su=False,
        project=False,
    ):

        values = super()._prepare_tasks_values(
            page=page,
            date_begin=date_begin,
            date_end=date_end,
            sortby=sortby,
            search=search,
            search_in=search_in,
            groupby=groupby,
            url=url,
            domain=domain,
            su=su,
            project=project,
        )

        values.update(
            {
                "support_ticket_project": self._is_support_tickets(),

            }
        )
        return values

    
    @http.route(
        "/ticket/create",
        type="http",
        auth="user",
        methods=["POST"],
        website=True,
    )
    def portal_create_support_ticket(self, **post):
        subject = (post.get("subject") or "").strip()
        description = (post.get("description") or "").strip()

        if not subject or not description:
            return request.redirect(
                "/my/tasks?filterby=support_tickets&ticket_error=missing_required"
            )

        project = (
            request.env["project.project"]
            .sudo()
            .search([("helpdesk_project", "=", True)], limit=1)
        )
        if not project:
            _logger.warning("No active support ticket project configured.")
            return request.redirect(
                "/my/tasks?filterby=support_tickets&ticket_error=no_project"
            )

        partner = request.env.user.partner_id

        task = (
            request.env["project.task"]
            .sudo()
            .create(
                {
                    "name": subject,
                    "description": Markup.escape(description).replace("\n", Markup("<br/>")),
                    "partner_id": partner.id,
                    "project_id": project.id,
                    "user_ids": False,
                }
            )
        )

        try:
            # Create attachments
            for file in request.httprequest.files.getlist("file"):
                too_big = process_file(file)
                if too_big:
                    raise UserError(_("Attachment is too large!"))

                datas = base64.b64encode(file.read())

                if not datas:
                    continue

                request.env["ir.attachment"].sudo().create(
                    {
                        "name": file.filename,
                        "datas": datas,
                        "type": "binary",
                        "res_id": task.id,
                        "res_model": "project.task",
                    }
                )
        except UserError:
            # Keep created ticket, but show the user a clear error.
            _logger.info("Support ticket created, but one attachment was too large.")
            return request.redirect(
                f"/my/tasks/{task.id}?ticket_created=1&ticket_error=attachment_too_large"
            )

        return request.redirect(f"/my/tasks/{task.id}?ticket_created=1")
        
