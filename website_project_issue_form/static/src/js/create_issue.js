odoo.define('website_project_issue_form.create_issue', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var loadingScreen = require('website_utilities.loader').loadingScreen;
    
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
        var summary = CKEDITOR.replace('issue_summary', config);

        // Frontend validation to issue form
        function issueValidation() {
            var errors = false;
            var name = $.trim($('#issue_name').val());
            var description = $.trim($(".issue-summary iframe").contents().find("body").text());
            var placeholder = $('#issue_summary').attr('placeholder');
            var email = $.trim($('#issue_email').val());
            // Parse whitespaces from recipients
            $('#issue_recipients').val($('#issue_recipients').val().replace(/\s/g, ''));
            var recipients = $('#issue_recipients').val();
            var recipientsFormat = /^(([\w\.-]+@[a-zA-Z_]+?\.[a-zA-Z]{2,3})\,?)+$/;

            // Check name and description are not empty
            if (!name) {
                $('#issue_name_error').removeClass('hidden');
                errors = true;
            }
            if (!email) {
                $('#issue_email_error').removeClass('hidden');
                errors = true;
            }
            if (!description || description == placeholder) {
                $('#issue_summary_error').removeClass('hidden');
                errors = true;
            }
            if (!recipientsFormat.test(recipients)) {
                // Strip spaces and check if the format matches to <email>(,<email>,...)
                $('#issue_recipients_error').removeClass('hidden');
                errors = true;
            }
            return errors;
        };

        // Loading screen when creating issue
        $('#submit_issue').on('click', function(evt) {
            evt.preventDefault();

            // Reset error popups
            $("p[id*='_error']").addClass('hidden');
            var errors = issueValidation();
            CKEDITOR.instances.issue_summary.updateElement();
            if (!errors) {
                loadingScreen();
                $('#issue_modal').modal('hide');
                $('#issue_form').submit();
            }
        });
    });
});
