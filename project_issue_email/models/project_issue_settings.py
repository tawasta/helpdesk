# -*- coding: utf-8 -*-
from odoo import fields, models


class ProjectIssueSettings(models.Model):

    _name = 'project.issue.settings'
    _description = "Project issue settings"

    def _default_email_issue_received(self):
        template_id = self.env.ref(
            'project_issue_email.project_issue_email_received_autoreply')

        if template_id:
            return template_id.id

    def _default_email_issue_reply(self):
        template_id = self.env.ref(
            'project_issue_email.project_issue_email_reply')

        if template_id:
            return template_id.id

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        help='Company for which these settings are defined',
        default=lambda self: self.env.user.company_id.id,
    )
    email_reply_to = fields.Char(
        string='Helpdesk reply to email address',
        size=256,
        help='Reply to email address for the company',
        default=lambda self: self.env.user.company_id.email,
    )
    email_issue_received = fields.Many2one(
        'mail.template',
        string='Email template for autoreply',
        help='Auto reply email when customer submits a new issue',
        default=_default_email_issue_received,
        domain=[('model_id', '=', 'project.issue')],
    )
    email_issue_reply = fields.Many2one(
        'mail.template',
        string='Email template for new reply',
        help='When employee sends a new message from issue, '
             'this template is used',
        default=_default_email_issue_reply,
        domain=[('model_id', '=', 'project.issue')],
    )
    project_id = fields.Many2one(
        'project.project',
        string='Helpdesk project',
        help='Currently used helpdesk project for the company',
    )
    mail_server_id = fields.Many2one(
        'ir.mail_server',
        string='Force sending mail server',
        help='Force the sending mail server for this company',
    )
