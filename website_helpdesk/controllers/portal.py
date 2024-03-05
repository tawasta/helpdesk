import logging
from collections import OrderedDict
from operator import itemgetter

from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.osv.expression import OR
from odoo.tools import groupby as groupbyelem

from odoo.addons.hr_timesheet.controllers.portal import TimesheetCustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.project.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)


class PortalSupportTicket(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        helpdesk_project = (
            request.env["project.project"]
            .sudo()
            .search([("helpdesk_project", "=", True)])
        )
        if "support_tickets_count" in counters:
            # Show tickets from partner's company
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
        **kw
    ):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            "date": {"label": _("Newest"), "order": "create_date desc"},
            "name": {"label": _("Title"), "order": "name"},
            "stage": {"label": _("Stage"), "order": "stage_id, project_id"},
            "update": {
                "label": _("Last Stage Update"),
                "order": "date_last_stage_update desc",
            },
        }
        searchbar_filters = {
            "all": {"label": _("All"), "domain": []},
        }
        searchbar_inputs = {
            "content": {
                "input": "content",
                "label": _("Search <span class='nolabel'> (in Content)</span>"),
            },
            "message": {"input": "message", "label": _("Search in Messages")},
            "customer": {"input": "customer", "label": _("Search in Customer")},
            "stage": {"input": "stage", "label": _("Search in Stages")},
            "all": {"input": "all", "label": _("Search in All")},
        }
        searchbar_groupby = {
            "none": {"input": "none", "label": _("None")},
            "project": {"input": "project", "label": _("Project")},
            "stage": {"input": "stage", "label": _("Stage")},
        }

        # extends filterby criteria with project the customer has access to
        helpdesk_project = (
            request.env["project.project"]
            .sudo()
            .search([("helpdesk_project", "=", True)])
        )
        searchbar_filters.update(
            {
                str(helpdesk_project.id): {
                    "label": helpdesk_project.name,
                    "domain": [("project_id", "=", helpdesk_project.id)],
                }
            }
        )

        # default sort by value
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        # default filter by value
        if not filterby:
            filterby = "all"
        domain = searchbar_filters.get(filterby, searchbar_filters.get("all"))["domain"]

        # default group by value
        if not groupby:
            groupby = "project"

        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ("content", "all"):
                search_domain = OR(
                    [
                        search_domain,
                        [
                            "|",
                            ("name", "ilike", search),
                            ("description", "ilike", search),
                        ],
                    ]
                )
            # if search_in in ("customer", "all"):
            #     search_domain = OR([search_domain, [("partner_id", "ilike", search)]])
            if search_in in ("message", "all"):
                search_domain = OR(
                    [search_domain, [("message_ids.body", "ilike", search)]]
                )
            if search_in in ("stage", "all"):
                search_domain = OR([search_domain, [("stage_id", "ilike", search)]])
            # if search_in in ("project", "all"):
            #     search_domain = OR([search_domain, [("project_id", "ilike", search)]])
            domain += search_domain

        # TODO: Show tickets from partner's company?
        # default domain
        domain += [
            ("project_id", "=", helpdesk_project.id),
        ]
        # task count
        task_count = request.env["project.task"].search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/tickets",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
                "filterby": filterby,
                "groupby": groupby,
                "search_in": search_in,
                "search": search,
            },
            total=task_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        if groupby == "project":
            order = (
                "project_id, %s" % order
            )  # force sort on project first to group by project in view
        if groupby == "stage":
            order = (
                "stage_id, %s" % order
            )  # force sort on stage first to group by stage in view

        tasks = request.env["project.task"].search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_tasks_history"] = tasks.ids[:100]

        if groupby == "project":
            grouped_tasks = [
                request.env["project.task"].concat(*g)
                for k, g in groupbyelem(tasks, itemgetter("project_id"))
            ]
        if groupby == "stage":
            grouped_tasks = [
                request.env["project.task"].concat(*g)
                for k, g in groupbyelem(tasks, itemgetter("stage_id"))
            ]
        else:
            grouped_tasks = [tasks] if tasks else []

        values.update(
            {
                "date": date_begin,
                "is_ticket": True,
                "date_end": date_end,
                "grouped_tasks": grouped_tasks,
                "page_name": "tickets",
                "default_url": "/my/tickets",
                "pager": pager,
                "searchbar_sortings": searchbar_sortings,
                "searchbar_groupby": searchbar_groupby,
                "searchbar_inputs": searchbar_inputs,
                "search_in": search_in,
                "search": search,
                "sortby": sortby,
                "groupby": groupby,
                "searchbar_filters": OrderedDict(sorted(searchbar_filters.items())),
                "filterby": filterby,
            }
        )
        return request.render("project.portal_my_tasks", values)

    @http.route(
        ["/my/tasks", "/my/tasks/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_tasks(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        filterby=None,
        search=None,
        search_in="content",
        groupby=None,
        **kw
    ):
        res = super().portal_my_tasks(
            page,
            date_begin,
            date_end,
            sortby,
            filterby,
            search,
            search_in,
            groupby,
            **kw
        )
        helpdesk_project = (
            request.env["project.project"]
            .sudo()
            .search([("helpdesk_project", "=", True)])
        )
        if res.qcontext.get("grouped_tasks"):
            real_tasks = request.env["project.task"]
            for task in res.qcontext["grouped_tasks"]:
                if task.project_id.id != helpdesk_project.id:
                    real_tasks |= task

            res.qcontext.update(
                {
                    "grouped_tasks": [real_tasks] if real_tasks else [],
                }
            )

        return res

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
            return request.redirect("/my/task/{}".format(ticket_id))

        # ensure attachment are accessible with access token inside template
        for attachment in task_sudo.attachment_ids:
            attachment.generate_access_token()
        values = self._task_get_page_view_values(task_sudo, access_token, **kw)
        values["page_name"] = "ticket"
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
            _logger.info("Creating a new ticket from portal user...")
            request.env["project.task"].sudo().create(
                {
                    "name": subject,
                    "description": description,
                    "partner_id": current_user.partner_id.id,
                    "project_id": helpdesk_project.id,
                }
            )
        return request.redirect("/my/tickets")

    def _task_get_page_view_values(self, task, access_token, **kwargs):
        values = super()._task_get_page_view_values(task, access_token, **kwargs)
        # Prevent timesheets on task view, since sudo used we have to pop elements
        values.pop("timesheets")
        values.pop("timesheets_by_subtask")
        return values

    @http.route(
        ["/my/project/<int:project_id>"], type="http", auth="public", website=True
    )
    def portal_my_project(self, project_id=None, access_token=None, **kw):
        # Prevent project view
        return request.redirect("/my")

    @http.route(["/my/task/<int:task_id>"], type="http", auth="user", website=True)
    def portal_my_task(self, task_id, access_token=None, **kw):
        """No access with only access token (change auth to user)"""
        return super().portal_my_task(task_id, access_token, **kw)


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
        **kw
    ):
        """Prevent user to check timesheets from portal"""
        return request.redirect("/my")
