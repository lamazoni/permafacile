var app = app || {};
(function($) {
	'use strict';
	app.AppLogView = Backbone.View.extend({
		el: $('body'),
		initialize : function () {
			_.bindAll(this,'render','renderWhenError');
			this.columns = [
				{
					name: "id",
					label: "id",
					editable: false,
        			cell: Backgrid.IntegerCell
				},
				{
		        	name: "when",
					label: "Quand",
					editable: false,
        			cell: Backgrid.DatetimeCell.extend({
      					includeTime: false
    				})
      			}, {
        			name: "who",
					label: "Qui",
					editable: false,
        			cell: "string"
      			},{
        			name: "where_slotdate",
					label: "Ou (date)",
					editable: false,
        			cell: Backgrid.DateCell
      			},{
        			name: "where_slotname",
					label: "Ou (type)",
					editable: false,
        			cell: "string"
      			},{
        			name: "what",
					label: "Action",
        			cell: "string"
      			}
			];
			var Log = Backbone.PageableCollection.extend({
        		url: URLSERVER+"/log/search",
        		mode: "client"
      		});
			this.log = new Log ()
			this.listenTo(this.log,'sync',this.render);
			this.listenTo(this.log,'request',this.renderLoading);
			this.listenTo(this.log,'error',this.renderWhenError);
			this.log.fetch();
			this.grid = new Backgrid.Grid({
        		columns: this.columns,
        		collection: this.log
      		});
      		this.paginator = new Backgrid.Extension.Paginator({
        		collection: this.log
      		});
		},
		render : function () {
			this.$(".container").empty();
			this.$(".container").append(this.grid.render().$el);
			this.$(".backgrid-paginator").append(this.paginator.render().$el);
		},
		renderWhenError: function() {
			this.$(".container").append("A error occured, cannot render.");
		},
		renderLoading: function() {
			console.log("AppView: renderLoading");
			this.$(".container").append('<br><div class="loading"></div>');
		},
	});
})(jQuery);
