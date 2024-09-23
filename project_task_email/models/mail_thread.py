##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2024- Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
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

# 1. Standard library imports:
import logging

import lxml

# 3. Odoo imports (openerp):
from odoo import models

# 2. Known third party imports:


# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):

    # 1. Private attributes
    _inherit = "mail.thread"

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def _message_parse_extract_payload_postprocess(self, message, payload_dict):
        """Parse only last message from email"""
        res = super()._message_parse_extract_payload_postprocess(message, payload_dict)
        if not res:
            return res

        body = res["body"]
        root = lxml.html.fromstring(body)
        postprocessed = False
        to_remove = []
        try:
            for node in root.iter():
                # Gmail / Mac email parsing
                if (
                    node is not None
                    and node.tag == "blockquote"
                    and node.getprevious().get("class") != "moz-cite-prefix"
                ):
                    postprocessed = True
                    parent = node.getparent()
                    to_remove.append(parent.getprevious())
                    to_remove.append(parent)
                # Gmail / Mac parsing ends
                # Thunderbird parsing
                if (
                    node is not None
                    and node.tag == "blockquote"
                    and node.getprevious().get("class") == "moz-cite-prefix"
                ):
                    postprocessed = True
                    to_remove.append(node.getprevious())
                    to_remove.append(node)
                # Thunderbird ends
                # Outlook parsing: remove blockquote from Outlook
                if node.tag == "div" and node.get("id") == "appendonsend":
                    postprocessed = True
                    to_remove.append(node)
                    to_remove.append(node.getnext())
                if node.tag == "div" and node.get("id", "").endswith("divRplyFwdMsg"):
                    postprocessed = True
                    to_remove.append(node)
                if node.tag == "div" and node.get("id", "").endswith("_issue_reply"):
                    postprocessed = True
                    to_remove.append(node)
                # Outlook ends
            for node in to_remove:
                if node is None:
                    continue
                parent = node.getparent()
                if (
                    parent is not None
                    and parent.tag != "body"
                    and parent.tag != "section"
                ):
                    parent.remove(node)
            if postprocessed:
                body = lxml.etree.tostring(root, pretty_print=False, encoding="UTF-8")

            res["body"] = body
        except (AttributeError, TypeError):
            _logger.error("Email import parsing error for, fall back to original...")

        return res

    # 8. Business methods
