odoo.define('website_project_issue_form.create_issue', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var toastr = require('website_utilities.notifications').toastr;
    var loadingScreen = require('website_utilities.loader').loadingScreen;

    $(function() {
        // Check filesize and restrict filesize to under 20 MB
        $('#issue_attachment').on('change', function() {

            var file = $(this).prop('files')[0];
            var size = "";
            var msg = "";

            $('#fileTooBigDiv').addClass('hidden');
            $('#fileSizeOkDiv').addClass('hidden');
            
            if (file) {
                if (file.size > 1024 * 1024) {
                    size = (Math.round(file.size * 10 / (1024 * 1024))/10).toString() + 'MB';
                }
                else {
                    size = (Math.round(file.size * 10 / 1024)/10).toString() + 'KB';
                }      
            }

            // If file is over 20 MB, clear the element and give notifications
            if (file.size > (20 * 1024 * 1024)) {
                $(':file').filestyle('clear');
                $('#fileTooBigDiv').removeClass('hidden');
                $('#fileTooBig').text(size);
            } else {
                $('#fileSizeOkDiv').removeClass('hidden');
                $('#fileSizeOk').text(size);
            }
        });
        // Javascript translations don't work right after page has reloaded, but with a small timeout
        // the text can be translated
        setTimeout(function() {
            $(':file').filestyle({
                iconName: "fa fa-folder-open",
                buttonName: "btn-primary",
                buttonText: _t("Choose file"),
            });
        }, 500);
        
    });
    

});