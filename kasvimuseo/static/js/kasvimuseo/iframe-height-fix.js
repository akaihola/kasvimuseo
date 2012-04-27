$(window).on('pagechange', function(event, data) {
    parent.postMessage(
        {plantedSpeciesIframeHeight: Math.floor($('.ui-footer', data.toPage).position().top) + 'px',
         plantedSpeciesIframePlantName: $('.finnish-name', data.toPage).text().trim()},
        '*'
    );
});
