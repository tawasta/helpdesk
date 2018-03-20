odoo.define('website_project_issue_form.create_issue', function (require) {
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
        var summary = CKEDITOR.replace('issue_summary', config);

        // Frontend validation to issue form
        function issueValidation() {
            var errors = false;
            var name = $.trim($('#issue_name').val());
            var description = $.trim($(".issue-summary iframe").contents().find("body").text());
            var placeholder = $('#issue_summary').attr('placeholder');

            // Check name and description are not empty
            if (!name) {
                $('#issue_name_error').removeClass('hidden');
                errors = true;
            }
            if (!description || description == placeholder) {
                $('#issue_summary_error').removeClass('hidden');
                errors = true;
            }
            return errors;
        };

        // Loading screen when creating issue
        $('#submit_issue').on('click', function(evt) {
            evt.preventDefault();
            // Reset error popups
            $("p[id*='_error']").addClass('hidden');
            // Check errors
            var errors = issueValidation();
            var form = ('#issue_form');
            var action = $(form).attr('action');
            var text_data = $(form).serializeArray();
            var attachment = $('#issue_attachment').prop('files')[0];
            console.log(attachment);
            CKEDITOR.instances.issue_summary.updateElement();

            // var form_data = {
            //     'data': $(form).serializeArray()
            // };
            // console.log(form_data);

            var form_data = new FormData();
            form_data.append('attachment', attachment);
            $.each(text_data,function(key,input){
                form_data.append(input.name,input.value);
            });
            console.log(form_data);
            // return false;
            if (!errors) {
                $('#issue_modal').modal('hide');
                loadingScreen();

                $.ajax({
                    type: "POST",
                    url: action,
                    data: form_data,
                    contentType: false,
                    processData: false,
                    success: function (values) {
                        console.log(values);
                    }
                });

                // ajax.jsonRpc(action, "call", form_data).then(function(res) {
                //     var results = JSON.parse(res);
                //     if (results['error']) {
                //         toastr.error(results['error']);
                //     } else {
                //         // Add a new row to table, if table exists
                //         $('.panel > .alert').addClass('hidden');
                //         $('.panel > table').removeClass('hidden');
                //         var row = "<tr><td><a href='/my/issues/" + results["id"] + _t("'>Issue ") + results["id"] + "</a></td>";
                //         row += "<td><span>" + results["name"] + "</span></td>";
                //         row += "<td><span class='label label-info' ";
                //         row += "title='" + _t("Current stage of the issue") + "'>" + results["stage"] + "</span></td></tr>";
                //         $(row).prependTo("table");
                //         toastr.info(results['msg']);
            
                //         // Reset data
                //         $('#issue_modal').find('input,textarea,select').val('').end();
                //         CKEDITOR.instances.issue_summary.setData('');
                //     }
                //     $.unblockUI();
                // });
            }
        });
    });
});
