document.write('<iframe src="http://kasvit.ambitone.com/kasvimuseo/planted-species/" width="547px" height="10000px" scrolling="no" id="kasvit-iframe" style="border: none;"></iframe>');

(function() { 
    var getTop = function(elem) {
        },
        resizeIframe = function(event) {
            var elem = document.getElementById("kasvit-iframe"),
                y = elem.offsetTop;
            elem.style.height = event.data.plantedSpeciesIframeHeight;
            while (elem = elem.offsetParent) y += elem.offsetTop;
            window.scrollTo(0, y);
        };
    
    if (window.addEventListener) window.addEventListener("message", resizeIframe, false);
    else window.attachEvent("message", resizeIframe);
})();
