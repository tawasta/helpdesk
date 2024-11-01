/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";

publicWidget.registry.CreateTicketWidget = publicWidget.Widget.extend({
    selector: "#create_ticket_form",

    events: {
        "change .upload": "_onFileChange",
    },

    /**
     * Initializes the widget, sets up the editor, and manages the confirm button.
     */
    start: function () {
        const res = this._super.apply(this, arguments);
        
        // Initialize the rich text editor
        ClassicEditor.create(document.querySelector("#description"), {
            language: "fi",
        }).then((editor) => {
            this.editor = editor;
            editor.model.document.on("change:data", () => {
                const text = $.trim(editor.getData());
                this.$("#create_ticket_confirm_btn").toggleClass("disabled", !text);
            });
        });

        return res;
    },

    // --------------------------------------------------------------------------
    // Private
    // --------------------------------------------------------------------------

    /**
     * Handles file input changes, calculates file sizes, and displays file info.
     * @private
     */
    _onFileChange: function (event) {
        const $input = $(event.currentTarget).closest("input");
        const maxSize = $input.data("maxsize");
        const files = $input.prop("files");
        const fileCount = `${files.length} ${_t(" file(s) selected:")}`;
        const fileNameLabel = _t("File name: ");
        const fileSizeLabel = _t("File size: ");
        const fileTooBigLabel = _t("File size too big! Max size for file is ") + maxSize + "MB";
        
        let elements = `<p>${fileCount}</p><p id='file_sizes'>`;
        let fileTooBig = false;

        this.$("#files_info_div").addClass("d-none");

        for (let file of files) {
            let size = file.size > 1024 * 1024
                ? `${Math.round((file.size * 10) / (1000 * 1000)) / 10}MB`
                : `${Math.round((file.size * 10) / 1000) / 10}KB`;

            if (file.size > maxSize * 1000 * 1000) {
                fileTooBig = true;
                elements += `<strong>${fileTooBigLabel}</strong><br/>`;
            }

            elements += `${fileNameLabel}${file.name}, ${fileSizeLabel}${size}<br/>`;
        }
        elements += "</p>";
        
        this.$("#files_info_div").html(elements);
        this._updateFileStatus(fileTooBig);
    },

    /**
     * Updates the file information display and confirm button status.
     * @private
     */
    _updateFileStatus: function (fileTooBig) {
        if (fileTooBig) {
            this.$("#files_info_div")
                .removeClass("d-none alert-info")
                .addClass("alert-danger");
            this.$("#create_ticket_confirm_btn").addClass("disabled");
        } else {
            this.$("#files_info_div")
                .removeClass("d-none alert-danger")
                .addClass("alert-info");
            this.$("#create_ticket_confirm_btn").removeClass("disabled");
        }
    },
});

export default publicWidget.registry.CreateTicketWidget;
