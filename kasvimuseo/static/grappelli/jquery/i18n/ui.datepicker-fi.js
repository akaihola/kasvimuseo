/* Finnish initialisation for the jQuery UI date picker plugin. */
/* Written by Harri Kilpiö (harrikilpio@gmail.com), from jQuery UI 1.10.3
   (ui/i18n/jquery.ui.datepicker-fi.js, MIT), taken 2026-08-03. */
/*
   Grappelli 2.5 -- upgrade plan Stage 3 -- added an unconditional

       <script src="{% static 'grappelli/jquery/i18n/ui.datepicker-'
                    |add:LANGUAGE_CODE|add:'.js' %}">

   to `admin/base.html`, and ships exactly two of those files: `de` and `fr`.
   LANGUAGE_CODE here is `fi`, so every admin page asked for a file nobody had
   and got a 404, with the date picker left in English on a Finnish-only
   application. This is that file. It is in `kasvimuseo/static/` rather than
   patched into the package because `kasvimuseo` precedes `grappelli` in
   INSTALLED_APPS, so the app-directories static finder hands this one back
   under grappelli's own name and nothing has to be vendored or overridden.

   Two deliberate differences from jQuery UI's original, both copied from
   grappelli's `ui.datepicker-de.js` rather than invented here:

   * the wrapper is `(function($){...})(grp.jQuery)`, because grappelli runs
     its jQuery in `grp.jQuery` and the page's global `jQuery` is Django's;
   * `dateFormat` is the ISO `yy-mm-dd` and not Finnish `dd.mm.yy`. It is what
     `DATE_FORMAT = 'Y-m-d'` in `common_settings.py` means, and grappelli
     overrides the picker's format per field from that setting anyway
     (`grappelli.getFormat('date')`), so a locale format here would only
     disagree with the value the field is given.
*/
(function($){
	$.datepicker.regional['fi'] = {
		closeText: 'Sulje',
		prevText: '&#xAB;Edellinen',
		nextText: 'Seuraava&#xBB;',
		currentText: 'Tänään',
		monthNames: ['Tammikuu','Helmikuu','Maaliskuu','Huhtikuu','Toukokuu','Kesäkuu',
		'Heinäkuu','Elokuu','Syyskuu','Lokakuu','Marraskuu','Joulukuu'],
		monthNamesShort: ['Tammi','Helmi','Maalis','Huhti','Touko','Kesä',
		'Heinä','Elo','Syys','Loka','Marras','Joulu'],
		dayNames: ['Sunnuntai','Maanantai','Tiistai','Keskiviikko','Torstai','Perjantai','Lauantai'],
		dayNamesShort: ['Su','Ma','Ti','Ke','To','Pe','La'],
		dayNamesMin: ['Su','Ma','Ti','Ke','To','Pe','La'],
		weekHeader: 'Vk',
		dateFormat: 'yy-mm-dd', firstDay: 1,
		isRTL: false,
		showMonthAfterYear: false,
		yearSuffix: ''};
	$.datepicker.setDefaults($.datepicker.regional['fi']);
})(grp.jQuery);
