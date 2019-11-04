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
    'name': 'Project Issue Stage',
    'summary': 'Add stages changes records to issue',
    'version': '10.0.1.1.0',
    'category': 'Project',
    'website': 'https://tawasta.fi',
    'author': 'Oy Tawasta Technologies Ltd.',
    'license': 'AGPL-3',
    'depends': [
        'project_issue',
        'project_issue_menu',
        'project_stage_closed',
    ],
    'data': [
        'data/project_task_type.xml',
        'security/ir.model.access.csv',
        'views/project_issue_form.xml',
        'views/project_issue_stage_change.xml',
        'views/project_task_type.xml',
    ],
    'application': False,
    'installable': True,
}
