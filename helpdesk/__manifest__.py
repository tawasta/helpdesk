# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2019- Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
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
    'name': 'Help Desk',
    'summary': 'Help Desk core bundle',
    'version': '12.0.1.0.0',
    'category': 'Tools',
    'website': 'http://www.tawasta.fi',
    'author': 'Oy Tawasta Technologies Ltd.',
    'license': 'AGPL-3',
    'depends': [
        'project_issue_attachment',
        'project_issue_email',
        'project_issue_opportunity',
        'project_issue_other_recipients',
        'project_issue_security',
        'project_issue_sheet_extension',
        'project_issue_stage',
        'website_project_issue_extension',
        'website_project_issue_form',
        'website_project_issue_hide_project',
        'website_project_issue_redirect',
        'mail_debrand',
    ],
    'application': True,
    'installable': False,
}
