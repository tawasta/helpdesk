odoo.define('website_project_issue_extension.preview_image', function (require) {
    "use strict";

    $(function() {
        
        function firstMessage() {

            var first = $('.message:first');
            var img = $(first).find('.msg-img');

            if (img.length > 0) {
                $(img).attr('src', $(img).attr('data-src'));
            }
        }
        firstMessage();
        

        // Lazy load for images
        $(window).scroll(function() {
            $('.msg-img').each(function(i) {
                var bottom_of_object = $(this).offset().top + $(this).outerHeight();
                var bottom_of_window = $(window).scrollTop() + $(window).height();

                // Show image
                if (bottom_of_window > bottom_of_object && $(this).attr('src') == undefined) {
                    $(this).attr('src', $(this).attr('data-src'));
                }
            });
        });
    });
});
