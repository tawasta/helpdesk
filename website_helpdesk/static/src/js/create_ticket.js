odoo.define("website_helpdesk.create_ticket", function (require) {
    "use strict";

    var core = require("web.core");
    var _t = core._t;

    $(function () {
        // eslint-disable-next-line no-undef
        ClassicEditor.create(document.querySelector("#description"), {
            language: "fi",
        }).then((editor) => {
            editor.model.document.on("change:data", () => {
                var text = $.trim(editor.getData());
                $("#create_ticket_confirm_btn").toggleClass("disabled", !text);
            });
        });
        $(".upload").on("change", function (evt) {
            var $input = $(evt.currentTarget).closest("input");
            var size = "";
            var elements = "";
            var files = $input.prop("files");
            var fileCount = files.length.toString() + _t(" file(s) selected:");
            var fileNameLabel = _t("File name: ");
            var fileSizeLabel = _t("File size: ");
            var maxSize = $(this).data("maxsize");
            var fileTooBigLabel =
                _t("File size too big! Max size for file is ") + maxSize + "MB";
            var fileTooBig = false;

            $("#files_info_div").addClass("d-none");
            elements += "<p>" + fileCount + "</p><p id='file_sizes'>";
            for (var i = 0; i < files.length; ++i) {
                var file = files[i];
                if (file.size > 1024 * 1024) {
                    size =
                        (Math.round((file.size * 10) / (1000 * 1000)) / 10).toString() +
                        "MB";
                } else {
                    size = (Math.round((file.size * 10) / 1000) / 10).toString() + "KB";
                }
                // If file is larger than max_size, clear the element and give notifications
                if (file.size > maxSize * 1000 * 1000) {
                    fileTooBig = true;
                    elements += "<strong>" + fileTooBigLabel + "</strong><br/>";
                    elements +=
                        fileNameLabel +
                        file.name +
                        ", " +
                        fileSizeLabel +
                        size +
                        "<br/><br/>";
                } else {
                    elements +=
                        fileNameLabel +
                        file.name +
                        ", " +
                        fileSizeLabel +
                        size +
                        "<br/>";
                }
            }
            elements += "</p>";
            if (fileTooBig) {
                $("#files_info_div")
                    .removeClass("d-none alert-info")
                    .addClass("alert-danger");
                $("#create_ticket_confirm_btn").addClass("disabled");
            } else {
                $("#files_info_div")
                    .removeClass("d-none alert-danger")
                    .addClass("alert-info");
                $("#create_ticket_confirm_btn").removeClass("disabled");
            }
            $("#files_info_div").html(elements);
        });
    });
});
