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
            var max_size = $(this).data('maxsize');

            $('#fileTooBigDiv').addClass('hidden');
            $('#fileSizeOkDiv').addClass('hidden');
            
            if (file) {
                if (file.size > 1024 * 1024) {
                    size = (Math.round(file.size * 10 / (1000 * 1000))/10).toString() + 'MB';
                }
                else {
                    size = (Math.round(file.size * 10 / 1000)/10).toString() + 'KB';
                }      
            }

            // If file is larger than max_size, clear the element and give notifications
            if (file.size > (max_size * 1000 * 1000)) {
                $('#issue_attachment').val('');
                $('#fileTooBigDiv').removeClass('hidden');
                $('#fileTooBig').text(size);
            } else {
                $('#fileSizeOkDiv').removeClass('hidden');
                $('#fileSizeOk').text(size);
            }
        }); 
    });
});