if (document.location.search == '?debug=1') {
    document.write('<div id="planted-species-iframe-debug" style="position:absolute;width:233px;height:10em;overflow:scroll;margin-left:-233px;background:#cff;"></div>');
};
var plantedSpeciesScript = document.currentScript;
var plantedSpeciesFrame = document.createElement('iframe');
plantedSpeciesFrame.src = new URL('/kasvimuseo/planted-species/',
    plantedSpeciesScript.getAttribute('data-site-url') || window.location.origin).href;
plantedSpeciesFrame.width = '547px';
plantedSpeciesFrame.height = '10000px';
plantedSpeciesFrame.frameBorder = '0';
plantedSpeciesFrame.scrolling = 'no';
plantedSpeciesFrame.id = 'kasvit-iframe';
plantedSpeciesFrame.style.border = 'none';
plantedSpeciesScript.insertAdjacentElement('afterend', plantedSpeciesFrame);

(function() {
    var debug = document.getElementById("planted-species-iframe-debug"),
        resizeIframe = function(event) {
            var elem = document.getElementById("kasvit-iframe"),
                y = elem.offsetTop;
            if (debug) {
                debug.innerHTML +=
                    '<br>' +
                    event.data.plantedSpeciesIframePlantName +
                    '/' +
                    event.data.plantedSpeciesIframeHeight;
                debug.scrollTop = 10000;
            }
            elem.style.height = event.data.plantedSpeciesIframeHeight;
            while (elem = elem.offsetParent) y += elem.offsetTop;
            window.scrollTo(0, y);
        };
    
    if (window.addEventListener) window.addEventListener("message", resizeIframe, false);
    else window.attachEvent("message", resizeIframe);
})();
