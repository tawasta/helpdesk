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
    "name": "Project Task Email",
    "summary": "Email modifications to Project Task",
    "version": "14.0.1.2.4",
    "category": "Project",
    "website": "https://gitlab.com/tawasta/odoo/helpdesk",
    "author": "Tawasta",
    "license": "AGPL-3",
    "depends": [
        "email_template_qweb",
        "mail",
        "mail_layout_force",
        "project",
        "project_task_code",
    ],
    "data": [
        "data/mail_helpdesk_autoreply.xml",
        "data/mail_layout.xml",
        "views/fetchmail_server_form.xml",
        "views/project_project_form.xml",
    ],
    "application": False,
    "installable": True,
    "qweb": [],
}
