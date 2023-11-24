odoo.define("website_helpdesk.portal.chatter", function (require) {
    "use strict";

    var core = require("web.core");
    var _t = core._t;
    var time = require("web.time");

    var portalChatter = require("portal.chatter");
    var PortalChatter = portalChatter.PortalChatter;

    PortalChatter.include({
        // --------------------------------------------------------------------------
        // Public
        // --------------------------------------------------------------------------

        /**
         * Update the messages datetime format
         *
         * @param {Array<Object>} messages
         * @returns {Array}
         */
        preprocessMessages: function (messages) {
            _.each(messages, function (m) {
                m.author_avatar_url = _.str.sprintf(
                    "/web/image/%s/%s/author_avatar/50x50",
                    "mail.message",
                    m.id
                );
                m.published_date_str = _.str.sprintf(
                    _t("Published on %s"),
                    moment(time.str_to_datetime(m.date)).format("D.M.YYYY HH:mm")
                );
            });
            return messages;
        },
    });
});
