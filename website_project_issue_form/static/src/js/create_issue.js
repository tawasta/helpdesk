odoo.define('website_project_issue_form.create_issue', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var toastr = require('website_utilities.notifications').toastr;
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
        summary.on("instanceReady", function(){
            this.document.on("keyup", function() {
                // Disable save button until there's some text
                var text = $.trim(this.getBody().getText());
                $('#submit_issue').prop('disabled', !text);
            });
            this.document.on("input", function() {
                // Disable save button until there's some text
                var text = $.trim(this.getBody().getText());
                $('#submit_issue').prop('disabled', !text);
            });
        });
        // Paste handler
        summary.on("paste", function(evt){
            var data = $.parseHTML(evt.data.dataValue);
            var text = $.trim($(data).text());
            $('#submit_issue').prop('disabled', !text);
        });
    });
});
