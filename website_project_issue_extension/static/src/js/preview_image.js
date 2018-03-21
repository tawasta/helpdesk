odoo.define('website_project_issue_extension.preview_image', function (require) {
    "use strict";

    $(function() {
        
        var first = $('.message:first');
        if (first.find('.msg-img').length > 0) {

        }
        

        // Lazy load for images
        $(window).scroll( function(){
            $('.msg-img').each( function(i){
                var bottom_of_object = $(this).offset().top + $(this).outerHeight();
                var bottom_of_window = $(window).scrollTop() + $(window).height();

                // Show image
                if( bottom_of_window > bottom_of_object && $(this).attr('src') == undefined){
                    $(this).attr('src', $(this).attr('data-src'));
                }
            });
        });
    });
});
