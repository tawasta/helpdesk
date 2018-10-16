odoo.define('website_project_issue_form.create_issue', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var toastr = require('website_utilities.notifications').toastr;
    var loadingScreen = require('website_utilities.loader').loadingScreen;

    $(function() {
        // Check filesize and restrict filesize to under 20 MB
        $('#issue_attachments').on('change', function() {
            var files = $(this).prop('files');
            var size = '';
            var msg = '';
            var maxSize = $(this).data('maxsize');
            var elements = '';
            var fileCount = files.length.toString() + _t(' file(s) selected');
            var fileNameLabel = _t('File name: ');
            var fileSizeLabel = _t('File size: ');
            var fileTooBigLabel = _t('File size too big! Max size for file is ') + maxSize + 'MB';
            var fileTooBig = false;

            $('#attachment_info_div').addClass('hidden');
            $('#submit_issue').prop('disabled', false);

            elements += '<p>' + fileCount + '</p><p id="file_sizes">';

            for (var i = 0; i < files.length; ++i) {
                var file = files[i];
                if (file.size > 1024 * 1024) {
                    size = (Math.round(file.size * 10 / (1000 * 1000)) / 10).toString() + 'MB';
                }
                else {
                    size = (Math.round(file.size * 10 / 1000) / 10).toString() + 'KB';
                }
                // If file is larger than max_size, clear the element and give notifications
                if (file.size > (maxSize * 1000 * 1000)) {
                    fileTooBig = true;
                    elements += '<strong>' + fileTooBigLabel + '</strong><br/>'
                    elements += fileNameLabel + file.name + ', ' + fileSizeLabel + size + '<br/><br/>';
                } else {
                    elements += fileNameLabel + file.name + ', ' + fileSizeLabel + size + '<br/>';
                }
            }
            elements += "</p>";
            if (fileTooBig) {
                $('#issue_attachments').val('');
                $('#submit_issue').prop('disabled', 'disabled');
                $('#attachment_info_div').removeClass('hidden alert-info').addClass('alert-danger');
            } else {
                $('#attachment_info_div').removeClass('hidden alert-danger').addClass('alert-info');
            }
            $('#attachment_info_div').html(elements);
        }); 
    });
});