var app = app || {};
(function($) {
	'use strict';
	app.AppSummaryView = Backbone.View.extend({
		el: $('body'),
		initialize : function () {
			_.bindAll(this,'render','renderWhenError');
			this.columns = [
				// {
        		// name: "id",
        		// editable: false,
        		// cell: Backgrid.IntegerCell.extend({
          // 			orderSeparator: ''
        		// })
      	// 		},
				{
		        	name: "name",
					label: "nom",
        			cell: "string"
      			}, {
        			name: "participationDone",
					label: "effectue",
        			cell: "integer"
      			},{
        			name: "participationPlaned",
					label: "prevue",
        			cell: "integer"
      			},
				// , {
        		// 	name: "Inscription",
        		// 	cell: "integer"
      	// 		}, {
				// 	name: "Restant",
        		// 	cell: "integer"
      	// 		}
			];
			var Summary = Backbone.PageableCollection.extend({
        		url: URLSERVER+"/summary/search",
        		mode: "client"
      		});
			this.summary = new Summary ()
			this.listenTo(this.summary,'sync',this.render);
			this.listenTo(this.summary,'request',this.renderLoading);
			this.listenTo(this.summary,'error',this.renderWhenError);
			this.summary.fetch();
			this.grid = new Backgrid.Grid({
        		columns: this.columns,
        		collection: this.summary
      		});
      		this.paginator = new Backgrid.Extension.Paginator({
        		collection: this.summary
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
