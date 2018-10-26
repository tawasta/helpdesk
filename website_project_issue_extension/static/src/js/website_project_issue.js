odoo.define('website_project_issue_extension.issue', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var ajax = require('web.ajax');
    var loadingScreen = require('website_utilities.loader').loadingScreen;
    var toastr = require('website_utilities.notifications').toastr;
    
    $(function () {
        var submitPressed = false;
        // Initialize CKEditor
        CKEDITOR.plugins.addExternal('confighelper', 'https://martinezdelizarrondo.com/ckplugins/confighelper/');
        var lang = window.location.pathname.indexOf("fi_FI") >= 0 ? 'fi' : 'en';
        var config = {
            language: lang,
            toolbarGroups: [
            {"name":"basicstyles","groups":["basicstyles"]},
            {"name":"styles","groups":["styles"]},
            {"name":"paragraph","groups":["list","blocks"]},
            {"name":"links","groups":["links"]},
            {"name":"about","groups":["about"]}
            ],
            removePlugins: 'pastefromword,image,contextmenu,tabletools,tableselection',
            removeButtons: 'Underline,Strike,Subscript,Superscript,Anchor,Styles,Specialchar',
            extraPlugins: 'confighelper'
        };
        var comment = CKEDITOR.replace('comment', config);

        // If unsaved changes, ask confirmation
        $(window).on('beforeunload', function(){
            var text = $.trim(comment.document.getBody().getText());
            var placeholder = $('#comment').attr('placeholder');
            if (text && text != placeholder && !submitPressed) {
                return true;
            }
            submitPressed = false;
        });

        // Frontend validation to message form
        function messageValidation() {
            var errors = false;
            var description = $.trim($(".msg-comment iframe").contents().find("body").text());
            var placeholder = $('#comment').attr('placeholder');

            // Check name and description are not empty
            if (!description || description == placeholder) {
                $('#comment_error').removeClass('hidden');
                errors = true;
            }
            return errors;
        };

        // Loading screen when submitting message
        $('#submit_message').on('click', function(evt) {
            evt.preventDefault();
            // Reset error popups
            $("p[id*='_error']").addClass('hidden');
            // Check errors
            var errors = messageValidation();
            var form = ('#issue_message_submit_form');
            var action = $(form).attr('action');

            CKEDITOR.instances.comment.updateElement();

            if (!errors) {
                loadingScreen();
                submitPressed = true;
                $('#issue_message_submit_form').submit();
            }
        });

        // Check filesize and restrict filesize to under 20 MB
        $('#attachment_ids').on('change', function() {
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
            $('#submit_message').prop('disabled', false);

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
                $(this).val('');
                $('#submit_message').prop('disabled', 'disabled');
                $('#attachment_info_div').removeClass('hidden alert-info').addClass('alert-danger');
            } else {
                $('#attachment_info_div').removeClass('hidden alert-danger').addClass('alert-info');
            }
            $('#attachment_info_div').html(elements);
        });

        // Update message thread
        function updateMessages() {
            var action = window.location.href + "/update_message";
            var timestamp = $('#timestamp');
            var data = {
                'timestamp': $(timestamp).val(),
                'csrf_token': core.csrf_token,
            };
            var msg = "";
            $.get(action, data, function (res) {
                if (res != "") {
                    var new_date = (new Date().getTime()/1000);
                    $(timestamp).val(new_date);
                    // Show the image right away since it's the first message
                    var cleaned = res.replace('data-src', 'src');
                    $('#issue_messages').prepend(cleaned);
                    msg = _t('New message arrived!');
                    toastr.info(msg);
                }      
            });
        }

        // Polling functionality for messages in issues
        setInterval(function () {
            updateMessages();
        }, $('#issue_messages').data('interval'));
    });
});
