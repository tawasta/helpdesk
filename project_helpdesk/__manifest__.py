##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2019- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
    "name": "Project Helpdesk",
    "summary": "Project Helpdesk core bundle",
    "version": "14.0.1.3.2",
    "category": "Tools",
    "website": "https://gitlab.com/tawasta/odoo/helpdesk",
    "author": "Tawasta",
    "license": "AGPL-3",
    "depends": [
        "project_task_auto_reopen",
        "project_task_email",
        "mail_highlight",
    ],
    "application": True,
    "installable": True,
    "data": [
        "views/project_form.xml",
        "views/project_menu.xml",
        "views/project_task.xml",
        "views/project_task_menu.xml",
        "data/project_task_data.xml",
    ],
}
