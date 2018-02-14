var app = app || {};
/**
* @description : Represent a time slotView.
*
**/
(function() {
    'use strict';
	app.Slot = Backbone.Model.extend({
		url: function() {
			// return URLSERVER+"/slot/"+this.get('searchid');
			return URLSERVER+"/slot/"+this.get('id');
		},
		idAttribute: "id",
		opacity : false,
		tmpattenders : null,
		defaults: {
			// 'searchid' : "61",
            'date': null,
			'attenders': null,
			'lock': false,
			'lockCancelAttender': false,
			// 'opacity': false,
        },
		// localStorage: new Backbone.LocalStorage('agenda-slot'),
	});
})();
