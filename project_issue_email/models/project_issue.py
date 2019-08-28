# -*- coding: utf-8 -*-

# 1. Standard library imports:
import logging
import re
from datetime import datetime
import base64

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models, _
from odoo import SUPERUSER_ID

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


_logger = logging.getLogger(__name__)


class ProjectIssue(models.Model):

    # 1. Private attributes
    _inherit = 'project.issue'

    _sql_constraints = [
        ('issue_number', 'unique(issue_number)', _('This issue number is already in use.'))
    ]

    # 2. Fields declaration
    issue_number = fields.Char(
        string='Issue number',
        help='Number assigned to issue as identifier',
    )
    customer_issue_count = fields.Integer(
        compute='_compute_customer_issue_count',
        string='Number of issues on customer',
        help='Number of issues on customer',
    )
    description = fields.Html(
        string='Description',
    )
    subject = fields.Char(
        string='Subject',
        help='Issue subject for emails',
        required=True,
        readonly=True,
    )
    issue_type = fields.Char(
        string='Issue type',
        help='How issue was created',
        readonly=True,
    )

    # 3. Default methods
    @api.model
    def default_get(self, fields):
        res = super(ProjectIssue, self).default_get(fields)
        company_id = self.env.user.company_id.id
        setting = self.env['project.issue.settings'].sudo().search([
            ('company_id', '=', company_id),
        ])
        res.update({
            'project_id': setting.project_id.id,
        })
        return res

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_customer_issue_count(self):
        for record in self:
            partner_id = record.partner_id.id
            record.customer_issue_count = self.search_count([
                ('partner_id', '=', partner_id),
            ])

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model
    def create(self, vals):
        """
        Set issue default values, remove email_cc (deprecated),
        generate subject, and add partners as followers.

        @param vals: dict of values
        @return: issue id
        """
        if not vals.get('issue_number'):
            vals['issue_number'] = self.env['ir.sequence'].sudo().next_by_code('project.issue')
        # Create patner if it doesn't exist
        if not vals.get('partner_id'):
            vals['partner_id'] = self._fetch_partner(vals.get('email_from'))
        if not vals.get('date'):
            vals['date'] = datetime.today()
        if not vals.get('subject'):
            # Hardcoded to Finnish since we don't want the subject to ever change
            vals['subject'] = u'Tukipyyntö #%s: %s' % (vals['issue_number'], vals['name'])
        if not vals.get('issue_type'):
            vals['issue_type'] = 'backend'
        if not vals.get('stage_id'):
            vals['stage_id'] = self.env['project.task.type'].sudo().search([
                ('issue_stage', '=', True),
                ('sequence', '=', 1),
            ], limit=1).id
        # Get default project from fetchmailserver -> settings -> project
        # if not supplied in vals
        fetchmail_server_id = self.env.context.get('fetchmail_server_id')
        if fetchmail_server_id and not vals.get('project_id'):
            mailserver = self.env['fetchmail.server'].sudo().browse(fetchmail_server_id)
            company_id = mailserver.company_id.id
            vals['project_id'] = self.env['project.issue.settings'].sudo().search([
                ('company_id', '=', company_id)
            ], limit=1).project_id.id

            vals['company_id'] = company_id
        issue = super(ProjectIssue, self).create(vals)
        # Add customer to followers
        if issue.partner_id:
            issue.message_subscribe([issue.partner_id.id])
        # If issue created from backend, post a message to thread
        # which is sent to customer (autoresponse)
        if issue.issue_type == 'backend':
            attachments = [(a['datas_fname'], base64.b64decode(a['datas']))
                           for a in issue.attachment_ids.sudo().read(['datas_fname', 'datas'])]
            issue.sudo().message_post(
                subject=issue.subject,
                message_type='comment',
                subtype='mt_comment',
                body=issue.description,
                attachments=attachments,
            )
        return issue

    @api.multi
    def write(self, vals):
        if vals.get('partner_id'):
            # Force-write partner email even when it's readonly
            partner_id = self.env['res.partner'].browse([vals['partner_id']])
            vals['email_from'] = partner_id.email

            # Unsubscribe/subscribe if partner is changed
            for record in self:
                # Remove current partner
                record.message_unsubscribe([record.partner_id.id])
                # Set the new partner as follower
                record.message_subscribe([vals.get('partner_id')])

        return super(ProjectIssue, self).write(vals)

    # 7. Action methods
    @api.multi
    def customer_issues_tree_view(self):
        """ Customer's issues """
        self.ensure_one()
        domain = [
            ('partner_id', '=', self.partner_id.id),
        ]
        return {
            'name': _("Customer's issues"),
            'domain': domain,
            'res_model': 'project.issue',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Issues are attached to customers.</p><p>
                    </p>'''),
            'limit': 80,
        }

    # 8. Business methods
    @api.model
    def _fetch_partner(self, email_recipient):
        """ Fetch partner from email """
        name_regex = re.compile("^[^<]+")
        email_regex = re.compile(r"[\w\.-]+@[\w\.-]+")

        try:
            name = name_regex.findall(email_recipient)[0]
            email = email_regex.findall(email_recipient)[0].lower()
        except IndexError:
            # The email has no name information
            name = email_recipient
            email = email_recipient

        email = re.sub(r'[<>]', "", email).lower()
        name = re.sub(r'["<>]', "", name)

        _logger.info("Fetching partner for email %s", email)

        partner_object = self.env['res.partner']
        existing_partner = partner_object.search([('email', '=ilike', email)], limit=1)
        if existing_partner:
            partner_id = existing_partner.id
        else:
            _logger.info("No partner found. Creating %s (%s)" % (name, email))
            partner_vals = dict()
            partner_vals['name'] = name
            partner_vals['email'] = email
            partner_id = partner_object.create(partner_vals).id
        return partner_id

    @api.model
    def message_new(self, msg, custom_values=None):
        """
        This method is called, when a new issue is starting from an email

        @param msg: message payload json
        @param custom_values: dict of values
        @return: issue id
        """
        defaults = {
            'issue_type': 'email'
        }
        if custom_values:
            defaults.update(custom_values)
        res = super(ProjectIssue, self).message_new(msg, custom_values=defaults)
        issue = self.browse(res)
        issue.update_other_recipients(msg)
        if not issue.description:
            issue.description = msg.get('body', False)
        return res

    @api.model
    def _init_issue_numbers(self):
        """ Initialize issue numbers when module is installed """
        issues = self.search([('issue_number', '=', False)])
        for issue in issues:
            issue.issue_number = self.env['ir.sequence'].next_by_code('project.issue')
            issue.subject = 'Tukipyyntö' + " #" + issue.issue_number + ": " + issue.name
            _logger.debug("Setting issue number and subject for %s", issue.issue_number)

    @api.model
    def _init_issue_subjects(self):
        """ Initialize issue subjects when module is installed """
        issues = self.search([('subject', '=', False)])
        for issue in issues:
            issue.subject = 'Tukipyyntö' + " #" + issue.issue_number + ": " + issue.name
            _logger.debug("Setting issue subject for %s", issue.subject)

    @api.multi
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, subtype=None, **kwargs):
        """
        When message is posted, check if it's the first message and
        add attachments to issue if it was the first message
        """
        self.ensure_one()
        messages = len(self.message_ids)
        mail_message = super(ProjectIssue, self).message_post(subtype=subtype, **kwargs)
        if messages == 0:
            # self.send_issue_autoreply()
            if len(self.attachment_ids) == 0 and len(mail_message.attachment_ids) != 0:
                self.attachment_ids = [(6, 0, mail_message.attachment_ids.ids)]
        return mail_message

    @api.multi
    def get_issue_autoreply_values(self, vals):
        """ Update values for autoreply """
        self.ensure_one()
        settings = self.env['project.issue.settings'].sudo().search([
            ('company_id', '=', self.company_id.id),
        ], limit=1)
        vals.update({
            'email_from': 'Tukipalvelu <%s>' % settings.email_reply_to,
            'reply_to': settings.email_reply_to,
            'subject': self.subject,
            'author_id': SUPERUSER_ID,
            'mail_server_id': settings.mail_server_id.id or None,
        })
        return vals
