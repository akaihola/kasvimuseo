if (document.location.search == '?debug=1') {
    document.write('<div id="planted-species-iframe-debug" style="position:absolute;width:233px;height:10em;overflow:scroll;margin-left:-233px;background:#cff;"></div>');
};
document.write('<iframe src="//kasvit.ambitone.com/kasvimuseo/planted-species/" width="547px" height="10000px" frameborder="0" scrolling="no" id="kasvit-iframe" style="border: none;"></iframe>');

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
