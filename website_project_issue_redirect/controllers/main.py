# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


class WebsiteLogin(Website):

    @http.route()
    def web_login(self, redirect=None, *args, **kw):
        response = super(Website, self).web_login(redirect=redirect, *args, **kw)
        if not redirect and request.params['login_success']:
            if request.env['res.users'].browse(request.uid).has_group('project_issue_security.project_issue_group_portal_user'):
                redirect = '/my/issues?' + request.httprequest.query_string

            elif request.env['res.users'].browse(request.uid).has_group('base.group_user'):
                redirect = '/web?' + request.httprequest.query_string

            else:
                redirect = '/'

            return http.redirect_with_hash(redirect)
        return response
