import lxml
from lxml import etree
import logging
from odoo import api, models
_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):

    _inherit = 'mail.thread'

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
            node.getparent().remove(node)
        if postprocessed:
            body = etree.tostring(root, pretty_print=False, encoding='UTF-8')
        return body, attachments
