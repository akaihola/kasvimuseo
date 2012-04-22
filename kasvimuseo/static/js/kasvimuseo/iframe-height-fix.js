$(window).load(function() {
    parent.postMessage(
        {plantedSpeciesIframeHeight: $('.ui-footer').position().top + 'px'},
        '*'
    );
});
