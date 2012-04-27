if (document.location.getParameter('debug')) {
    document.write('<div id="planted-species-iframe-debug" style="height:3em;overflow:scroll;">debug</div>');
};
document.write('<iframe src="http://kasvit.ambitone.com/kasvimuseo/planted-species/" width="547px" height="10000px" frameborder="0" scrolling="no" id="kasvit-iframe" style="border: none;"></iframe>');

(function() { 
    var debug = document.getElementById("planted-species-iframe-debug"),
        resizeIframe = function(event) {
            var elem = document.getElementById("kasvit-iframe"),
                y = elem.offsetTop;
            if (debug) {
                debug.innerHTML += '<br>' + event.data.plantedSpeciesIframePlantName;
            }
            elem.style.height = event.data.plantedSpeciesIframeHeight;
            while (elem = elem.offsetParent) y += elem.offsetTop;
            window.scrollTo(0, y);
        };
    
    if (window.addEventListener) window.addEventListener("message", resizeIframe, false);
    else window.attachEvent("message", resizeIframe);
})();
