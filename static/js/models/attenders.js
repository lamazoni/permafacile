var app = app || {};
/**
* @description : Represent a time slotView.
*
**/
(function() {
    'use strict';
	app.Attenders = Backbone.Model.extend({
		url: function() {
			return URLSERVER+"/attender/search"
		},
		defaults: {
            'listofname': [],
        },
		// localStorage: new Backbone.LocalStorage('agenda-slot'),
	});
})();
// let aAttenders = new app.Attenders();
