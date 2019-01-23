odoo.define('website_project_issue_extension.issue_followers', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var ajax = require('web.ajax');
    var loadingScreen = require('website_utilities.loader').loadingScreen;
    var toastr = require('website_utilities.notifications').toastr;

    $(function() {
        function addFollowersValidation() {
            var errors = false;
            // Parse whitespaces from recipients
            $('#new_followers').val($('#new_followers').val().replace(/\s/g, ''));
            var newFollowers = $('#new_followers').val();
            var newFollowersFormat = /^(([\w\.-]+@[a-zA-Z_]+?\.[a-zA-Z]{2,3})\,?)+$/;

            if (!newFollowersFormat.test(recipients)) {
                // Strip spaces and check if the format matches to <email>(,<email>,...)
                $('#new_followers_error').removeClass('hidden');
                errors = true;
            }
            return errors;
        }

        // Add followers submit with AJAX
        $('#add_followers').on('submit', function(evt) {
            evt.preventDefault();
            // Reset error popups
            $("p[id*='_error']").addClass('hidden');
            var errors = addFollowersValidation();
            var action = $(this).data('action');
            var newFollowers = $('#new_followers').val();
            if (!errors) {
                // TODO: implement add followers submission
                // loadingScreen();
                // $('#add_followers_modal').modal('hide');
                // ajax.jsonRpc(action, 'call', {'followers': newFollowers}).then(function(res) {

                // });
            }
        });
    });
});
