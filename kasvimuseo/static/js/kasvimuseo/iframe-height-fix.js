$(window).on('pagechange', function(event, data) {
    var getHeight = function() {
            return Math.floor($('.ui-footer', data.toPage).position().top);
        },
        postHeight = function(height) {
            parent.postMessage(
                {plantedSpeciesIframeHeight: height + 'px',
                 plantedSpeciesIframePlantName: $('.finnish-name', data.toPage).text().trim()},
                '*'
            );
        },
        firstHeight = getHeight();
    postHeight(firstHeight);

    setTimeout(function() {
        var newHeight = getHeight();
        if (newHeight > firstHeight) postHeight(newHeight);
    }, 500);
});
