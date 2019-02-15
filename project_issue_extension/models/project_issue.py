# -*- coding: utf-8 -*-

# 1. Standard library imports:
import logging
import re
from datetime import datetime

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models, _, SUPERUSER_ID

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
    doc_count = fields.Integer(
        compute='_compute_attached_docs_count',
        string='Number of documents attached',
        help='Number of documents attached to this record',
    )
    customer_issue_count = fields.Integer(
        compute='_compute_customer_issue_count',
        string='Number of issues on customer',
        help='Number of issues on customer',
    )
    description = fields.Html(
        string='Description',
    )
    stage_change_ids = fields.One2many(
        'project.issue.stage.change',
        'issue_id',
        string='Stage changes',
        readonly=True,
        help="Issue's stage changes",
    )
    # Remove thread tracking from fields that aren't needed
    kanban_state = fields.Selection(track_visibility=False)
    stage_id = fields.Many2one(track_visibility=False)
    project_id = fields.Many2one(track_visibility=False)
    subject = fields.Char(
        string='Subject',
        help='Issue subject for emails',
        required=True,
        readonly=True,
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_attached_docs_count(self):
        attachment = self.env['ir.attachment']
        for record in self:
            record.doc_count = attachment.search_count([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id),
            ])


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
        When project issue is created:
            - issue number is set
            - Auto reply is sent to the customer
        """
        print "-------------"
        print vals
        if not vals.get('issue_number'):
            vals['issue_number'] = self.env['ir.sequence'].sudo().next_by_code('project.issue')
        # Create patner if it doesn't exist
        if not vals.get('partner_id'):
            vals['partner_id'] = self._fetch_partner(vals)
        if not vals.get('date'):
            vals['date'] = datetime.today()
        if not vals.get('subject'):
            # Hardcoded to Finnish since we don't want the subject to ever change
            vals['subject'] = 'Tukipyyntö' + " #" + vals['issue_number'] + ": " + vals['name']
        issue = super(ProjectIssue, self).create(vals)
        # Add customer to followers
        if issue.partner_id:
            issue.message_subscribe([issue.partner_id.id])
        # TODO: If issue created from backend, post a message to thread
        # which is sent to customer (autoresponse)
        print "------ CREATE LOPPUU-------------"
        return issue


    @api.multi
    def write(self, values):
        """
        Add a new row to stage_change_ids, when stage is changed
        """
        stage_id = values.get('stage_id')
        # Create new line to stage change log
        if stage_id:
            values['stage_change_ids'] = [(0, _, {'stage': stage_id})]
        return super(ProjectIssue, self).write(values)


    # 7. Action methods
    @api.multi
    def attachment_tree_view(self):
        """
        Issue's attachments
        """
        self.ensure_one()
        domain = [
            ('res_model', '=', self._name), ('res_id', 'in', self.ids),
        ]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,kanban,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached to the issues.</p><p>
                        Send messages or log internal notes with attachments to link
                        documents to issues.
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }


    @api.multi
    def customer_issues_tree_view(self):
        """
        Customer's issues
        """
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
    def _fetch_partner(self, vals):
        """
        Get partner
        """
        email_from = vals.get('email_from')
        name_regex = re.compile("^[^<]+")
        email_regex = re.compile(r"[\w\.-]+@[\w\.-]+")

        try:
            name = name_regex.findall(email_from)[0]
            email = email_regex.findall(email_from)[0].lower()
        except IndexError:
            # The email has no name information
            name = email_from
            email = email_from

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
        """
        print "TÄMÄ ON MESSAGE_NEW1"
        res = super(ProjectIssue, self).message_new(msg, custom_values)
        issue = self.browse(res)
        print "TÄMÄ ON MESSAGE_NEW"
        if not issue.description:
            issue.description = msg.get('body', False)
        return res


    @api.model
    def _init_issue_numbers(self):
        """
        Initialize issue numbers when module is installed
        """
        issues = self.search([('issue_number', '=', False)])
        for issue in issues:
            issue.issue_number = self.env['ir.sequence'].next_by_code('project.issue')
            issue.subject = 'Tukipyyntö' + " #" + issue.issue_number + ": " + issue.name
            _logger.debug("Setting issue number and subject for %s", issue.issue_number)


    @api.model
    def _init_issue_subjects(self):
        """
        Initialize issue subjects when module is installed
        """
        issues = self.search([('subject', '=', False)])
        for issue in issues:
            issue.subject = 'Tukipyyntö' + " #" + issue.issue_number + ": " + issue.name
            _logger.debug("Setting issue subject for %s", issue.subject)


    @api.multi
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, subtype=None, **kwargs):
        """
        When message is posted, check if it's the first message and send autoreply if it was
        """
        self.ensure_one()
        messages = len(self.message_ids)
        mail_message = super(ProjectIssue, self).message_post(subtype=subtype, **kwargs)
        if messages == 0:
            self.send_issue_autoreply()
        return mail_message


    @api.multi
    def send_issue_autoreply(self):
        """
        Send autoreply email regarding issue "Issue received" to submitter and CCs
        """
        self.ensure_one()
        settings = self.env['project.issue.settings'].sudo().search([
            ('company_id', '=', self.company_id.id),
        ], limit=1)
        message = self.env['mail.message'].sudo().search([
            ('res_id', '=', self.id),
            ('model', '=', 'project.issue'),
        ], limit=1)
        # TODO: Change email_cc to partners and use that??
        mail_values = {
            'mail_message_id': message.id,
            'mail_server_id': message.mail_server_id.id,
            'auto_delete': True,
            'references': False,
            'email_cc': self.email_cc,
            'email_from': settings.email_reply_to,
            'reply_to': settings.email_reply_to,
        }
        print mail_values
        self.partner_id._notify_send(message.body, self.subject, self.partner_id, **mail_values)
