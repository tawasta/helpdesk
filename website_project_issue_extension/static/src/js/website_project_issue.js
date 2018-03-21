odoo.define('website_project_issue_extension.issue', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var ajax = require('web.ajax');
    var loadingScreen = require('website_utilities.loader').loadingScreen;
    var toastr = require('website_utilities.notifications').toastr;
    
    $(function () {

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
            if (text && text != placeholder) {
                return true;
            }
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
            var attachment = $('#message_attachment').prop('files')[0];

            CKEDITOR.instances.comment.updateElement();

            // Prepare form inputs
            var form_fields = {};
            form_fields = $(form).serializeArray();
            form_fields.push({name: 'attachment', value: attachment});
            form_fields.push({name: 'csrf_token', value: core.csrf_token})
            
            var form_values = {};
            _.each(form_fields, function(input) {
                if (input.value != '' && input.value !== undefined) {
                    form_values[input.name] = input.value;
                }
            });

            if (!errors) {
                loadingScreen();

                ajax.post(action, form_values).then(function(res) {
                    var results = JSON.parse(res);
                    if (results['error']) {
                        toastr.error(results['error']);
                    } else {
                        // Update message thread
                        updateMessages();

                        // Reset data
                        $(form).find('input,textarea,select').val('').end();
                        CKEDITOR.instances.comment.setData('');
                    }
                    $.unblockUI();
                });
            }
        });

        // Check filesize and restrict filesize to under 20 MB
        $('#message_attachment').on('change', function() {

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
                $('#message_attachment').val('');
                $('#fileTooBigDiv').removeClass('hidden');
                $('#fileTooBig').text(size);
            } else {
                $('#fileSizeOkDiv').removeClass('hidden');
                $('#fileSizeOk').text(size);
            }
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
                    $('#issue_messages').prepend(res);
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
