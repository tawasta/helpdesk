# -*- coding: utf-8 -*-
import lxml
from lxml import etree
import logging
from odoo import api, models
_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):

    _inherit = 'mail.thread'

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None, custom_values=None):
        """
        Attempt to map the message to the original issue

        :param string message: an email.message instance
        :param dict message_dict: dictionary holding parsed message variables
        :param string model: the fallback model to use if the message does not match
            any of the currently configured mail aliases (may be None if a matching
            alias is supposed to be present)
        :type dict custom_values: optional dictionary of default field values
            to pass to ``message_new`` if a new record needs to be created.
            Ignored if the thread record already exists, and also if a matching
            mail.alias was found (aliases define their own defaults)
        :param int thread_id: optional ID of the record/thread from ``model`` to
            which this mail should be attached. Only used if the message does not
            reply to an existing thread and does not match any mail alias.
        :return: list of routes [(model, thread_id, custom_values, user_id, alias)]

        :raises: ValueError, TypeError
        """
        res = super(MailThread, self).message_route(
            message, message_dict, model, thread_id, custom_values)
        # If the fetched message is an issue and isnt' matched,
        # check if the issue exists with issue number
        if res and res[0][0] == 'project.issue':
            if res[0][1]:
                # Add ccs to existing issue
                email_ccs = message_dict.get('cc')
                if email_ccs:
                    issue = self.env['project.issue'].browse(res[0][1])
                    issue.update_other_recipients(message_dict)
        return res

    # @api.multi
    # def _message_auto_subscribe_notify(self, partner_ids):
    #     """
    #     Inherited cores function and extended to set email template for assiged to -action on issues.

    #     :param partner_ids : the list of partner to add as needaction partner of the last message
    #         (This excludes the current partner)
    #     """
    #     if not partner_ids:
    #         return
    #     if self.env.context.get('mail_auto_subscribe_no_notify'):
    #         return
    #     # send the email only to the current record and not all the ids matching active_domain !
    #     # by default, send_mail for mass_mail use the active_domain instead of active_ids.
    #     if 'active_domain' in self.env.context:
    #         ctx = dict(self.env.context)
    #         ctx.pop('active_domain')
    #         self = self.with_context(ctx)
    #     for record in self:
    #         email_template = 'mail.message_user_assigned'
    #         if record._name == 'project.issue':
    #             # TODO TAWASTA: Assigned to -email template??
    #             pass
    #         record.message_post_with_view(
    #             email_template,
    #             composition_mode='mass_mail',
    #             partner_ids=[(4, pid) for pid in partner_ids],
    #             auto_delete=True,
    #             auto_delete_message=True,
    #             parent_id=False,
    #             subtype_id=self.env.ref('mail.mt_note').id
    #         )

    @api.model
    def _message_extract_payload_postprocess(self, message, body, attachments):
        """
        Strip previous HTML messages from email

        :param message: email message
        :param body: body extracted from the email message
        :param attachments: attachments related to email
        :returns: body, attachments
        """
        body, attachments = super(MailThread, self)._message_extract_payload_postprocess(message, body, attachments)
        if not body:
            return body, attachments
        root = lxml.html.fromstring(body)
        postprocessed = False
        to_remove = []
        for node in root.iter():
            # Gmail / Mac email parsing
            if node.tag == 'blockquote' and node.getprevious() and node.getprevious().get('class') != 'moz-cite-prefix':
                postprocessed = True
                parent = node.getparent()
                to_remove.append(parent.getprevious())
                to_remove.append(parent)
            # Gmail / Mac parsing ends
            # Thunderbird parsing
            if node.tag == 'blockquote' and node.getprevious() and node.getprevious().get('class') == 'moz-cite-prefix':
                postprocessed = True
                to_remove.append(node.getprevious())
                to_remove.append(node)
            # Thunderbird ends
            # Outlook parsing: remove blockquote from Outlook
            if node.tag == 'div' and node.get('id') == 'appendonsend':
                postprocessed = True
                to_remove.append(node)
                to_remove.append(node.getnext())
            if node.tag == 'div' and node.get('id', '').endswith('divRplyFwdMsg'):
                postprocessed = True
                to_remove.append(node)
            if node.tag == 'div' and node.get('id', '').endswith('_issue_reply'):
                postprocessed = True
                to_remove.append(node)
            # Outlook ends
        for node in to_remove:
            parent = node.getparent()
            if parent:
                parent.remove(node)
        if postprocessed:
            body = etree.tostring(root, pretty_print=False, encoding='UTF-8')
        return body, attachments
