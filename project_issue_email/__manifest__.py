# -*- coding: utf-8 -*-
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
    'name': 'Project Issue Email',
    'summary': 'Email modifications to Project Issue',
    'version': '10.0.0.19.4',
    'category': 'Project',
    'website': 'https://tawasta.fi',
    'author': 'Oy Tawasta Technologies Ltd.',
    'license': 'AGPL-3',
    'depends': [
        'email_template_qweb',
        'project_issue',
        'project_issue_attachment',
        'project_issue_code',
        'project_issue_menu',
        'project_issue_other_recipients',
        'project_issue_stage',
    ],
    'data': [
        'data/issue_subject_init.xml',
        'data/project_issue_settings_data.xml',
        'security/ir.model.access.csv',
        'views/fetchmail_server_form_view.xml',
        'views/project_issue_form.xml',
        'views/project_issue_search.xml',
        'views/project_issue_settings.xml',
        'views/project_issue_stage_change.xml',
        # 'views/assets.xml',
    ],
    'application': False,
    'installable': True,
    'qweb': [
        # 'static/src/xml/thread.xml',
    ],
}
