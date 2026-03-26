import base64
import logging
import os
from collections import OrderedDict

from odoo import _, http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
from odoo.osv.expression import AND

from odoo.addons.hr_timesheet.controllers.portal import TimesheetCustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.project.controllers.portal import CustomerPortal

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


class PortalSupportTicket(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        helpdesk_project = (
            request.env["project.project"]
            .sudo()
            .search([("helpdesk_project", "=", True)])
        )
        if "support_tickets_count" in counters:
            values["support_tickets_count"] = (
                (
                    request.env["project.task"].search_count(
                        [
                            ("project_id", "=", helpdesk_project.id),
                        ]
                    )
                )
                if request.env["project.task"].check_access_rights(
                    "read", raise_exception=False
                )
                else 0
            )

        if "task_count" in values:
            values["task_count"] = (
                request.env["project.task"].search_count(
                    [
                        ("project_id", "!=", helpdesk_project.id),
                    ]
                )
                if request.env["project.task"].check_access_rights(
                    "read", raise_exception=False
                )
                else 0
            )
        return values

    def _task_get_searchbar_sortings(self, milestones_allowed, project=False):
        """Override 'Sort By' dropdown above task list with fewer options"""
        res = super()._task_get_searchbar_sortings(
            milestones_allowed=milestones_allowed, project=project
        )

        res.pop("progress", None)
        res.pop("date_deadline", None)
        res.pop("milestone", None)

        # Maybe put back if useful, but can be confused with Stage
        res.pop("status", None)

        res["customer"] = {
            "label": _("Customer"),
            "order": "partner_id asc, id desc",
            "sequence": 35,  # mikä vaan sopiva numero
        }

        return res

    def _task_get_searchbar_groupby(self, milestones_allowed, project=False):
        """Override 'Group By' dropdown above task list with fewer options"""
        res = super()._task_get_searchbar_groupby(
            milestones_allowed=milestones_allowed, project=project
        )

        res.pop("sale_order", None)
        res.pop("sale_line", None)
        # res.pop("customer", None)
        res.pop("milestone", None)

        # Maybe put back if useful, but can be confused with Stage
        res.pop("status", None)

        return res

    def _get_my_tasks_searchbar_filters(self, project_domain=None, task_domain=None):
        """Filter By dropdown: All + My tickets (customer)."""

        my_partner = request.env.user.partner_id.commercial_partner_id

        return {
            "all": {
                "label": _("All"),
                "domain": [("project_id", "!=", False)],
            },
            "customer": {
                "label": _("My tickets"),
                "domain": [("partner_id", "=", my_partner.id)],
            },
        }

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
        """Limit tasks shown to only those where the portal user has been added to the
        Portal Users with Access field"""

        # Check based on the path whether to fetch support tickets or regular tasks
        current_path = request.httprequest.path  # e.g., "/my/tickets/123"
        viewing_helpdesk_tickets = "/my/tickets" in current_path

        if viewing_helpdesk_tickets:
            domain = AND([domain, [("project_id.helpdesk_project", "=", True)]])
        else:
            domain = AND([domain, [("project_id.helpdesk_project", "=", False)]])

            if request.env.user.has_group("base.group_portal"):
                # Check the 'Portal Users with Access' field
                domain = AND(
                    [domain, [("allowed_portal_user_ids", "in", [request.env.user.id])]]
                )

                # Exclude tasks from closed projects
                domain = AND([domain, [("project_id.stage_id.is_closed", "=", False)]])

        res = super()._prepare_tasks_values(
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

        if viewing_helpdesk_tickets:
            res.update(
                {
                    "is_ticket": True,
                    "page_name": "tickets",
                    "default_url": "/my/tickets",
                }
            )

            res["pager"].update({"url": "/my/tickets"})

        return res

    @http.route(
        ["/my/tickets", "/my/tickets/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_tickets(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        filterby=None,
        search=None,
        search_in="content",
        groupby=None,
        **kw,
    ):
        searchbar_filters = self._get_my_tasks_searchbar_filters()

        if not filterby:
            filterby = "all"
        domain = searchbar_filters.get(filterby, searchbar_filters.get("all"))["domain"]

        values = self._prepare_tasks_values(
            page,
            date_begin,
            date_end,
            sortby,
            search,
            search_in,
            groupby,
            domain=domain,
        )

        # pager
        pager_vals = values["pager"]
        pager_vals["url_args"].update(filterby=filterby)
        pager = portal_pager(**pager_vals)

        values.update(
            {
                "grouped_tasks": values["grouped_tasks"](pager["offset"]),
                "pager": pager,
                "searchbar_filters": OrderedDict(sorted(searchbar_filters.items())),
                "filterby": filterby,
            }
        )
        return request.render("project.portal_my_tasks", values)

    @http.route(
        ["/my/ticket/<int:ticket_id>"], type="http", auth="public", website=True
    )
    def portal_my_ticket(self, ticket_id, access_token=None, **kw):
        try:
            task_sudo = self._document_check_access(
                "project.task", ticket_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        # Check if ticket is instead task, redirect to project task then
        if not task_sudo.project_id.helpdesk_project:
            return request.redirect(f"/my/task/{ticket_id}")

        # ensure attachment are accessible with access token inside template
        for attachment in task_sudo.attachment_ids:
            attachment.generate_access_token()
        values = self._task_get_page_view_values(task_sudo, access_token, **kw)
        follower_parters = (
            task_sudo.message_follower_ids.mapped("partner_id") | task_sudo.partner_id
        )
        internal_ids = (
            request.env["res.users"]
            .sudo()
            .with_context(active_test=False)
            .search([])
            .filtered(lambda r: r.has_group("base.group_user"))
            .mapped("partner_id")
            .ids
        )
        ext_partners = follower_parters.filtered(lambda r: r.id not in internal_ids)
        ext_followers = ", ".join([p.name for p in ext_partners])
        values.update(
            {
                "page_name": "ticket",
                "ext_followers": ext_followers,
                "show_submission_received_msg": kw.get("submitted", False),
            }
        )
        return request.render("project.portal_my_task", values)

    @http.route(
        ["/ticket/create"], type="http", auth="user", methods=["POST"], website=True
    )
    def portal_create_ticket(self, **post):
        """Create ticket from portal"""
        current_user = request.env.user
        subject = post.get("subject", "").strip()
        description = post.get("description", "").strip()
        helpdesk_project = (
            request.env["project.project"]
            .sudo()
            .search([("helpdesk_project", "=", True)], limit=1)
        )
        if subject and description and helpdesk_project:
            try:
                task = (
                    request.env["project.task"]
                    .sudo()
                    .create(
                        {
                            "name": subject,
                            "description": description,
                            "partner_id": current_user.partner_id.id,
                            "project_id": helpdesk_project.id,
                            "user_ids": None,
                        }
                    )
                )
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
                _logger.error(
                    "Attachment is too large, prevent creating ticket and attacments"
                )

        # return request.redirect("/my/tickets")
        return request.redirect(f"/my/ticket/{task.id}?submitted=1")

    def _task_get_page_view_values(self, task, access_token, **kwargs):
        values = super()._task_get_page_view_values(task, access_token, **kwargs)
        # Prevent timesheets on task view, since sudo used we have to pop elements
        values.pop("timesheets")
        values.pop("timesheets_by_subtask")

        # Always hide the project link
        values["project_accessible"] = False
        return values

    @http.route(
        ["/my/project/<int:project_id>"], type="http", auth="public", website=True
    )
    def portal_my_project(self, project_id=None, access_token=None, **kw):
        # Prevent project view
        return request.redirect("/my")

    @http.route(["/my/tasks/<int:task_id>"], type="http", auth="user", website=True)
    def portal_my_task(
        self, task_id, report_type=None, access_token=None, project_sharing=False, **kw
    ):
        """No access with only access token (change auth from public to user)"""

        # Check if task is actually a helpdesk project ticket, redirect to ticket view
        task_sudo = request.env["project.task"].sudo().search([("id", "=", task_id)])
        if task_sudo.project_id.helpdesk_project:
            return request.redirect(f"/my/ticket/{task_id}")

        # Prevent access if task belongs to a closed project,
        # or the portal user has not been
        # granted access to view the task

        if task_sudo.project_id.stage_id.is_closed:
            return request.redirect("/my")

        if (
            request.env.user.has_group("base.group_portal")
            and request.env.user.id not in task_sudo.allowed_portal_user_ids.ids
        ):
            return request.redirect("/my")

        return super().portal_my_task(
            task_id, report_type, access_token, project_sharing, **kw
        )


class TimesheetCustomerPortal(TimesheetCustomerPortal):
    @http.route(
        ["/my/timesheets", "/my/timesheets/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_timesheets(
        self,
        page=1,
        sortby=None,
        filterby=None,
        search=None,
        search_in="all",
        groupby="none",
        **kw,
    ):
        """Prevent user to check timesheets from portal"""
        return request.redirect("/my")
