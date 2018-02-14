var app = app || {};
/**
* @description : Represent a time slotView.
*
**/
(function() {
	'use strict';

	app.Slots = Backbone.PageableCollection.extend({
		model : app.Slot,
	    url: function() {
			return URLSERVER+"/slot/search";
		},
		mode: "client",
		state : {
			// indice 1 based indice
			firstPage: 1,
			// currentPage: 3,
		},
	});

})();
