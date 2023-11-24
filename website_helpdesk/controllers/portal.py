import logging
from collections import OrderedDict
from operator import itemgetter

from odoo import _, http
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
        partner = request.env.user.partner_id
        if "support_tickets_count" in counters:
            project_id = (
                request.env["project.project"]
                .sudo()
                .search([("helpdesk_project", "=", True)])
            )
            stages_ids = (
                request.env["project.task.type"].sudo().search([("fold", "=", False)])
            )
            # Show tickets from partner's company
            values["support_tickets_count"] = (
                request.env["project.task"]
                .sudo()
                .search_count(
                    [
                        ("project_id", "=", project_id.id),
                        ("partner_id.parent_id", "=", partner.parent_id.id),
                        ("stage_id", "in", stages_ids.ids),
                    ]
                )
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
        partner = request.env.user.partner_id
        searchbar_sortings = {
            "date": {"label": _("Newest"), "order": "create_date desc"},
            "name": {"label": _("Title"), "order": "name"},
            "stage": {"label": _("Stage"), "order": "stage_id, project_id"},
            #            "project": {"label": _("Project"), "order": "project_id, stage_id"},
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
            #            "project": {"input": "project", "label": _("Search in Project")},
            "all": {"input": "all", "label": _("Search in All")},
        }
        searchbar_groupby = {
            "none": {"input": "none", "label": _("None")},
            "project": {"input": "project", "label": _("Project")},
            "stage": {"input": "stage", "label": _("Stage")},
        }

        # extends filterby criteria with project the customer has access to
        project = (
            request.env["project.project"]
            .sudo()
            .search([("helpdesk_project", "=", True)])
        )
        searchbar_filters.update(
            {
                str(project.id): {
                    "label": project.name,
                    "domain": [("project_id", "=", project.id)],
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

        stages_ids = (
            request.env["project.task.type"].sudo().search([("fold", "=", False)])
        )
        # TODO: Show tickets from partner's company?
        # default domain
        domain += [
            ("project_id", "=", project.id),
            ("partner_id.parent_id", "=", partner.parent_id.id),
            ("stage_id", "in", stages_ids.ids),
        ]
        # task count
        task_count = request.env["project.task"].sudo().search_count(domain)
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

        tasks = (
            request.env["project.task"]
            .sudo()
            .search(
                domain, order=order, limit=self._items_per_page, offset=pager["offset"]
            )
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
            grouped_tasks = [tasks]

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
        ["/my/ticket/<int:ticket_id>"], type="http", auth="public", website=True
    )
    def portal_my_ticket(self, ticket_id, access_token=None, **kw):
        partner = request.env.user.partner_id
        task_sudo = request.env["project.task"].browse([ticket_id]).sudo()

        stages_ids = (
            request.env["project.task.type"].sudo().search([("fold", "=", False)])
        )
        # TODO: Show tickets from partner's company?
        task = (
            request.env["project.task"]
            .sudo()
            .search(
                [
                    ("id", "=", ticket_id),
                    ("partner_id.parent_id", "=", partner.parent_id.id),
                    ("project_id.helpdesk_project", "=", True),
                    ("stage_id", "in", stages_ids.ids),
                ]
            )
        )
        if not task:
            return request.redirect("/my")

        # ensure attachment are accessible with access token inside template
        for attachment in task_sudo.attachment_ids:
            attachment.generate_access_token()
        values = self._task_get_page_view_values(task_sudo, access_token, **kw)
        values["page_name"] = "ticket"
        return request.render("project.portal_my_task", values)

    def _task_get_page_view_values(self, task, access_token, **kwargs):
        values = super()._task_get_page_view_values(task, access_token, **kwargs)
        # Prevent timesheets on task view, since sudo used we have to pop elements
        values.pop("timesheets")
        values.pop("timesheets_by_subtask")
        return values


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
