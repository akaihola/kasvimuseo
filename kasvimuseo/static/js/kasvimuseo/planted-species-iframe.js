var plantedSpeciesScript = document.currentScript;
var plantedSpeciesSite = new URL(plantedSpeciesScript.src);
plantedSpeciesSite.hostname = plantedSpeciesSite.hostname.replace(/^static\./, '');
var plantedSpeciesFrame = document.createElement('iframe');
plantedSpeciesFrame.src = new URL('/kasvimuseo/planted-species/',
    plantedSpeciesSite.origin).href;
plantedSpeciesFrame.width = '547px';
plantedSpeciesFrame.height = '10000px';
plantedSpeciesFrame.frameBorder = '0';
plantedSpeciesFrame.scrolling = 'no';
plantedSpeciesFrame.id = 'kasvit-iframe';
plantedSpeciesFrame.style.border = 'none';
plantedSpeciesScript.insertAdjacentElement('afterend', plantedSpeciesFrame);

(function() {
    // Only the catalogue frame may resize itself, and only in whole pixels up
    // to maxHeight. Any other window can post to this page (task 23).
    var catalogueOrigin = plantedSpeciesSite.origin,
        maxHeight = 100000,
        debug = null,
        resizeIframe = function(event) {
            var elem = plantedSpeciesFrame,
                y = elem.offsetTop,
                height,
                line;
            if (event.origin !== catalogueOrigin ||
                    event.source !== plantedSpeciesFrame.contentWindow ||
                    !event.data) return;
            height = event.data.plantedSpeciesIframeHeight;
            if (typeof height !== 'string' || !/^\d+px$/.test(height) ||
                    parseInt(height, 10) > maxHeight) return;
            if (debug) {
                line = document.createElement('div');
                line.textContent =
                    event.data.plantedSpeciesIframePlantName + '/' + height;
                debug.appendChild(line);
                debug.scrollTop = 10000;
            }
            elem.style.height = height;
            while (elem = elem.offsetParent) y += elem.offsetTop;
            window.scrollTo(0, y);
        };

    if (document.location.search == '?debug=1') {
        debug = document.createElement('div');
        debug.id = 'planted-species-iframe-debug';
        debug.style.cssText = 'position:absolute;width:233px;height:10em;overflow:scroll;margin-left:-233px;background:#cff;';
        plantedSpeciesFrame.insertAdjacentElement('afterend', debug);
    }
    window.addEventListener('message', resizeIframe, false);
})();
