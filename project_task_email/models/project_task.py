import logging
import re
from datetime import datetime
import base64
from odoo import api, fields, models, _
from odoo import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):

    # 1. Private attributes
    _inherit = 'project.task'

    # 2. Fields declaration
    '''
    Duplicate with task_count and task_ids, but they count ALL tasks    
    customer_issue_count = fields.Integer(
        compute='_compute_customer_issue_count',
        string='Number of issues on customer',
        help='Number of issues on customer',
    )
    
    def _compute_customer_issue_count(self):
        for record in self:
            partner_id = record.partner_id.id
            record.customer_issue_count = self.search_count([
                ('partner_id', '=', partner_id),
            ])    
    '''

    subject = fields.Char(
        string='Subject',
        help='Task subject for emails',
        compute='_compute_subject',
    )

    issue_type = fields.Char(
        string='Issue type',
        help='How issue was created',
        readonly=True,
    )

    latest_message_id = fields.Many2one(
        comodel_name='mail.message',
        string='Latest message',
        help='Latest message (in thread)',
        compute='_compute_latest_message',
    )
    previous_message_id = fields.Many2one(
        comodel_name='mail.message',
        string='Previous message',
        help='Previous message (in thread)',
        compute='_compute_previous_message',
    )

    # 3. Default methods

    # 4. Compute and search fields
    def _compute_subject(self):
        """ Compute task subjects for helpdesk """
        for record in self:
            record.subject = _("Issue {}").format(record.display_name)

    def _compute_latest_message(self, offset=0):
        """ Search the latest message """
        mail_message = self.env['mail.message'].sudo()

        for record in self:
            latest_message_id = mail_message.search([
                ('res_id', '=', record.id),
                ('model', '=', self._name),
                ('subtype_id.internal', '=', False),
                ('message_type', '!=', 'notification'),
            ], limit=1, offset=offset)

            record.latest_message_id = latest_message_id.id

    def _compute_previous_message(self):
        """ Search the message that precedes the latest message """

        for record in self:
            record.previous_message_id = \
                self._compute_latest_message(offset=1).id

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model
    def create(self, vals):

        # Get default project from fetchmail server, if not supplied in vals
        fetchmail_server_id = self.env.context.get('fetchmail_server_id')
        if fetchmail_server_id and not vals.get('project_id'):
            mail_server = \
                self.env['fetchmail.server'].sudo().browse(fetchmail_server_id)
            vals['company_id'] = mail_server.company_id.id or \
                mail_server.project_id.company_id.id
            vals['project_id'] = \
                mail_server.project_id and mail_server.project_id.id or False

        res = super(ProjectTask, self).create(vals)

        return res
    '''
    10.0 create
    @api.model
    def create(self, vals):
        """
        Set issue default values, remove email_cc (deprecated),
        generate subject, and add partners as followers.

        @param vals: dict of values
        @return: issue id
        """
        # Create issue code
        if vals.get('issue_code', '/') == '/':
            vals['issue_code'] = self.env['ir.sequence'].next_by_code(
                'project.issue') or '/'
        # Create partner if it doesn't exist
        if not vals.get('partner_id'):
            vals['partner_id'] = self._fetch_partner(vals.get('email_from'))
        if not vals.get('date'):
            vals['date'] = datetime.today()
        if not vals.get('subject'):
            # Hardcoded to Finnish since we don't want the subject to ever change
            vals['subject'] = u'Tukipyyntö #%s: %s' % (vals['issue_code'], vals['name'])
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

        # Unsubscribe admin
        issue.message_unsubscribe(
            [self.env['res.users'].browse([SUPERUSER_ID]).partner_id.id])

        # Post an auto-response message to thread
        attachments = [(a['datas_fname'], base64.b64decode(a['datas']))
                       for a in issue.attachment_ids.sudo().read(['datas_fname', 'datas'])]

        if vals.get('issue_type') != 'email':
            # Send an automated message for issues created from backend
            # Post auto-reply
            issue.message_post(
                body=vals['description'],
                subject=vals['subject'],
                message_type='email',
                subtype='mt_comment',
                attachments=attachments,
                # Only send the auto-reply to partner.
                # CC-recipients don't necessarily need it
                partner_ids=[issue.partner_id.id],
            )
        return issue
    '''

    '''
    @api.multi
    def write(self, vals):
        if vals.get('partner_id'):
            # Force-write partner email even when it's readonly
            partner_id = self.env['res.partner'].browse([vals['partner_id']])
            vals['email_from'] = partner_id.email

        for record in self:
            # Unsubscribe/subscribe if partner is changed
            if vals.get('partner_id'):
                # Remove current partner
                record.message_unsubscribe([record.partner_id.id])
                # Set the new partner as follower
                record.message_subscribe([vals.get('partner_id')])

            # Auto-assign the issue on stage change, if no assignee is set
            if vals.get('stage_id') and not vals.get(
                    'user_id') and not record.user_id:
                record.user_id = self.env.user.id

        return super(ProjectIssue, self).write(vals)
        '''

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
            'res_model': 'project.task',
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
    def message_new(self, msg, custom_values=None):
        """
        This method is called, when a new issue is starting from an email

        @param msg: message payload json
        @param custom_values: dict of values
        @return: issue id
        """
        defaults = {
            'issue_type': 'email',
            'description': msg.get('body'),
        }
        if custom_values:
            defaults.update(custom_values)
        res = super(ProjectTask, self).message_new(msg, custom_values=defaults)

        if not res.description:
            res.description = msg.get('body', False)

        return res

    @api.multi
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, *args, **kwargs):

        values = kwargs

        # Use custom notification layout
        values['notif_layout'] = \
            'project_task_email.message_notification_helpdesk'

        # Signature/no signature
        values['add_sign'] = True

        return super(ProjectTask, self).message_post(
            *args,
            **values,
        )

    @api.multi
    def message_post_with_template(self, template_id, **kwargs):
        values = kwargs

        # Use custom notification layout
        values['notif_layout'] = \
            'project_task_email.message_notification_helpdesk'

        # Signature/no signature
        values['add_sign'] = True

        return super(ProjectTask, self).message_post_with_template(
            template_id,
            **values,
        )
