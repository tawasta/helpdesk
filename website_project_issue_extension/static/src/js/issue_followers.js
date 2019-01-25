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
            var newFollowersFormat = /^(([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\,?)+$/;

            if (newFollowers && !newFollowersFormat.test(newFollowers)) {
                // Strip spaces and check if the format matches to <email>(,<email>,...)
                $('#new_followers_error').removeClass('hidden');
                errors = true;
            }
            return errors;
        }

        // Add followers submit with ajax
        $('#add_followers').on('submit', function(evt) {
            evt.preventDefault();
            // Reset error popups
            $("p[id*='_error']").addClass('hidden');
            var errors = addFollowersValidation();
            var action = $(this).data('action');
            var newFollowers = $('#new_followers').val();
            var msg = _t('Added new followers to the issue');
            if (!errors) {
                loadingScreen();
                $('#add_followers_modal').modal('hide');
                $(this).find('input').val('');
                ajax.jsonRpc(action, 'call', {'followers': newFollowers}).then(function(res) {
                    var followersHtml = '';
                    var container = $('#issue_followers');
                    for (var i = 0; i < res.length; i++) {
                        followersHtml += '<div id="follower_' + res[i]['id'] + '" class="issue-follower mb8">' + res[i]['email'];
                        followersHtml += '<button class="btn btn-xs btn-danger pull-right delete-follower"';
                        followersHtml += 'data-follower="' + res[i]['id'] + '" data-toggle="modal"';
                        followersHtml += 'data-target="#delete_follower_modal" title="Delete follower">';
                        followersHtml += '<i class="fa fa-trash"/></button></div>';
                    }
                    container.append(followersHtml);
                    $.unblockUI();
                    toastr.info(msg);
                });
            }
        });

        // Pass follower id to delete form
        $(document).on('click', '.delete-follower', function() {
            var follower = $(this).attr('data-follower');
            $('.delete-follower-confirm').attr('data-follower', follower);
        });
        // Delete follower with ajax
        $(document).on('submit', '#delete_follower', function(evt) {
            evt.preventDefault();
            var follower = $('.delete-follower-confirm').attr('data-follower');
            var action = $(this).data('action');
            var msg = _t('Follower was removed successfully');
            loadingScreen();
            ajax.jsonRpc(action, 'call', {'follower_id': follower}).then(function(res) {
                $('#delete_follower_modal').modal('hide');
                if ('id' in res) {
                    $('#follower_' + follower).remove();
                    toastr.info(msg);
                }
                $.unblockUI();
            });
        });
    });
});
