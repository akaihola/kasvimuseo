document.write('<iframe src="http://kasvit.ambitone.com/kasvimuseo/planted-species/" width="547px" height="10000px" scrolling="no" id="kasvit-iframe" style="border: none;"></iframe>');

(function() { 
    function getTop(elem) {
        var y = elem.offsetTop;
        while (elem = elem.offsetParent) y += elem.offsetTop;
        return y;
    }

    window.addEventListener(
        "message",
        function(e) {
            var iframe = document.getElementById("kasvit-iframe");
            iframe.style.height = e.data.plantedSpeciesIframeHeight;
            window.scrollTo(0, getTop(iframe));
        },
        false);
})();
