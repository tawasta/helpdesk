##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
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

{
    "name": "Website Helpdesk",
    "summary": "Website Helpdesk",
    "version": "17.0.1.0.0",
    "category": "Project",
    "website": "https://gitlab.com/tawasta/odoo/helpdesk",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "portal",
        "project_helpdesk",
        "account",
        "contract",
        "sale",
        "hr_timesheet",
        "software_knowledge_base",
        "project_task_auto_reopen",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/project_task_views.xml",
        "views/project_task_type_views.xml",
        "views/portal_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_helpdesk/static/src/js/create_ticket.esm.js",
            "website_helpdesk/static/src/scss/styles.scss",
            "https://cdn.ckeditor.com/ckeditor5/36.0.1/classic/ckeditor.js",
            "https://cdn.ckeditor.com/ckeditor5/43.1.0/ckeditor5.css",
        ],
    },
}
